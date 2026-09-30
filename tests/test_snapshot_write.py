import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import snapshot_write as writer


class SnapshotWriteTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        (self.root / 'data').mkdir()
        self.cache = self.root / 'data/youtube.json'
        self.index = self.root / 'index.html'
        self.cache.write_bytes(b'old-json\r\n')
        self.index.write_bytes(b'old-html\r\n')
        self.outputs = {'data/youtube.json': 'new-json\n', 'index.html': 'new-html\n'}

    def assert_originals(self):
        self.assertEqual(self.cache.read_bytes(), b'old-json\r\n')
        self.assertEqual(self.index.read_bytes(), b'old-html\r\n')

    def test_success_replaces_both_outputs(self):
        writer.write_outputs(self.root, self.outputs)
        self.assertEqual(self.cache.read_bytes(), b'new-json\n')
        self.assertEqual(self.index.read_bytes(), b'new-html\n')
        self.assertFalse((self.root / '.snapshot-update').exists())

    def test_second_preparation_failure_leaves_originals(self):
        original = Path.write_bytes
        def fail(path, value):
            if path.name == '1.next':
                raise OSError('full disk')
            return original(path, value)
        with patch.object(Path, 'write_bytes', fail), self.assertRaises(OSError):
            writer.write_outputs(self.root, self.outputs)
        self.assert_originals()
        self.assertFalse((self.root / '.snapshot-update').exists())

    def test_second_install_failure_restores_exact_bytes(self):
        original = writer.os.replace
        def fail(source, target):
            if Path(source).name == '1.next':
                raise OSError('write denied')
            return original(source, target)
        with patch.object(writer.os, 'replace', fail), self.assertRaises(OSError):
            writer.write_outputs(self.root, self.outputs)
        self.assert_originals()
        self.assertFalse((self.root / '.snapshot-update').exists())

    def test_failed_restore_keeps_journal_and_blocks_retry(self):
        original = writer.os.replace
        def fail(source, target):
            if Path(source).name in ('1.next', '0.restore'):
                raise OSError('disk unavailable')
            return original(source, target)
        with patch.object(writer.os, 'replace', fail), self.assertRaises(writer.RecoveryRequiredError):
            writer.write_outputs(self.root, self.outputs)
        folder = self.root / '.snapshot-update'
        self.assertEqual((folder / '0.previous').read_bytes(), b'old-json\r\n')
        self.assertEqual(json.loads((folder / 'recovery.json').read_text())[0]['path'], 'data/youtube.json')
        with self.assertRaises(writer.RecoveryRequiredError):
            writer.write_outputs(self.root, self.outputs)

    def test_created_file_is_removed_on_rollback(self):
        self.cache.unlink()
        original = writer.os.replace
        def fail(source, target):
            if Path(source).name == '1.next':
                raise OSError('write denied')
            return original(source, target)
        with patch.object(writer.os, 'replace', fail), self.assertRaises(OSError):
            writer.write_outputs(self.root, self.outputs)
        self.assertFalse(self.cache.exists())
        self.assertEqual(self.index.read_bytes(), b'old-html\r\n')

    def test_unexpected_path_rejected(self):
        with self.assertRaises(ValueError):
            writer.write_outputs(self.root, {'../outside.txt': 'x'})
        self.assert_originals()
