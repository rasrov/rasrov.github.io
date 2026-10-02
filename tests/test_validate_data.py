import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_data import validate_data
from scripts.validation import read_json

ROOT = Path(__file__).resolve().parents[1]


class DataValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'data').mkdir()
        (self.root / 'img/calendar').mkdir(parents=True)
        self.snapshots = {
            path.name: json.loads(path.read_text(encoding='utf-8'))
            for path in (ROOT / 'data').glob('*.json')
        }
        for logo in self.snapshots['competition-logos.json'].values():
            (self.root / logo).write_bytes(b'fixture')
        self.write()

    def write(self):
        for name, value in self.snapshots.items():
            (self.root / 'data' / name).write_text(json.dumps(value), encoding='utf-8')

    def test_current_contracts_and_missing_editorial_decision(self):
        validate_data(self.root)
        self.snapshots['competition-participation.json'] = {}
        self.write()
        validate_data(self.root)

    def test_duplicate_and_invalid_filtered_event(self):
        event = self.snapshots['competitions.json']['events'][0]
        event['name'] = 'Natural Pro'
        self.snapshots['competitions.json']['events'].append(copy.deepcopy(event))
        self.write()
        with self.assertRaisesRegex(ValueError, r'competitions.json.events.*id: duplicate'):
            validate_data(self.root)
        self.snapshots['competitions.json']['events'].pop()
        event['end'] = '2026-02-30'
        self.write()
        with self.assertRaisesRegex(ValueError, r'competitions.json.events.*end: invalid'):
            validate_data(self.root)

    def test_wrong_type_and_reversed_dates(self):
        event = self.snapshots['competitions.json']['events'][0]
        event['id'] = True
        self.write()
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            validate_data(self.root)
        event['id'] = 21727
        event['end'] = '2020-01-01'
        self.write()
        with self.assertRaisesRegex(ValueError, 'precedes start'):
            validate_data(self.root)

    def test_orphan_status_and_logo(self):
        for filename, value in [
            ('competition-participation.json', {'status': 'pending'}),
            ('competition-logos.json', 'img/calendar/logo.png'),
        ]:
            with self.subTest(filename=filename):
                self.snapshots[filename]['999999'] = value
                self.write()
                with self.assertRaisesRegex(ValueError, filename + '.*orphan'):
                    validate_data(self.root)
                del self.snapshots[filename]['999999']
        self.write()
        key = next(iter(self.snapshots['competition-participation.json']))
        self.snapshots['competition-participation.json'][key]['status'] = 'maybe'
        self.write()
        with self.assertRaisesRegex(ValueError, 'status: invalid'):
            validate_data(self.root)

    def test_missing_logo(self):
        logo = next(iter(self.snapshots['competition-logos.json'].values()))
        (self.root / logo).unlink()
        with self.assertRaisesRegex(ValueError, 'competition-logos.json.*missing file'):
            validate_data(self.root)

    def test_social_duplicates_timezone_and_public_allowlist(self):
        posts = self.snapshots['instagram.json']['posts']
        original = copy.deepcopy(posts)
        for mutation, error in [
            (lambda: posts[1].update(id=posts[0]['id']), 'duplicate ID'),
            (lambda: posts[0].update(timestamp='2026-09-30T00:00:00'), 'timezone'),
            (lambda: posts[0].update(access_token='test-private'), 'unexpected public field'),
            (
                lambda: posts[0].update(media_url='https://cdninstagram.com.evil.test/a.jpg'),
                'preview host',
            ),
        ]:
            posts[:] = copy.deepcopy(original)
            mutation()
            self.write()
            with (
                self.subTest(error=error),
                self.assertRaisesRegex(ValueError, 'instagram.json.*' + error),
            ):
                validate_data(self.root)
        posts[:] = original
        self.snapshots['youtube.json']['videos'].pop()
        self.write()
        with self.assertRaisesRegex(ValueError, 'youtube.json.videos: expected 6'):
            validate_data(self.root)

    def test_duplicate_json_keys_are_not_silently_overwritten(self):
        path = self.root / 'data/competition-participation.json'
        path.write_text('{"123": {}, "123": {}}')
        with self.assertRaisesRegex(
            ValueError, 'competition-participation.json.*duplicate JSON key'
        ):
            read_json(path)

    def test_nonfinite_json_numbers_are_rejected(self):
        path = self.root / 'data/competitions.json'
        for value in ('NaN', 'Infinity', '-Infinity'):
            path.write_text('{"value": ' + value + '}')
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'non-finite'):
                read_json(path)
