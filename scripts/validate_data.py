"""Validate the project's public JSON contracts before rendering."""
from datetime import date, datetime
from pathlib import Path
import re
from urllib.parse import urlsplit

if __package__:
    from .validation import local_file, read_json, require
    from .update_youtube import CHANNEL_ID
    from .update_instagram import TARGET
else:
    from validation import local_file, read_json, require
    from update_youtube import CHANNEL_ID
    from update_instagram import TARGET

ROOT = Path(__file__).resolve().parents[1]


def obj(value, location):
    require(isinstance(value, dict), location, 'expected an object')
    return value


def text(value, location, empty=False):
    require(isinstance(value, str) and (empty or bool(value.strip())), location, 'expected a string' + ('' if empty else ' with content'))
    return value


def iso_date(value, location):
    text(value, location)
    require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value)), location, 'expected YYYY-MM-DD')
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f'{location}: invalid calendar date') from None


def timestamp(value, location):
    text(value, location)
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(parsed.utcoffset() is not None, location, 'timestamp must include timezone')
        return parsed
    except ValueError:
        raise ValueError(f'{location}: expected an ISO timestamp with timezone') from None


def https_url(value, location, hosts=None):
    text(value, location)
    try:
        parsed = urlsplit(value)
        valid = parsed.scheme == 'https' and bool(parsed.hostname) and not parsed.username and not parsed.password and parsed.port in (None, 443)
        require(valid and (hosts is None or parsed.hostname in hosts), location, 'invalid HTTPS URL or host')
        return parsed
    except ValueError:
        raise ValueError(f'{location}: invalid HTTPS URL or host') from None


def entries(value, key, location, count=None):
    rows = obj(value, location).get(key)
    require(isinstance(rows, list), f'{location}.{key}', 'expected an array')
    if count is not None:
        require(len(rows) == count, f'{location}.{key}', f'expected {count} entries')
    return rows


def unique_id(value, seen, location, pattern):
    require(isinstance(value, str) and bool(re.fullmatch(pattern, value)), location, 'invalid ID')
    require(value not in seen, location, 'duplicate ID')
    seen.add(value)


def validate_metadata(snapshot, location, source):
    if 'metadata' not in snapshot:
        return  # Legacy snapshots remain readable; absence means unknown provenance.
    metadata = obj(snapshot['metadata'], location + '.metadata')
    require(set(metadata) == {'source', 'fetched_at'}, location + '.metadata', 'expected source and fetched_at only')
    if metadata['source'] == 'legacy-cache':
        require(metadata['fetched_at'] is None, location + '.metadata.fetched_at', 'legacy acquisition time must remain unknown')
    else:
        require(metadata['source'] == source, location + '.metadata.source', 'unexpected provider')
        timestamp(metadata['fetched_at'], location + '.metadata.fetched_at')


