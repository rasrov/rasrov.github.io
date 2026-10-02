from pathlib import Path
import tempfile
import unittest

from scripts.check_format import check_text


class FormatTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_fix_normalizes_text_preserves_markdown_and_ignores_outputs(self):
        (self.root / 'example.py').write_bytes(b'\xef\xbb\xbfvalue = 1  \r\n')
        (self.root / 'README.md').write_bytes(b'Hard break  \r\nnext')
        (self.root / 'img').mkdir()
        binary = b'\x00\xff\r\n'
        (self.root / 'img/example.png').write_bytes(binary)
        (self.root / '_site').mkdir()
        (self.root / '_site/index.html').write_bytes(b'generated\r\n')
        self.assertTrue(check_text(self.root))
        self.assertEqual(check_text(self.root, fix=True), [])
        self.assertEqual((self.root / 'example.py').read_bytes(), b'value = 1\n')
        self.assertEqual((self.root / 'README.md').read_bytes(), b'Hard break  \nnext\n')
        self.assertEqual((self.root / 'img/example.png').read_bytes(), binary)
        self.assertEqual((self.root / '_site/index.html').read_bytes(), b'generated\r\n')
        self.assertEqual(check_text(self.root), [])

    def test_check_does_not_write_and_reports_tabs(self):
        path = self.root / 'example.py'
        original = b'\tvalue = 1\r\n'
        path.write_bytes(original)
        self.assertTrue(any('indentation' in error for error in check_text(self.root)))
        self.assertEqual(path.read_bytes(), original)

    def test_invalid_utf8_is_not_replaced(self):
        path = self.root / 'README.md'
        path.write_bytes(b'\xff')
        self.assertTrue(any('invalid UTF-8' in error for error in check_text(self.root, fix=True)))
        self.assertEqual(path.read_bytes(), b'\xff')
