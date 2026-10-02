import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import update_instagram as ig


def post(i):
    return {
        'id': str(100 + i),
        'permalink': f'https://www.instagram.com/p/post{i}/',
        'media_type': 'CAROUSEL_ALBUM',
        'timestamp': f'2026-09-{i:02d}T12:00:00+0000',
    }


class InstagramTests(unittest.TestCase):
    def setUp(self):
        clock = patch.object(ig, 'datetime', wraps=datetime)
        self.addCleanup(clock.stop)
        clock.start().now.return_value = datetime(2026, 9, 30, tzinfo=timezone.utc)

    def test_order_deduplicate_and_include_reels(self):
        items = [post(i) for i in range(1, 6)]
        items[-1]['media_type'] = 'VIDEO'
        items[-1]['permalink'] = 'https://www.instagram.com/reel/recent/'
        result = ig.select_posts(items + [copy.deepcopy(items[-1])])
        self.assertEqual([p['id'] for p in result], ['105', '104', '103'])
        self.assertEqual(result[0]['media_type'], 'VIDEO')

    def test_reject_foreign_url_and_incomplete_data(self):
        items = [post(i) for i in range(1, 4)]
        items[0]['permalink'] = 'https://evil.test/p/post1/'
        with self.assertRaises(ValueError):
            ig.select_posts(items)
        with self.assertRaises(ValueError):
            ig.select_posts([post(1)])

    def test_allowlist_drops_tokens_and_paging(self):
        items = [post(i) for i in range(1, 4)]
        for p in items:
            p['access_token'] = 'secret'
            p['caption'] = 'unneeded'
            p['paging'] = {'next': 'secret'}
        self.assertNotIn('secret', json.dumps(ig.select_posts(items)))

    def test_render_preserves_youtube_and_escapes(self):
        page = 'YouTube unchanged' + ig.START + 'old' + ig.END + 'Sponsors unchanged'
        result = ig.replace_posts(page, [post(i) for i in range(1, 4)])
        self.assertTrue(result.startswith('YouTube unchanged'))
        self.assertTrue(result.endswith('Sponsors unchanged'))
        self.assertEqual(result.count('class="social-card"'), 3)
        self.assertEqual(result.count('class="social-post"'), 3)
        self.assertEqual(result, ig.replace_posts(result, [post(i) for i in range(1, 4)]))

    def test_previews_and_fallback(self):
        items = [post(i) for i in range(1, 4)]
        items[0]['media_url'] = 'https://scontent.cdninstagram.com/photo.jpg?a=1&b=2'
        items[1].update(
            media_type='VIDEO',
            media_url='https://scontent.cdninstagram.com/video.mp4',
            thumbnail_url='https://scontent.cdninstagram.com/thumb.jpg',
        )
        items[2]['media_url'] = 'https://cdninstagram.com.evil.test/photo.jpg'
        result = ig.replace_posts(ig.START + ig.END, items)
        self.assertEqual(result.count('class="social-image"'), 2)
        self.assertIn('a=1&amp;b=2', result)
        self.assertIn('thumb.jpg', result)
        self.assertNotIn('video.mp4', result)
        self.assertNotIn('evil.test', result)
        self.assertEqual(result.count('class="social-fallback"'), 3)

    def test_failure_leaves_existing_files_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            (root / 'index.html').write_text('original')
            (root / 'data/instagram.json').write_text('original')
            with (
                patch.object(ig, 'ROOT', root),
                patch.dict(ig.os.environ, {'INSTAGRAM_ACCESS_TOKEN': 'secret'}),
                patch.object(ig.sys, 'argv', ['update']),
                patch.object(ig, 'fetch_posts', side_effect=RuntimeError('expired')),
            ):
                with self.assertRaises(RuntimeError):
                    ig.main()
            self.assertEqual((root / 'index.html').read_text(), 'original')
            self.assertEqual((root / 'data/instagram.json').read_text(), 'original')

    def test_token_is_header_and_not_in_url_or_error(self):
        error = HTTPError('https://graph.facebook.com', 403, 'denied', {}, None)
        with patch.object(ig, 'urlopen', side_effect=error) as call:
            with self.assertRaises(RuntimeError) as result:
                ig.fetch_posts('secret-value')
        request = call.call_args.args[0]
        self.assertNotIn('secret-value', request.full_url)
        self.assertEqual(request.get_header('Authorization'), 'Bearer secret-value')
        self.assertNotIn('secret-value', str(result.exception))

    def test_invalid_markers_rejected_with_valid_posts(self):
        posts = [post(i) for i in range(1, 4)]
        for page in ('none', ig.START * 2 + ig.END, ig.START + ig.END * 2, ig.END + ig.START):
            with self.subTest(page=page), self.assertRaisesRegex(ValueError, 'instagram'):
                ig.replace_posts(page, posts)

    def test_injected_clock_and_timezone_boundary(self):
        now = datetime(2026, 9, 3, 12, tzinfo=timezone.utc)
        posts = [post(i) for i in range(1, 5)]
        posts[2]['timestamp'] = '2026-09-03T14:00:00+02:00'
        posts[3]['timestamp'] = '2026-09-03T12:00:01Z'
        self.assertEqual([p['id'] for p in ig.select_posts(posts, now=now)], ['103', '102', '101'])
        with self.assertRaises(ValueError):
            ig.parse_date('2026-09-03T12:00:00')


if __name__ == '__main__':
    unittest.main()