def validate_data(root=ROOT, *, competitions=None):
    root = Path(root)
    snapshots = {name: read_json(root / 'data' / name) for name in (
        'competitions.json', 'competition-participation.json', 'competition-logos.json', 'youtube.json', 'instagram.json')}
    if competitions is not None:
        snapshots['competitions.json'] = competitions
    competitions = snapshots['competitions.json']
    rows = entries(competitions, 'events', 'data/competitions.json')
    iso_date(competitions.get('checked_at'), 'data/competitions.json.checked_at')
    event_ids = set()
    for index, row in enumerate(rows):
        loc = f'data/competitions.json.events[{index}]'
        obj(row, loc)
        require(type(row.get('id')) is int and row['id'] > 0, loc + '.id', 'expected a positive integer')
        unique_id(str(row['id']), event_ids, loc + '.id', r'[0-9]+')
        text(row.get('name'), loc + '.name')
        start = iso_date(row.get('start'), loc + '.start')
        end = iso_date(row.get('end'), loc + '.end')
        require(end >= start, loc + '.end', 'precedes start')
        for field in ('city', 'country', 'description'):
            text(row.get(field, ''), loc + '.' + field, empty=True)
        url = https_url(row.get('url'), loc + '.url', {'www.ifbbpro.com'})
        require(url.path.startswith('/competition/') and not url.query and not url.fragment, loc + '.url', 'expected a competition source URL')
        if row.get('image_url'):
            https_url(row['image_url'], loc + '.image_url')
    if 'metadata' in competitions:
        loc = 'data/competitions.json.metadata'
        metadata = obj(competitions['metadata'], loc)
        require(set(metadata) == {'source', 'fetched_at', 'query_start', 'query_end', 'fetched_total', 'retained_missing_ids'}, loc, 'unexpected metadata fields')
        require(metadata['source'] == 'https://www.ifbbpro.com/wp-json/tribe/events/v1/events', loc + '.source', 'unexpected IFBB endpoint')
        fetched_at = timestamp(metadata['fetched_at'], loc + '.fetched_at')
        require(fetched_at.date().isoformat() == competitions['checked_at'], loc, 'checked_at differs from fetched_at')
        start = iso_date(metadata['query_start'], loc + '.query_start')
        end = iso_date(metadata['query_end'], loc + '.query_end')
        require(start <= end, loc, 'invalid query range')
        require(type(metadata['fetched_total']) is int and metadata['fetched_total'] > 0, loc + '.fetched_total', 'expected positive count')
        retained = metadata['retained_missing_ids']
        require(isinstance(retained, list) and all(type(key) is int and str(key) in event_ids for key in retained), loc + '.retained_missing_ids', 'expected known integer event IDs')
        require(len(retained) == len(set(retained)), loc + '.retained_missing_ids', 'duplicate ID')
    for name in ('competition-participation.json', 'competition-logos.json'):
        mapping = obj(snapshots[name], 'data/' + name)
        for key, value in mapping.items():
            loc = f'data/{name}.{key}'
            require(key in event_ids, loc, 'orphan event ID')
            if name == 'competition-participation.json':
                obj(value, loc)
                require(value.get('status') in ('pending', 'confirmed', 'absent'), loc + '.status', 'invalid participation status')
                if 'name' in value:
                    text(value['name'], loc + '.name')
            else:
                text(value, loc)
                require(value.startswith('img/calendar/') and '..' not in value, loc, 'expected an img/calendar/ path')
                require(not urlsplit(value).query and not urlsplit(value).fragment, loc, 'logo path must not contain query or fragment')
                local_file(root, value, 'index.html', loc)
    videos = snapshots['youtube.json']
    rows = entries(videos, 'videos', 'data/youtube.json', 6)
    require(set(videos) <= {'channelId', 'videos', 'metadata'}, 'data/youtube.json', 'unexpected public field')
    require(videos.get('channelId') == CHANNEL_ID, 'data/youtube.json.channelId', 'unexpected channel')
    validate_metadata(videos, 'data/youtube.json', 'youtube-data-api')
    seen = set()
    for index, row in enumerate(rows):
        loc = f'data/youtube.json.videos[{index}]'
        obj(row, loc)
        require(set(row) <= {'id', 'title', 'publishedAt'}, loc, 'unexpected public field')
        unique_id(row.get('id'), seen, loc + '.id', r'[A-Za-z0-9_-]{11}')
        text(row.get('title'), loc + '.title')
        timestamp(row.get('publishedAt'), loc + '.publishedAt')
    instagram = snapshots['instagram.json']
    rows = entries(instagram, 'posts', 'data/instagram.json', 3)
    require(set(instagram) <= {'username', 'posts', 'metadata'}, 'data/instagram.json', 'unexpected public field')
    require(instagram.get('username') == TARGET, 'data/instagram.json.username', 'unexpected profile')
    validate_metadata(instagram, 'data/instagram.json', 'meta-business-discovery')
    seen = set()
    for index, row in enumerate(rows):
        loc = f'data/instagram.json.posts[{index}]'
        obj(row, loc)
        require(set(row) <= {'id', 'permalink', 'media_type', 'timestamp', 'media_url', 'thumbnail_url'}, loc, 'unexpected public field')
        unique_id(row.get('id'), seen, loc + '.id', r'[0-9]+')
        require(row.get('media_type') in ('IMAGE', 'VIDEO', 'CAROUSEL_ALBUM'), loc + '.media_type', 'invalid media type')
        timestamp(row.get('timestamp'), loc + '.timestamp')
        url = https_url(row.get('permalink'), loc + '.permalink', {'www.instagram.com'})
        require(bool(re.fullmatch(r'/(?:p|reel)/[A-Za-z0-9_-]+/', url.path)) and not url.query and not url.fragment, loc + '.permalink', 'invalid post URL')
        for field in ('media_url', 'thumbnail_url'):
            if field in row:
                url = https_url(row[field], loc + '.' + field)
                require(any(url.hostname == host or url.hostname.endswith('.' + host) for host in ('cdninstagram.com', 'fbcdn.net')), loc + '.' + field, 'unexpected preview host')
    return snapshots


if __name__ == '__main__':
    validate_data()
    print('Data contracts valid.')
