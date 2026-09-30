from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import update_instagram as ig, update_youtube as yt, snapshot_write
from scripts.validate_data import validate_metadata

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)


class SnapshotMetadataTests(unittest.TestCase):
    def test_online_updates_record_provider_and_fetch_time(self):
        for module, name, field, method, secret, provider in (
            (yt, 'youtube', 'videos', 'fetch_videos', 'YOUTUBE_API_KEY', 'youtube-data-api'),
            (ig, 'instagram', 'posts', 'fetch_posts', 'INSTAGRAM_ACCESS_TOKEN', 'meta-business-discovery'),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
                root = Path(folder)
                (root / 'data').mkdir()
                page = module.START + 'old' + module.END
                (root / 'index.html').write_text(page)
                cache = root / 'data' / (name + '.json')
                cache.write_text('old')
                rows = json.loads((ROOT / 'data' / (name + '.json')).read_text(encoding='utf-8'))[field]
                stack.enter_context(patch.object(module, 'ROOT', root))
                stack.enter_context(patch.object(module.sys, 'argv', ['update']))
                stack.enter_context(patch.dict(module.os.environ, {secret: 'test-secret'}))
                stack.enter_context(patch.object(module, method, return_value=rows))
                clock = stack.enter_context(patch.object(module, 'datetime', wraps=datetime))
                clock.now.return_value = NOW
                module.main()
                snapshot = json.loads(cache.read_text(encoding='utf-8'))
                self.assertEqual(snapshot['metadata'], {'source': provider, 'fetched_at': '2026-09-30T12:00:00Z'})
                self.assertNotIn('test-secret', cache.read_text(encoding='utf-8'))
                validate_metadata(snapshot, name, provider)
                self.assertNotEqual((root / 'index.html').read_text(encoding='utf-8'), page)
                before_cache = cache.read_bytes()
                before_html = (root / 'index.html').read_bytes()
                clock.now.return_value = datetime(2026, 10, 1, tzinfo=timezone.utc)
                original_replace = snapshot_write.os.replace
                def fail_second(source, target):
                    if Path(source).name == '1.next':
                        raise OSError('HTML write failed')
                    return original_replace(source, target)
                with patch.object(snapshot_write.os, 'replace', fail_second), self.assertRaises(OSError):
                    module.main()
                self.assertEqual(cache.read_bytes(), before_cache)
                self.assertEqual((root / 'index.html').read_bytes(), before_html)


    def test_cache_render_preserves_snapshot_bytes_and_metadata(self):
        for module, name in ((yt, 'youtube'), (ig, 'instagram')):
            for metadata in (None, {'source': 'legacy-cache', 'fetched_at': None},
                             {'source': 'youtube-data-api' if name == 'youtube' else 'meta-business-discovery', 'fetched_at': '2026-09-30T00:00:00Z'}):
                with self.subTest(name=name, metadata=metadata), tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
                    root = Path(folder)
                    (root / 'data').mkdir()
                    snapshot = json.loads((ROOT / 'data' / (name + '.json')).read_text(encoding='utf-8'))
                    snapshot.pop('metadata', None)
                    if metadata is not None:
                        snapshot['metadata'] = metadata
                    content = (json.dumps(snapshot, indent=3) + '\r\n').encode('utf-8')
                    cache = root / 'data' / (name + '.json')
                    cache.write_bytes(content)
                    (root / 'index.html').write_text(module.START + 'old' + module.END)
                    stack.enter_context(patch.object(module, 'ROOT', root))
                    stack.enter_context(patch.object(module.sys, 'argv', ['update', '--from-cache']))
                    stack.enter_context(patch.object(module, 'urlopen', side_effect=AssertionError('No network expected')))
                    clock = stack.enter_context(patch.object(module, 'datetime', wraps=datetime))
                    clock.now.return_value = NOW
                    module.main()
                    self.assertEqual(cache.read_bytes(), content)

    def test_bad_metadata_is_rejected(self):
        for metadata in ({'source': 'legacy-cache', 'fetched_at': '2026-09-30T12:00:00Z'},
                         {'source': 'wrong', 'fetched_at': '2026-09-30T12:00:00Z'},
                         {'source': 'youtube-data-api', 'fetched_at': '2026-09-30T12:00:00'},
                         {'source': 'youtube-data-api', 'fetched_at': None},
                         {'source': 'legacy-cache', 'fetched_at': None, 'token': 'secret'}):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                validate_metadata({'metadata': metadata}, 'snapshot', 'youtube-data-api')
