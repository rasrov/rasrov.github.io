import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_resources import validate_resources


class ResourceValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ('css', 'js', 'img'):
            (self.root / name).mkdir()
        (self.root / 'img/Photo.png').write_bytes(b'image')
        (self.root / 'img/small.webp').write_bytes(b'webp')
        self.manifest = {'img/Photo.png': {'width': 10, 'height': 10, 'bytes': 5,
                         'variants': [{'src': 'img/small.webp', 'width': 5, 'height': 5, 'bytes': 4}]}}
        (self.root / 'img/image-manifest.json').write_text(json.dumps(self.manifest))
        (self.root / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"><url><loc>https://example.test/</loc><image:image><image:loc>https://example.test/img/Photo.png</image:loc></image:image></url></urlset>')
        self.page = '<link rel="canonical" href="https://example.test/"><p id="target">Target</p>'
        self.write_page('')

    def write_page(self, extra):
        (self.root / 'index.html').write_text(self.page + extra, encoding='utf-8')

    def test_local_root_relative_remote_and_data_resources(self):
        self.write_page('<a href="#target">Link</a><img src="/img/Photo.png?x=1" srcset="img/Photo.png 10w, img/small.webp 5w"><img src="https://remote.invalid/image.png"><img srcset="data:image/png;base64,AAAA 1x, img/small.webp 2x">')
        validate_resources(self.root)

    def test_missing_srcset_and_fragment(self):
        for markup, message in [('<img srcset="img/Photo.png 1x, img/missing.webp 2x">', 'srcset.*missing file'),
                                ('<a href="#missing">Link</a>', 'missing HTML fragment'),
                                ('<p id="target">Duplicate</p>', 'duplicate HTML id')]:
            self.write_page(markup)
            with self.subTest(markup=markup), self.assertRaisesRegex(ValueError, message):
                validate_resources(self.root)

    def test_cross_document_fragment(self):
        (self.root / 'other.html').write_text('<p id="other">Other</p>')
        self.write_page('<a href="other.html#other">Other</a>')
        validate_resources(self.root)
        self.write_page('<a href="other.html#missing">Other</a>')
        with self.assertRaisesRegex(ValueError, 'missing HTML fragment'):
            validate_resources(self.root)

    def test_casing_and_path_escape(self):
        for path in ('img/photo.png', '../outside.png', '%2e%2e/outside.png'):
            self.write_page(f'<img src="{path}">')
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_resources(self.root)

    def test_css_urls_imports_and_static_javascript(self):
        (self.root / 'css/style.css').write_text('/* url(missing.png) */ .x { background: url("../img/Photo.png"); }')
        validate_resources(self.root)
        (self.root / 'css/style.css').write_text('@import "missing.css";')
        with self.assertRaisesRegex(ValueError, 'css/style.css.url.*missing file'):
            validate_resources(self.root)
        (self.root / 'css/style.css').write_text('')
        (self.root / 'js/example.js').write_text("const fallback = 'img/missing.png';")
        with self.assertRaisesRegex(ValueError, 'js/example.js.static-path.*missing file'):
            validate_resources(self.root)

    def test_manifest_missing_variant_and_stale_size(self):
        (self.root / 'img/small.webp').unlink()
        with self.assertRaisesRegex(ValueError, 'image-manifest.json.*missing file'):
            validate_resources(self.root)
        (self.root / 'img/small.webp').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'image-manifest.json.*bytes: file size'):
            validate_resources(self.root)

    def test_sitemap_missing_image_or_foreign_page(self):
        path = self.root / 'sitemap.xml'
        original = path.read_text()
        path.write_text(original.replace('Photo.png', 'missing.png'))
        with self.assertRaisesRegex(ValueError, 'sitemap.xml.*missing file'):
            validate_resources(self.root)
        path.write_text(original.replace('<loc>https://example.test/', '<loc>https://foreign.test/'))
        with self.assertRaisesRegex(ValueError, 'sitemap.xml.*outside the canonical'):
            validate_resources(self.root)
        path.write_text('<broken>')
        with self.assertRaisesRegex(ValueError, 'sitemap.xml: invalid'):
            validate_resources(self.root)
