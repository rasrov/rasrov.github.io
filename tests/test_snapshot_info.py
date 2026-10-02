from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.snapshot_info import describe


class SnapshotInfoTests(unittest.TestCase):
    def test_comparison_ignores_json_formatting(self):
        with tempfile.TemporaryDirectory() as folder, redirect_stdout(io.StringIO()):
            path = Path(folder) / 'youtube.json'
            snapshot = {
                'metadata': {'source': 'youtube-data-api', 'fetched_at': '2026-09-30T00:00:00Z'},
                'videos': [],
            }
            path.write_text(json.dumps(snapshot, indent=2))
            first = describe(path, 'youtube-data-api')
            path.write_text(json.dumps(snapshot, sort_keys=True))
            self.assertEqual(describe(path, 'youtube-data-api'), first)
            snapshot['metadata']['fetched_at'] = '2026-10-01T00:00:00Z'
            path.write_text(json.dumps(snapshot))
            self.assertNotEqual(describe(path, 'youtube-data-api'), first)

    def test_missing_metadata_is_reported_as_unknown(self):
        with tempfile.TemporaryDirectory() as folder, redirect_stdout(io.StringIO()) as output:
            path = Path(folder) / 'youtube.json'
            path.write_text('{"videos": []}')
            describe(path, 'youtube-data-api')
            self.assertIn('source=legacy-cache, fetched_at=unknown', output.getvalue())
