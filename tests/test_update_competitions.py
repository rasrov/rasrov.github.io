"""IFBB refresh regressions with deterministic time and no network access."""

from datetime import date, datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

from scripts import update_competitions as updater
from scripts.validate_data import validate_data

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def event(key=90001):
    return {
        'id': key,
        'title': '2027 Test &amp; Pro',
        'description': '<p>Men&#8217;s Classic Physique<br>Masters Classic Physique</p>',
        'categories': [{'slug': 'professional'}],
        'start_date': '2027-09-30 00:00:00',
        'end_date': '2027-10-01 23:59:59',
        'venue': {'city': 'Madrid'},
        'image': False,
        'url': 'https://www.ifbbpro.com/competition/2027-test-pro/',
    }


def response(rows):
    return {'events': rows, 'total': len(rows), 'total_pages': 1}


class CompetitionFetchTests(unittest.TestCase):
    def test_horizon_initial_and_yearly_rollover(self):
        for day, expected in [
            ('2026-09-30', '2027-10-01'),
            ('2026-10-01', '2027-10-01'),
            ('2027-09-30', '2027-10-01'),
            ('2027-10-01', '2028-10-01'),
            ('2028-02-29', '2028-10-01'),
            ('2028-10-01', '2029-10-01'),
        ]:
            with self.subTest(day=day):
                self.assertEqual(updater.scope_end(date.fromisoformat(day)).isoformat(), expected)

    def test_pagination_filter_and_html_decoding(self):
        rows = [event(key) for key in range(1, 52)]
        rows[0]['categories'] = [{'slug': 'pro-qualifer'}]
        rows[1]['description'] = 'Bodybuilding only'
        rows[2]['title'] = 'Natural Masters Test'
        urls = []

        def fetch(url):
            urls.append(url)
            page = int(parse_qs(urlsplit(url).query)['page'][0])
            return {'events': rows[(page - 1) * 50 : page * 50], 'total': 51, 'total_pages': 2}

        selected, total = updater.fetch_events(date(2027, 10, 1), fetch)
        self.assertEqual((len(selected), total, len(urls)), (49, 51, 2))
        self.assertEqual(selected[0]['name'], 'Natural Masters Test')
        self.assertEqual(selected[-1]['name'], '2027 Test & Pro')
        self.assertIn('Physique\nMasters', selected[-1]['description'])
        self.assertEqual(selected[-1]['country'], '')
        self.assertEqual(selected[-1]['end'], '2027-10-01')
        self.assertEqual(parse_qs(urlsplit(urls[0]).query)['end_date'], ['2027-10-01'])

    def test_reject_empty_partial_duplicate_or_changing_pages(self):
        cases = [
            response([]),
            {'events': [event()], 'total': 2, 'total_pages': 1},
            response([event(), event()]),
            {'events': [event()], 'total': 1, 'total_pages': 2},
        ]
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                updater.fetch_events(date(2027, 10, 1), lambda url: payload)
        first = {'events': [event(key) for key in range(1, 51)], 'total': 51, 'total_pages': 2}
        second = {'events': [event(51), event(52)], 'total': 52, 'total_pages': 2}
        with self.assertRaises(ValueError):
            updater.fetch_events(date(2027, 10, 1), unittest.mock.Mock(side_effect=[first, second]))

    def test_reject_invalid_event_and_outside_scope(self):
        for field, value in [
            ('id', True),
            ('categories', None),
            ('description', None),
            ('start_date', '2027-02-30 00:00:00'),
            ('start_date', '2028-01-01 00:00:00'),
            ('venue', 'invalid'),
        ]:
            row = event()
            row[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                updater.fetch_events(date(2027, 10, 1), lambda url: response([row]))

    def test_network_retries_are_bounded(self):
        with (
            patch.object(updater, 'urlopen', side_effect=URLError('offline')) as request,
            patch.object(updater.time, 'sleep'),
        ):
            with self.assertRaises(RuntimeError):
                updater.request_json(updater.API)
            self.assertEqual(request.call_count, 3)
        with patch.object(
            updater, 'urlopen', side_effect=HTTPError(updater.API, 404, 'missing', {}, None)
        ) as request:
            with self.assertRaises(RuntimeError):
                updater.request_json(updater.API)
            self.assertEqual(request.call_count, 1)


class CompetitionRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'data', self.root / 'data')
        shutil.copytree(ROOT / 'img/calendar', self.root / 'img/calendar')
        self.before = {p.name: p.read_bytes() for p in (self.root / 'data').glob('*.json')}

    def test_merge_preserves_history_and_editorial_files(self):
        previous = json.loads(self.before['competitions.json'])['events']
        changed = event(previous[0]['id'])
        snapshot, report = updater.refresh(self.root, NOW, lambda url: response([changed, event()]))
        self.assertEqual(report['added'], 1)
        self.assertEqual(report['updated'], 1)
        self.assertEqual(len(snapshot['events']), len(previous) + 1)
        self.assertEqual(len(report['retained_missing_ids']), len(previous) - 1)
        for name, original in self.before.items():
            if name != 'competitions.json':
                self.assertEqual((self.root / 'data' / name).read_bytes(), original)
        self.assertFalse((self.root / '.snapshot-update').exists())
        validate_data(self.root)

    def test_dry_run_does_not_write(self):
        updater.refresh(self.root, NOW, lambda url: response([event()]), dry_run=True)
        self.assertEqual(
            (self.root / 'data/competitions.json').read_bytes(), self.before['competitions.json']
        )

    def test_invalid_candidate_and_network_failure_preserve_snapshot(self):
        row = event()
        row['url'] = 'https://example.com/competition/wrong/'
        for fetch in [
            lambda url: response([row]),
            unittest.mock.Mock(side_effect=RuntimeError('offline')),
        ]:
            with self.assertRaises((ValueError, RuntimeError)):
                updater.refresh(self.root, NOW, fetch)
            self.assertEqual(
                (self.root / 'data/competitions.json').read_bytes(),
                self.before['competitions.json'],
            )

    def test_write_failure_preserves_snapshot(self):
        with patch('scripts.snapshot_write.os.replace', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                updater.refresh(self.root, NOW, lambda url: response([event()]))
        self.assertEqual(
            (self.root / 'data/competitions.json').read_bytes(), self.before['competitions.json']
        )

    def test_metadata_rejects_unknown_retained_ids(self):
        snapshot, _ = updater.refresh(self.root, NOW, lambda url: response([event()]), dry_run=True)
        snapshot['metadata']['retained_missing_ids'] = [999999999]
        with self.assertRaises(ValueError):
            validate_data(self.root, competitions=snapshot)
