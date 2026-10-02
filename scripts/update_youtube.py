"""Refresh public uploads and render six cards. Standard library only."""

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
from urllib.parse import urlencode
from urllib.request import Request, urlopen

if __package__:
    from .generated_regions import replace_region
    from .snapshot_write import RecoveryRequiredError, write_outputs
else:
    from generated_regions import replace_region
    from snapshot_write import RecoveryRequiredError, write_outputs

ROOT = Path(__file__).resolve().parents[1]
CHANNEL_ID = 'UCEqAjtwYKSwKDN4BENhvc6A'
COUNT = 6
START = '<!-- youtube:generated:start -->'
END = '<!-- youtube:generated:end -->'


def api(resource, params, key):
    url = (
        'https://www.googleapis.com/youtube/v3/'
        + resource
        + '?'
        + urlencode({**params, 'key': key})
    )
    for attempt in range(3):
        try:
            with urlopen(
                Request(url, headers={'User-Agent': 'KimAngelWebsite/1.0'}), timeout=30
            ) as response:
                payload = json.load(response)
            if not isinstance(payload.get('items'), list):
                raise ValueError('Unexpected YouTube response: ' + resource)
            return payload
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                # Never log the exception URL: it contains the API key.
                raise RuntimeError(
                    f'YouTube {resource}: HTTP {error.code}. Check API access/quota.'
                ) from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError('YouTube unavailable after three attempts.') from None
        time.sleep(2**attempt)


def published(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('Publication date must include timezone')
    return date


def select_videos(items, now=None):
    now = now or datetime.now(timezone.utc)
    unique = {}
    for item in items:
        snippet, status = item.get('snippet', {}), item.get('status', {})
        if (
            snippet.get('channelId') != CHANNEL_ID
            or status.get('privacyStatus') != 'public'
            or status.get('embeddable') is not True
            or snippet.get('liveBroadcastContent') in ('upcoming', 'live')
        ):
            continue
        video_id = item.get('id', '')
        title, date = snippet.get('title', '').strip(), snippet.get('publishedAt', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id) or not title:
            continue
        if published(date) > now:
            continue
        # Shorts are videos too: no duration filter or guessed format label.
        unique[video_id] = {'id': video_id, 'title': title, 'publishedAt': date}
    return sorted(
        unique.values(), key=lambda v: (published(v['publishedAt']), v['id']), reverse=True
    )[:COUNT]


def fetch_videos(key):
    channels = api('channels', {'part': 'contentDetails', 'id': CHANNEL_ID}, key)['items']
    if len(channels) != 1:
        raise ValueError('Channel not found')
    playlist = channels[0]['contentDetails']['relatedPlaylists']['uploads']
    items, token, chosen = [], None, []
    for _ in range(4):
        params = {'part': 'contentDetails', 'playlistId': playlist, 'maxResults': 50}
        if token:
            params['pageToken'] = token
        page = api('playlistItems', params, key)
        ids = list(dict.fromkeys(x['contentDetails']['videoId'] for x in page['items']))
        if ids:
            items.extend(
                api('videos', {'part': 'snippet,status', 'id': ','.join(ids)}, key)['items']
            )
        chosen = select_videos(items)
        token = page.get('nextPageToken')
        if len(chosen) == COUNT or not token:
            break
    if len(chosen) != COUNT:
        raise ValueError('Fewer than six available uploads; keeping published site unchanged')
    return chosen


def render(videos):
    if len(videos) != COUNT or len({v['id'] for v in videos}) != COUNT:
        raise ValueError('Expected six distinct videos')
    cards = []
    for video in videos:
        vid = video['id']
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid):
            raise ValueError('Invalid video ID')
        title = html.escape(video['title'], quote=True)
        date = published(video['publishedAt'])
        machine_date = html.escape(video['publishedAt'], quote=True)
        cards.append(
            '\n                    <article class="youtube-card">\n'
            f'                        <iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{title}" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>\n'
            f'                        <h3><a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener noreferrer">{title}</a></h3>\n'
            f'                        <time class="youtube-date" datetime="{machine_date}">{date:%d/%m/%Y}</time>\n'
            '                    </article>'
        )
    return ''.join(cards) + '\n                '


def replace_cards(page, videos):
    return replace_region(page, 'youtube', render(videos))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--from-cache', action='store_true', help='Render local snapshot without contacting YouTube'
    )
    args = parser.parse_args()
    cache = ROOT / 'data/youtube.json'
    if args.from_cache:
        videos = json.loads(cache.read_text(encoding='utf-8'))['videos']
    else:
        key = os.environ.get('YOUTUBE_API_KEY', '').strip()
        if not key:
            raise ValueError('Add the YOUTUBE_API_KEY repository secret. See docs/youtube.md')
        videos = fetch_videos(key)
        fetched_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    index = ROOT / 'index.html'
    result = replace_cards(index.read_text(encoding='utf-8'), videos)
    outputs = {}
    if not args.from_cache:
        snapshot = {
            'channelId': CHANNEL_ID,
            'videos': videos,
            'metadata': {'source': 'youtube-data-api', 'fetched_at': fetched_at},
        }
        outputs['data/youtube.json'] = json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n'
    outputs['index.html'] = result
    write_outputs(ROOT, outputs)
    print(f'Rendered {len(videos)} public uploads, newest first.')


if __name__ == '__main__':
    try:
        main()
    except RecoveryRequiredError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, RuntimeError, OSError) as error:
        print(f'YouTube update failed: {error}', file=sys.stderr)
        sys.exit(1)
