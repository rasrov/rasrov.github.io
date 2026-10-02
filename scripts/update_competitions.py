"""Refresh the IFBB snapshot; preserve editorial decisions and missing historical events."""

import argparse
from datetime import date, datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

if __package__:
    from .snapshot_write import write_outputs
    from .validate_data import validate_data
else:
    from snapshot_write import write_outputs
    from validate_data import validate_data

ROOT = Path(__file__).resolve().parents[1]
API = 'https://www.ifbbpro.com/wp-json/tribe/events/v1/events'
START = date(2026, 1, 1)
PAGE_SIZE = 50
MAX_PAGES = 200


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'p', 'div', 'li'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('p', 'div', 'li'):
            self.parts.append('\n')

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(value):
    if not isinstance(value, str):
        raise ValueError('Expected IFBB text field')
    parser = PlainText()
    parser.feed(value)
    parser.close()
    return '\n'.join(
        line for part in ''.join(parser.parts).splitlines() if (line := ' '.join(part.split()))
    )


def scope_end(today):
    # Initial horizon stays at 2027; roll forward on October 1, never backwards.
    year = max(2027, today.year + (today >= date(today.year, 10, 1)))
    return date(year, 10, 1)


def request_json(url):
    for attempt in range(3):
        try:
            request = Request(
                url, headers={'User-Agent': 'KimAngelWebsite/1.0', 'Accept': 'application/json'}
            )
            with urlopen(request, timeout=30) as response:
                raw = response.read(10_000_001)
            if len(raw) > 10_000_000:
                raise ValueError('IFBB response too large')
            return json.loads(raw)
        except HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise RuntimeError(f'IFBB HTTP {error.code}') from None
            if attempt == 2:
                raise RuntimeError(f'IFBB HTTP {error.code} after retries') from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError('IFBB unavailable after retries') from None
        time.sleep(2 ** (attempt + 1))


def normalize_event(row):
    if not isinstance(row, dict) or type(row.get('id')) is not int or row['id'] <= 0:
        raise ValueError('Invalid IFBB event ID')
    categories = row.get('categories')
    if not isinstance(categories, list) or any(
        not isinstance(c, dict) or not isinstance(c.get('slug'), str) for c in categories
    ):
        raise ValueError('Invalid IFBB categories')
    if not any(c['slug'] == 'professional' for c in categories):
        return None
    description = plain_text(row.get('description'))
    if not re.search(r'\bclassic\s+physique\b', description, re.I):
        return None
    venue = row.get('venue')
    if venue in (None, False, []):
        venue = {}
    if not isinstance(venue, dict):
        raise ValueError('Invalid IFBB venue')
    image = row.get('image')
    if image in (None, False):
        image = {}
    if not isinstance(image, dict):
        raise ValueError('Invalid IFBB image')
    # Use local event dates, not UTC conversions that can shift the calendar day.
    dates = []
    for field in ('start_date', 'end_date'):
        value = row.get(field)
        if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', value
        ):
            raise ValueError('Invalid IFBB event date')
        dates.append(datetime.strptime(value, '%Y-%m-%d %H:%M:%S').date().isoformat())
    return {
        'id': row['id'],
        'name': plain_text(row.get('title')),
        'start': dates[0],
        'end': dates[1],
        'city': plain_text(venue.get('city', '')),
        'country': plain_text(venue.get('country', '')),
        'url': row.get('url'),
        'description': description,
        'image_url': image.get('url', ''),
    }


def fetch_events(end, fetch=request_json):
    rows, seen, totals = [], set(), None
    for page in range(1, MAX_PAGES + 1):
        url = (
            API
            + '?'
            + urlencode(
                {
                    'start_date': START.isoformat(),
                    'end_date': end.isoformat(),
                    'per_page': PAGE_SIZE,
                    'page': page,
                }
            )
        )
        payload = fetch(url)
        if not isinstance(payload, dict):
            raise ValueError('Invalid IFBB response')
        total, pages = payload.get('total'), payload.get('total_pages')
        if (
            type(total) is not int
            or total <= 0
            or type(pages) is not int
            or not 1 <= pages <= MAX_PAGES
        ):
            raise ValueError('Empty or invalid IFBB pagination; snapshot preserved')
        if pages != (total + PAGE_SIZE - 1) // PAGE_SIZE:
            raise ValueError('Inconsistent IFBB page count')
        if totals is None:
            totals = (total, pages)
        elif totals != (total, pages):
            raise ValueError('IFBB results changed during pagination; retry later')
        batch = payload.get('events')
        expected = min(PAGE_SIZE, total - (page - 1) * PAGE_SIZE)
        if not isinstance(batch, list) or len(batch) != expected:
            raise ValueError('Incomplete IFBB page; snapshot preserved')
        for row in batch:
            event = normalize_event(row)
            key = row['id']
            if key in seen:
                raise ValueError('Duplicate IFBB ID across pages')
            seen.add(key)
            if event:
                if event['end'] < START.isoformat() or event['start'] > end.isoformat():
                    raise ValueError('IFBB event outside requested scope')
                rows.append(event)
        if page == pages:
            break
    if not rows:
        raise ValueError('No professional Classic Physique events; snapshot preserved')
    return rows, totals[0]


def refresh(root=ROOT, now=None, fetch=request_json, dry_run=False):
    root = Path(root)
    now = now or datetime.now(timezone.utc)
    if now.utcoffset() is None:
        raise ValueError('Refresh time must include timezone')
    now = now.astimezone(timezone.utc)
    existing = validate_data(root)['competitions.json']
    end = scope_end(now.date())
    events, fetched_count = fetch_events(end, fetch)
    previous = {row['id']: row for row in existing['events']}
    incoming = {row['id']: row for row in events}
    retained = sorted(previous.keys() - incoming.keys())
    merged = previous | incoming
    report = {
        'added': len(incoming.keys() - previous.keys()),
        'updated': sum(previous[key] != incoming[key] for key in previous.keys() & incoming.keys()),
        'retained_missing_ids': retained,
    }
    snapshot = {
        'checked_at': now.date().isoformat(),
        'metadata': {
            'source': API,
            'fetched_at': now.isoformat().replace('+00:00', 'Z'),
            'query_start': START.isoformat(),
            'query_end': end.isoformat(),
            'fetched_total': fetched_count,
            'retained_missing_ids': retained,
        },
        'events': sorted(merged.values(), key=lambda row: (row['start'], row['id'])),
    }
    validate_data(root, competitions=snapshot)
    if not dry_run:
        write_outputs(
            root,
            {'data/competitions.json': json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n'},
        )
    return snapshot, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--dry-run', action='store_true', help='Fetch and validate without writing files'
    )
    args = parser.parse_args()
    snapshot, report = refresh(dry_run=args.dry_run)
    if report['retained_missing_ids']:
        print(
            f'Warning: {len(report["retained_missing_ids"])} previous events absent from the eligible response were retained for review.'
        )
    print(
        json.dumps(
            {
                'dry_run': args.dry_run,
                'scope_end': snapshot['metadata']['query_end'],
                'events': len(snapshot['events']),
                **report,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError) as error:
        print(f'IFBB update failed: {error}', file=sys.stderr)
        sys.exit(1)
