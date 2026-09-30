import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import render_calendar as calendar



def event(event_id=1, **changes):
    return dict(id=event_id, name='Example Pro', start='2026-09-01', end='2026-09-02',
                url='https://www.ifbbpro.com/competition/example/', description='Classic Physique', **changes)


class CalendarTests(unittest.TestCase):
    def test_empty_events(self):
        self.assertEqual(calendar.render([], {}, {}), '')

    def test_order_status_default_and_escaping(self):
        first = event(1)
        first.update(name='<Example & Pro>', city='A & B')
        second = event(2)
        second.update(start='2026-08-01', end='2026-08-01')
        output = calendar.render([first, second], {'2': {'status': 'confirmed'}}, {})
        self.assertLess(output.index('competition-2'), output.index('competition-1'))
        self.assertIn('&lt;Example &amp; Pro&gt;', output)
        self.assertIn('A &amp; B', output)
        self.assertIn('PARTICIPA', output)
        self.assertIn('PENDIENTE', output)
        self.assertIn('NO PARTICIPA', calendar.render([first], {'1': {'status': 'absent'}}, {}))

    def test_natural_filter_preserves_masters_and_unrelated_divisions(self):
        variants = [event(i) for i in range(1, 5)]
        variants[0]['name'] = 'Natural Pro'
        variants[1]['description'] = 'Natural Classic Physique'
        variants[2]['description'] = 'Masters Classic Physique'
        variants[3]['description'] = 'Classic Physique\nNatural Bikini'
        output = calendar.render(variants, {}, {})
        self.assertNotIn('competition-1', output)
        self.assertNotIn('competition-2', output)
        self.assertIn('competition-3', output)
        self.assertIn('competition-4', output)

    def test_duplicate_ids_including_filtered_events(self):
        for name in ('Example Pro', 'Natural Pro'):
            item = event()
            item['name'] = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                calendar.render([item, copy.deepcopy(item)], {}, {})

    def test_invalid_dates_status_and_source(self):
        for changes in ({'start': 'bad'}, {'end': '2026-08-31'}, {'url': 'https://evil.test/'}):
            item = event()
            item.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                calendar.render([item], {}, {})
        with self.assertRaises(ValueError):
            calendar.render([event()], {'1': {'status': 'unknown'}}, {})

    def test_logo_path_and_existing_logo(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'img/calendar').mkdir(parents=True)
            (root / 'img/calendar/logo.svg').write_text('<svg/>')
            with patch.object(calendar, 'ROOT', root):
                self.assertIn('img/calendar/logo.svg', calendar.render([event()], {}, {'1': 'img/calendar/logo.svg'}))
                for path in ('img/calendar/missing.png', 'img/calendar/../logo.svg', 'https://evil.test/logo.svg'):
                    with self.subTest(path=path), self.assertRaises(ValueError):
                        calendar.render([event()], {}, {'1': path})

    def test_replacement_preserves_other_sections_and_is_idempotent(self):
        page = 'before<!-- youtube:generated:start -->video<!-- youtube:generated:end -->' + calendar.START + 'old' + calendar.END + 'after'
        output = calendar.replace_calendar(page, 'new')
        self.assertEqual(output, page.replace('old', '\nnew\n'))
        self.assertEqual(calendar.replace_calendar(output, 'new'), output)

    def test_invalid_markers(self):
        for page in ('none', calendar.START, calendar.START * 2 + calendar.END, calendar.END + calendar.START):
            with self.subTest(page=page), self.assertRaises(ValueError):
                calendar.replace_calendar(page, 'new')


if __name__ == '__main__':
    unittest.main()
