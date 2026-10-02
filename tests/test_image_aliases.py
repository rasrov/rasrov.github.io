import json
import unittest

import test_build
from scripts import build
from scripts.image_aliases import materialize_image_aliases


class ImageAliasTests(unittest.TestCase):
    def setUp(self):
        test_build.BuildTests.setUp(self)
        (self.root / 'img/new.png').write_bytes(b'original image bytes')
        self.mapping = self.root / 'img/image-aliases.json'
        self.mapping.write_text(json.dumps({'img/old_name.png': 'img/new.png'}))

    def test_build_preserves_old_urls_without_duplicating_sources(self):
        before = test_build.files(self.root)
        output = build.build(self.root)
        self.assertEqual(
            (output / 'img/old_name.png').read_bytes(), (output / 'img/new.png').read_bytes()
        )
        self.assertFalse((self.root / 'img/old_name.png').exists())
        self.assertEqual({name: (self.root / name).read_bytes() for name in before}, before)
        initial = test_build.files(output)
        build.build(self.root)
        self.assertEqual(test_build.files(output), initial)

    def test_broken_alias_preserves_previous_build(self):
        output = build.build(self.root)
        before = test_build.files(output)
        self.mapping.write_text(json.dumps({'img/old.png': 'img/missing.png'}))
        with self.assertRaisesRegex(ValueError, 'missing file'):
            build.build(self.root)
        self.assertEqual(test_build.files(output), before)

    def test_reject_unsafe_paths_chains_and_collisions_before_copying(self):
        cases = [
            {'../outside.png': 'img/new.png'},
            {'img/../outside.png': 'img/new.png'},
            {'img/old.png': 'https://example.test/new.png'},
            {'img/a.png': 'img/b.png', 'img/b.png': 'img/new.png'},
            {'img/new.png': 'img/new.png'},
            {'img/new.png': 'img/another.png'},
        ]
        (self.root / 'img/another.png').write_bytes(b'another')
        for mapping in cases:
            with self.subTest(mapping=mapping):
                self.mapping.write_text(json.dumps(mapping))
                before = test_build.files(self.root)
                with self.assertRaises(ValueError):
                    materialize_image_aliases(self.root)
                self.assertEqual(test_build.files(self.root), before)
