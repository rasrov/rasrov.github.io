"""Render three public Instagram posts via Facebook Business Discovery."""

import argparse
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

if __package__:
    from .generated_regions import replace_region
    from .snapshot_write import RecoveryRequiredError, write_outputs
else:
    from generated_regions import replace_region
    from snapshot_write import RecoveryRequiredError, write_outputs

ROOT = Path(__file__).resolve().parents[1]
OWN_IG_ID = '17841401870042081'
TARGET = 'kim_angel'
VERSION = 'v26.0'
START = '<!-- instagram:generated:start -->'
END = '<!-- instagram:generated:end -->'


def parse_date(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('Timestamp without timezone')
    return date


def preview_url(item):
    value = item.get('thumbnail_url' if item.get('media_type') == 'VIDEO' else 'media_url', '')
    url = urlparse(value)
    host = url.hostname or ''
    if (
        url.scheme == 'https'
        and not url.username
        and not url.password
        and url.port in (None, 443)
        and any(
            host == domain or host.endswith('.' + domain)
            for domain in ('cdninstagram.com', 'fbcdn.net')
        )
    ):
        return value
    return ''


def select_posts(items, now=None):
    now = now or datetime.now(timezone.utc)
    unique = {}
    for item in items:
        if item.get('media_type') not in ('IMAGE', 'VIDEO', 'CAROUSEL_ALBUM'):
            continue
        post_id = str(item.get('id', ''))
        if not post_id.isdigit():
            raise ValueError('Invalid media ID')
        link = urlparse(item.get('permalink', ''))
        if (
            link.scheme != 'https'
            or link.netloc != 'www.instagram.com'
            or not re.fullmatch(r'/(?:p|reel)/[A-Za-z0-9_-]+/', link.path)
            or link.query
            or link.fragment
        ):
            raise ValueError('Unexpected Instagram permalink')
        date = parse_date(item['timestamp'])
        if date > now:
            continue
        unique[post_id] = {key: item[key] for key in ('id', 'permalink', 'media_type', 'timestamp')}
        preview = preview_url(item)
        if preview:
            key = 'thumbnail_url' if item['media_type'] == 'VIDEO' else 'media_url'
            unique[post_id][key] = preview
    selected = sorted(
        unique.values(), key=lambda p: (parse_date(p['timestamp']), str(p['id'])), reverse=True
    )[:3]
    if len(selected) != 3:
        raise ValueError('Fewer than three valid posts; published site will not be replaced')
    return selected


def fetch_posts(token):
    # Read a larger recent batch and sort by timestamp rather than visual pinning.
    fields = (
        'business_discovery.username('
        + TARGET
        + '){username,media.limit(50){id,permalink,media_type,media_url,thumbnail_url,timestamp}}'
    )
    url = f'https://graph.facebook.com/{VERSION}/{OWN_IG_ID}?' + urlencode({'fields': fields})
    request = Request(url, headers={'Authorization': 'Bearer ' + token})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                data = json.load(response)
            if 'error' in data:
                raise RuntimeError('Meta rejected the request; check token and permissions')
            profile = data['business_discovery']
            if profile.get('username') != TARGET:
                raise ValueError('Unexpected Instagram profile')
            return select_posts(profile['media']['data'])
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                # Response body and request headers may contain sensitive data.
                raise RuntimeError(
                    f'Meta HTTP {error.code}; check token expiry and permissions'
                ) from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError('Meta unavailable after three attempts') from None
        time.sleep(2**attempt)


def replace_posts(page, posts, now=None):
    posts = select_posts(posts, now=now)
    cards = []
    for post in posts:
        link = html.escape(post['permalink'], quote=True)
        preview = html.escape(preview_url(post), quote=True)
        kind = {'VIDEO': 'Reel', 'CAROUSEL_ALBUM': 'Carrusel', 'IMAGE': 'Foto'}[post['media_type']]
        icon = (
            '<path d="m9 5 11 7-11 7Z"/>'
            if kind == 'Reel'
            else '<rect x="7" y="7" width="13" height="13" rx="2"/><path d="M16 7V4H4v12h3"/>'
            if kind == 'Carrusel'
            else '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="m3 16 6-6 12 10"/>'
        )
        label = f'{kind} de @kim_angel del {parse_date(post["timestamp"]).strftime("%d/%m/%Y")}. Abrir en Instagram (nueva pestaña)'
        picture = (
            f'<img class="social-image" src="{preview}" alt="" width="800" height="1000" loading="lazy" decoding="async">'
            if preview
            else ''
        )
        cards.append(
            '\n                    <article class="social-post">\n'
            f'                        <a class="social-card" href="{link}" target="_blank" rel="noopener noreferrer" aria-label="{label}">\n'
            '                            <span class="social-fallback" aria-hidden="true">@kim_angel<span>Ver publicación en Instagram ↗</span></span>\n'
            f'                            {picture}\n'
            f'                            <span class="social-kind" title="{kind}" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">{icon}</svg></span>\n'
            '                            <span class="social-open" aria-hidden="true">Ver en Instagram ↗</span>\n'
            '                        </a>\n'
            '                    </article>'
        )
    return replace_region(page, 'instagram', ''.join(cards) + '\n                ')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-cache', action='store_true')
    args = parser.parse_args()
    cache = ROOT / 'data/instagram.json'
    if args.from_cache:
        posts = select_posts(json.loads(cache.read_text(encoding='utf-8'))['posts'])
    else:
        token = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '').strip()
        if not token:
            raise ValueError(
                'Add INSTAGRAM_ACCESS_TOKEN to GitHub Actions secrets; see docs/instagram.md'
            )
        posts = fetch_posts(token)
        fetched_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    index = ROOT / 'index.html'
    result = replace_posts(index.read_text(encoding='utf-8'), posts)
    outputs = {}
    if not args.from_cache:
        snapshot = {
            'username': TARGET,
            'posts': posts,
            'metadata': {'source': 'meta-business-discovery', 'fetched_at': fetched_at},
        }
        outputs['data/instagram.json'] = json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n'
    outputs['index.html'] = result
    write_outputs(ROOT, outputs)
    source = 'local cache (no Meta request)' if args.from_cache else 'Meta Business Discovery'
    print(f'Instagram source: {source}')
    for post in posts:
        print(
            f'Selected post {post["id"]} | {post["timestamp"]} | {post["media_type"]} | preview={bool(preview_url(post))}'
        )
    print(
        'Rendered cached posts; snapshot bytes and provenance unchanged.'
        if args.from_cache
        else 'Updated Instagram snapshot and HTML. Actions deploys these files without committing them.'
    )


if __name__ == '__main__':
    try:
        main()
    except RecoveryRequiredError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, RuntimeError, OSError):
        # Avoid echoing provider payloads or credentials on unexpected errors.
        print(
            'Instagram update failed. Check INSTAGRAM_ACCESS_TOKEN, its expiry and permissions; published site unchanged.',
            file=sys.stderr,
        )
        sys.exit(1)
