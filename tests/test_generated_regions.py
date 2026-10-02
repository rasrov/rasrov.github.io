import unittest

from scripts.generated_regions import replace_region


class GeneratedRegionTests(unittest.TestCase):
    def test_exact_surroundings_and_idempotence(self):
        page = (
            'before\r\n<!-- youtube:generated:start -->old<!-- youtube:generated:end -->\r\nafter'
        )
        result = replace_region(page, 'youtube', 'new\n')
        self.assertEqual(result, page.replace('old', 'new\n'))
        self.assertEqual(replace_region(result, 'youtube', 'new\n'), result)

    def test_reject_missing_duplicate_and_reversed_markers(self):
        for name in ('youtube', 'instagram', 'calendar'):
            start = f'<!-- {name}:generated:start -->'
            end = f'<!-- {name}:generated:end -->'
            for page in ('', start, end, start + start + end, start + end + end, end + start):
                with self.subTest(name=name, page=page), self.assertRaisesRegex(ValueError, name):
                    replace_region(page, name, 'new')

    def test_other_regions_are_preserved(self):
        page = ''.join(
            f'<!-- {name}:generated:start -->{name}<!-- {name}:generated:end -->'
            for name in ('youtube', 'instagram', 'calendar')
        )
        result = replace_region(page, 'instagram', 'replacement')
        self.assertEqual(result, page.replace('-->instagram<!--', '-->replacement<!--'))
