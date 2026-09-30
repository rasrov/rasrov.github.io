import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from scripts import build, update_instagram, update_youtube


def files(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class BuildTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        for name in build.PUBLIC_DIRECTORIES:
            (self.root / name).mkdir()
        for name in build.PUBLIC_FILES:
            (self.root / name).write_text(name, encoding='utf-8')
        page = 'Manual introduction\n<link rel="canonical" href="https://example.test/">' + ''.join(
            f'<!-- {name}:generated:start -->old<!-- {name}:generated:end -->'
            for name in ('youtube', 'instagram', 'calendar')) + '\nManual footer'
        (self.root / 'index.html').write_text(page, encoding='utf-8')
        videos = [dict(id=f'video{i:06d}', title=f'Video {i}', publishedAt='2020-01-01T12:00:00Z') for i in range(6)]
        posts = [dict(id=str(i), permalink=f'https://www.instagram.com/p/post{i}/',
                      media_type='IMAGE', timestamp='2020-01-01T12:00:00Z') for i in range(3)]
        for name, value in {'youtube.json': {'channelId': update_youtube.CHANNEL_ID, 'videos': videos}, 'instagram.json': {'username': update_instagram.TARGET, 'posts': posts},
                            'competitions.json': {'checked_at': '2026-09-30', 'events': []}, 'competition-logos.json': {},
                            'competition-participation.json': {}}.items():
            (self.root / 'data' / name).write_text(json.dumps(value), encoding='utf-8')
        (self.root / 'img/image-manifest.json').write_text('{}')
        (self.root / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.test/</loc></url></urlset>')
        (self.root / 'google-verification.html').write_text('verification')
        (self.root / 'CNAME').write_text('example.test')
        (self.root / '.env').write_text('PRIVATE_TEST_VALUE')
        (self.root / 'docs').mkdir()
        (self.root / 'docs/private.md').write_text('not public')
        for module in (update_instagram, update_youtube):
            clock = patch.object(module, 'datetime', wraps=datetime)
            self.addCleanup(clock.stop)
            clock.start().now.return_value = datetime(2026, 9, 30, tzinfo=timezone.utc)
            network = patch.object(module, 'urlopen', side_effect=AssertionError('Offline build used network'))
            network.start()
            self.addCleanup(network.stop)

    def test_public_artifact_preserves_sources_and_removes_stale_files(self):
        before = files(self.root)
        output = build.build(self.root)
        first = files(output)
        self.assertEqual({name: (self.root / name).read_bytes() for name in before}, before)
        self.assertEqual(set(p.name for p in output.iterdir()),
                         set(build.PUBLIC_FILES + build.PUBLIC_DIRECTORIES) | {'.nojekyll', 'CNAME', 'google-verification.html'})
        html = (output / 'index.html').read_text(encoding='utf-8')
        self.assertTrue(html.startswith('Manual introduction\n'))
        self.assertTrue(html.endswith('\nManual footer'))
        self.assertEqual(html.count('<iframe '), 6)
        self.assertEqual(html.count('class="social-card"'), 3)
        self.assertNotIn('PRIVATE_TEST_VALUE', html)
        (output / 'obsolete.txt').write_text('stale')
        build.build(self.root)
        self.assertEqual(files(output), first)
        self.assertEqual(list(self.root.glob('.site-build-*')), [])

    def test_invalid_source_preserves_previous_artifact(self):
        output = build.build(self.root)
        before = files(output)
        (self.root / 'index.html').write_text('missing markers')
        with self.assertRaises(ValueError):
            build.build(self.root)
        self.assertEqual(files(output), before)

    def test_copy_failure_preserves_previous_artifact(self):
        output = build.build(self.root)
        before = files(output)
        with patch.object(build.shutil, 'copy2', side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError):
                build.build(self.root)
        self.assertEqual(files(output), before)
        self.assertEqual(list(self.root.glob('.site-build-*')), [])

    def test_failed_install_restores_previous_artifact(self):
        output = build.build(self.root)
        before = files(output)
        rename = Path.rename

        def fail_install(path, target):
            if path.name == 'public':
                raise OSError('install failed')
            return rename(path, target)

        with patch.object(Path, 'rename', fail_install):
            with self.assertRaises(OSError):
                build.build(self.root)
        self.assertEqual(files(output), before)
        self.assertEqual(list(self.root.glob('.site-build-*')), [])

    def test_reject_file_as_output(self):
        (self.root / '_site').write_text('user file')
        with self.assertRaises(ValueError):
            build.build(self.root)
        self.assertEqual((self.root / '_site').read_text(), 'user file')

    def test_broken_resource_keeps_previous_output(self):
        output = build.build(self.root)
        before = files(output)
        with (self.root / 'index.html').open('a', encoding='utf-8') as page:
            page.write('<img src="img/missing.png">')
        with self.assertRaisesRegex(ValueError, 'missing file'):
            build.build(self.root)
        self.assertEqual(files(output), before)
        self.assertEqual(list(self.root.glob('.site-build-*')), [])

    def test_interrupted_snapshot_update_blocks_build(self):
        output = build.build(self.root)
        before = files(output)
        (self.root / '.snapshot-update').mkdir()
        with self.assertRaisesRegex(ValueError, 'Snapshot update active or interrupted'):
            build.build(self.root)
        self.assertEqual(files(output), before)
