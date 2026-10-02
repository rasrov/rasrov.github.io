import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_build
from scripts import optimize_images as optimizer, snapshot_write

try:
    from PIL import Image
except ImportError:
    Image = None


@unittest.skipUnless(Image, 'Install requirements-images.txt to test image optimization')
class ImageOptimizationTests(unittest.TestCase):
    def setUp(self):
        test_build.BuildTests.setUp(self)
        from test_render_calendar import event

        (self.root / 'data/competitions.json').write_text(
            json.dumps({'checked_at': '2026-09-30', 'events': [event()]})
        )
        self.name = 'img/calendar/example.png'
        self.image = self.root / self.name
        self.image.parent.mkdir()
        Image.new('RGBA', (400, 200), (30, 100, 200, 128)).save(self.image)
        with (self.root / 'index.html').open('a', encoding='utf-8') as page:
            page.write(
                f'<img src="{self.name}" alt="Example" sizes="50vw" data-full-src="{self.name}">'
            )
        (self.root / 'data/competition-logos.json').write_text(json.dumps({'1': self.name}))

    def test_generation_preserves_original_alpha_and_is_idempotent(self):
        original = self.image.read_bytes()
        report = optimizer.optimize(self.root)
        self.assertEqual(report['generated'], [self.name])
        self.assertEqual(self.image.read_bytes(), original)
        entry = json.loads((self.root / 'img/image-manifest.json').read_text())[self.name]
        self.assertEqual([v['width'] for v in entry['variants']], [160, 320, 400])
        for variant in entry['variants']:
            with Image.open(self.root / variant['src']) as image:
                self.assertEqual(image.getpixel((0, 0))[3], 128)
        page = (self.root / 'index.html').read_text()
        self.assertIn('sizes="50vw"', page)
        self.assertIn(f'data-full-src="{self.name}"', page)
        self.assertIn('srcset=', page)
        logos = json.loads((self.root / 'data/competition-logos.json').read_text())
        self.assertEqual(logos['1'], entry['variants'][1]['src'])
        before = test_build.files(self.root)
        self.assertEqual(optimizer.plan(self.root)[0], {})
        optimizer.optimize(self.root)
        self.assertEqual(test_build.files(self.root), before)

    def test_changed_original_and_missing_variant_are_repaired(self):
        optimizer.optimize(self.root)
        Image.new('RGBA', (100, 50), (200, 0, 0, 128)).save(self.image)
        self.assertEqual(optimizer.optimize(self.root)['generated'], [self.name])
        entry = json.loads((self.root / 'img/image-manifest.json').read_text())[self.name]
        self.assertEqual([v['width'] for v in entry['variants']], [100])
        (self.root / entry['variants'][0]['src']).unlink()
        self.assertEqual(optimizer.optimize(self.root)['generated'], [self.name])
        self.assertEqual(optimizer.plan(self.root)[0], {})

    def test_legacy_variants_adopted_without_reencoding(self):
        optimizer.optimize(self.root)
        manifest_path = self.root / 'img/image-manifest.json'
        manifest = json.loads(manifest_path.read_text())
        del manifest[self.name]['optimization']
        manifest_path.write_text(json.dumps(manifest))
        variants = {
            v['src']: (self.root / v['src']).read_bytes() for v in manifest[self.name]['variants']
        }
        self.assertEqual(optimizer.optimize(self.root)['adopted'], [self.name])
        for name, data in variants.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        self.assertEqual(optimizer.optimize(self.root, force=True)['generated'], [self.name])

    def test_dry_run_and_validation_failure_preserve_all_files(self):
        before = test_build.files(self.root)
        optimizer.optimize(self.root, dry_run=True)
        self.assertEqual(test_build.files(self.root), before)
        with patch.object(
            optimizer, 'validate_resources', side_effect=ValueError('broken resource')
        ):
            with self.assertRaises(ValueError):
                optimizer.optimize(self.root)
        self.assertEqual(test_build.files(self.root), before)

    def test_exif_orientation_applied(self):
        name = 'img/photo.jpg'
        exif = Image.Exif()
        exif[274] = 6
        Image.new('RGB', (80, 40)).save(self.root / name, exif=exif)
        optimizer.optimize(self.root, source=name)
        entry = json.loads((self.root / 'img/image-manifest.json').read_text())[name]
        self.assertEqual((entry['width'], entry['height']), (40, 80))

    def test_unsafe_source_rejected(self):
        for name in ('../outside.png', 'img/../outside.png', 'img/optimized/photo.webp'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                optimizer.optimize(self.root, source=name)

    def test_binary_install_failure_rolls_back_new_files(self):
        before = test_build.files(self.root)
        replace = snapshot_write.os.replace

        def fail(source, target):
            if Path(source).name == '1.next':
                raise OSError('disk unavailable')
            return replace(source, target)

        with patch.object(snapshot_write.os, 'replace', fail), self.assertRaises(OSError):
            optimizer.optimize(self.root)
        self.assertEqual(test_build.files(self.root), before)

    def test_writer_refuses_original_image_overwrite(self):
        with self.assertRaises(ValueError):
            snapshot_write.write_outputs(self.root, {self.name: b'bad'}, image_assets=True)
