import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import update_youtube as yt


def item(i, **overrides):
    value = {
        'id': f'video{i:06d}',
        'snippet': {
            'channelId': yt.CHANNEL_ID,
            'title': f'Video {i}',
            'publishedAt': f'2026-09-{i:02d}T12:00:00Z',
            'liveBroadcastContent': 'none',
        },
        'status': {'privacyStatus': 'public', 'embeddable': True},
    }
    for section, fields in overrides.items():
        value[section].update(fields)
    return value


class YouTubeTests(unittest.TestCase):
    def setUp(self):
        clock = patch.object(yt, 'datetime', wraps=datetime)
        self.addCleanup(clock.stop)
        clock.start().now.return_value = datetime(2026, 9, 30, tzinfo=timezone.utc)

    def test_newest_six_unique_and_short_not_filtered(self):
        items = [item(i) for i in range(1, 9)]
        items[-1]['contentDetails'] = {'duration': 'PT30S'}
        selected = yt.select_videos(items + [items[-1]])
        self.assertEqual([v['id'] for v in selected], [f'video{i:06d}' for i in range(8, 2, -1)])

    def test_unavailable_foreign_future_and_live_excluded(self):
        items = [
            item(1),
            item(2, status={'privacyStatus': 'private'}),
            item(3, status={'embeddable': False}),
            item(4, snippet={'liveBroadcastContent': 'upcoming'}),
            item(5, snippet={'channelId': 'other'}),
            item(6, snippet={'liveBroadcastContent': 'live'}),
            item(7, snippet={'publishedAt': '2099-01-01T00:00:00Z'}),
        ]
        self.assertEqual([v['id'] for v in yt.select_videos(items)], ['video000001'])

    def test_render_escape_and_preserve_other_sections(self):
        videos = yt.select_videos([item(i) for i in range(1, 7)])
        videos[0]['title'] = '<script>alert("x")</script> & hola'
        page = 'before' + yt.START + 'old' + yt.END + 'after'
        result = yt.replace_cards(page, videos)
        self.assertTrue(result.startswith('before' + yt.START))
        self.assertTrue(result.endswith(yt.END + 'after'))
        self.assertNotIn('<script>', result)
        self.assertEqual(result.count('<iframe '), 6)
        self.assertEqual(result, yt.replace_cards(result, videos))

    def test_incomplete_results_cannot_render(self):
        with self.assertRaises(ValueError):
            yt.render(yt.select_videos([item(1)]))

    def test_pagination_past_unavailable_uploads(self):
        responses = [
            {'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'uploads'}}}]},
            {'items': [{'contentDetails': {'videoId': 'video000001'}}], 'nextPageToken': 'next'},
            {'items': [item(1, status={'embeddable': False})]},
            {'items': [{'contentDetails': {'videoId': f'video{i:06d}'}} for i in range(2, 8)]},
            {'items': [item(i) for i in range(2, 8)]},
        ]
        with patch.object(yt, 'api', side_effect=responses) as api:
            self.assertEqual(len(yt.fetch_videos('test-key')), 6)
            self.assertEqual(api.call_args_list[3].args[1]['pageToken'], 'next')

    def test_http_error_does_not_expose_secret(self):
        error = HTTPError('https://example.test/?key=secret', 403, 'denied', {}, None)
        with patch.object(yt, 'urlopen', side_effect=error):
            with self.assertRaises(RuntimeError) as result:
                yt.api('videos', {}, 'secret')
        self.assertNotIn('secret', str(result.exception))

    def test_invalid_markers_rejected_with_valid_videos(self):
        videos = yt.select_videos([item(i) for i in range(1, 7)])
        for page in (
            '<html></html>',
            yt.START * 2 + yt.END,
            yt.START + yt.END * 2,
            yt.END + yt.START,
        ):
            with self.subTest(page=page), self.assertRaisesRegex(ValueError, 'youtube'):
                yt.replace_cards(page, videos)

    def test_injected_clock_and_timezone_boundary(self):
        now = datetime(2026, 9, 3, 12, tzinfo=timezone.utc)
        items = [
            item(1),
            item(2, snippet={'publishedAt': '2026-09-03T14:00:00+02:00'}),
            item(3, snippet={'publishedAt': '2026-09-03T12:00:01Z'}),
        ]
        self.assertEqual(
            [v['id'] for v in yt.select_videos(items, now=now)], ['video000002', 'video000001']
        )
        with self.assertRaises(ValueError):
            yt.published('2026-09-03T12:00:00')


if __name__ == '__main__':
    unittest.main()
