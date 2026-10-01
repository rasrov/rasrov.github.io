"""Real-browser regressions. Run validate.py --browser to require these tests."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BROWSER = os.environ.get('BROWSER_BIN')
SHELL = """<section id="calendario"><h3 id="calendar-month"></h3>
<button id="calendar-prev">Previous</button><button id="calendar-next">Next</button>
<div class="calendar-days"></div><div class="calendar-agenda">
<p class="calendar-empty" hidden>No events</p>{events}</div></section>"""


def card(key, start, end):
    return f'''<article class="calendar-event" id="competition-{key}" data-date="{start}" data-end="{end}"
        data-status="pending" data-logo="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E">
        <h3>Event {key}</h3></article>'''


@unittest.skipUnless(BROWSER, 'Use python scripts/validate.py --browser for Chrome/Edge regressions')
class CalendarBrowserTests(unittest.TestCase):
    def check_page(self, markup, assertions, scripts=None, bootstrap=None, setup='', styles=''):
        scripts = ['navigation-controls', 'calendar'] if scripts is None else scripts
        source = '\n'.join((ROOT / 'js' / (name + '.js')).read_text(encoding='utf-8') for name in scripts)
        if bootstrap is None:
            bootstrap = 'window.KimSite.initCalendar();'
        source += '\n' + bootstrap
        page = '<!doctype html><html lang="es"><meta charset="utf-8"><body>' + markup
        page += "<script>window.testErrors = []; addEventListener('error', e => testErrors.push(e.message));</script>"
        page += '<style>' + styles + '</style><script>' + setup + '</script>'
        page += '<script>' + source + '</script>'
        page += """<script>
function check(condition, message) { if (!condition) throw new Error(message); }
(async () => {
try {
    check(testErrors.length === 0, testErrors.join('; '));
""" + assertions + """
    check(testErrors.length === 0, testErrors.join('; '));
    document.body.dataset.tests = 'passed';
} catch (error) {
    document.body.dataset.tests = 'failed';
    document.body.append(error.message);
 }
})();
</script></body></html>"""
        with tempfile.TemporaryDirectory(prefix='calendar-browser-') as folder:
            file = Path(folder) / 'test.html'
            file.write_text(page, encoding='utf-8')
            result = subprocess.run([
                BROWSER, '--headless', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
                '--disable-background-networking', '--disable-extensions',
                '--user-data-dir=' + str(Path(folder) / 'profile'),
                '--dump-dom', '--virtual-time-budget=3000', '--timeout=10000', file.as_uri(),
            ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr[-1500:])
            self.assertTrue('data-tests="passed"' in result.stdout, result.stdout[-2500:])

    def test_absent_section(self):
        self.check_page('<p>Page without calendar</p>', "check(!document.querySelector('.calendar-event-list'), 'Unexpected initialization');")

    def test_empty_calendar_can_change_month(self):
        self.check_page(SHELL.format(events=''), """
KimSite.initCalendar();
check(document.querySelectorAll('.calendar-event-list').length === 1, 'Duplicate calendar initialization');
check(!document.querySelector('.calendar-empty').hidden, 'Empty message missing');
check(document.querySelector('.calendar-pagination').hidden, 'Empty pager should be hidden');
check(document.querySelectorAll('.calendar-days > *').length >= 28, 'Month grid missing');
const initial = document.querySelector('#calendar-month').textContent;
document.querySelector('#calendar-next').click();
check(document.querySelector('#calendar-month').textContent !== initial, 'Next month failed');
document.querySelector('#calendar-prev').click();
check(document.querySelector('#calendar-month').textContent === initial, 'Previous month failed');
""")

    def test_multiday_labels_popup_and_selection(self):
        events = card(1, '2026-09-24', '2026-09-27') + card(2, '2026-09-26', '2026-09-26') + card(3, '2026-08-31', '2026-09-01')
        self.check_page(SHELL.format(events=events), """
const tiles = [...document.querySelectorAll('.calendar-days > button')];
check(!document.querySelector('.calendar-days > button.is-empty'), 'Padding cell must not be focusable');
const labels = tiles.map(tile => tile.getAttribute('aria-label'));
for (const day of [1, 24, 25, 26, 27]) {
    check(labels.some(label => label.startsWith(day + ' septiembre de 2026')), 'Date missing: ' + day);
}
check(new Set(labels).size === labels.length, 'Indistinguishable day buttons');
const multiple = tiles.find(tile => tile.classList.contains('multiple-events'));
multiple.click();
const popup = document.querySelector('#calendar-day-popup');
check(popup.matches(':popover-open'), 'Popup did not open');
const options = [...popup.querySelectorAll('.calendar-day')];
check(options.length === 2, 'Wrong popup event count');
check(options.every(tile => tile.getAttribute('aria-label').startsWith('26 septiembre de 2026')), 'Popup date missing');
check(document.activeElement === options[0], 'Popup focus missing');
options[1].click();
check(!popup.matches(':popover-open'), 'Popup did not close');
check(document.activeElement.id === 'competition-2', 'Selected event did not receive focus');
check(!document.activeElement.hidden, 'Selected event hidden');
document.querySelector('#calendar-next').click();
check(!document.querySelector('.calendar-empty').hidden, 'Empty next month missing');
""")

    def test_popover_fallback_close_focus_and_selection(self):
        events = card(1, '2026-09-26', '2026-09-26') + card(2, '2026-09-26', '2026-09-26')
        self.check_page(SHELL.format(events=events) + '<button id="outside">Outside</button>', """
const trigger = document.querySelector('.multiple-events');
const popup = document.querySelector('#calendar-day-popup');
check(popup.hidden, 'Fallback visible before opening');
trigger.click();
check(!popup.hidden && trigger.getAttribute('aria-expanded') === 'true', 'Fallback did not open');
check(popup.contains(document.activeElement), 'Fallback focus missing');
document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}));
check(popup.hidden && document.activeElement === trigger, 'Escape did not restore focus');
trigger.click();
document.querySelector('#outside').click();
check(popup.hidden && trigger.getAttribute('aria-expanded') === 'false', 'Outside close failed');
trigger.click();
popup.querySelector('.calendar-day').click();
check(popup.hidden && document.activeElement.id === 'competition-1', 'Fallback selection failed');
trigger.click();
popup.querySelector('.calendar-popup-header button').click();
check(popup.hidden && document.activeElement === trigger, 'Close button focus failed');
""", setup="HTMLElement.prototype.showPopover = undefined; HTMLElement.prototype.hidePopover = undefined; window.ResizeObserver = undefined;")

    def test_agenda_pagination_boundaries(self):
        events = ''.join(card(i, '2026-09-26', '2026-09-26') for i in range(5))
        self.check_page(SHELL.format(events=events), """
const [previous, next] = document.querySelectorAll('.calendar-pagination button');
const visible = () => [...document.querySelectorAll('.calendar-event')].filter(e => !e.hidden);
check(visible().length === 3 && previous.getAttribute('aria-disabled') === 'true', 'First page invalid');
next.focus(); next.click();
check(visible().length === 2 && next.getAttribute('aria-disabled') === 'true', 'Last page invalid');
next.click();
check(visible().length === 2 && document.activeElement === next, 'Boundary lost page/focus');
previous.click();
check(visible().length === 3, 'Previous page failed');
""")

    def test_participation_uses_text_and_complete_accessible_labels(self):
        events = ''.join(card(i, f'2026-09-{20+i}', f'2026-09-{20+i}').replace('data-status="pending"', f'data-status="{status}"') for i, status in enumerate(['pending', 'confirmed', 'absent']))
        self.check_page(SHELL.format(events=events), """
check(!document.querySelector('.calendar-legend, .calendar-status-symbol'), 'Unexpected legend or symbols');
for (const [status, label] of [['pending','Pendiente'],['confirmed','Participa'],['absent','No participa']]) {
    const tile = document.querySelector('.calendar-days .' + status);
    check(tile.querySelector('.calendar-status-label').textContent === label, 'Full state text missing');
    check(tile.getAttribute('aria-label').includes('Kim: ' + label), 'Accessible state missing');
    const style = getComputedStyle(tile.querySelector('.calendar-status-label'));
    check(style.display !== 'none' && style.textTransform === 'uppercase' && parseFloat(style.letterSpacing) > 0, 'State text styling missing');
}
""", styles=(ROOT / 'css/styles.css').read_text(encoding='utf-8'))

    def test_multiple_day_uses_first_event_logo_and_preserves_counter(self):
        first = card(1, '2026-09-26', '2026-09-26')
        second = card(2, '2026-09-26', '2026-09-26').replace('/%3E', '/%3E#second')
        self.check_page(SHELL.format(events=first + second), """
const tile = document.querySelector('.multiple-events');
const logo = tile.querySelector('img');
check(logo.getAttribute('src') === document.querySelector('#competition-1').dataset.logo, 'First event logo not used');
check(tile.querySelector('span').textContent === '+2', 'Competition count changed');
check(getComputedStyle(logo).opacity === '0.38', 'Multiple-event opacity changed');
logo.dispatchEvent(new Event('error'));
check(logo.getAttribute('src') === 'img/calendar/default-championship.png', 'Missing logo fallback failed');
logo.dispatchEvent(new Event('error'));
check(!tile.querySelector('img') && tile.querySelector('span').textContent === '+2', 'Fallback failure lost count');
tile.click();
check(document.querySelectorAll('.calendar-popup-tiles .calendar-day').length === 2, 'Competition selector changed');
""", styles=(ROOT / 'css/styles.css').read_text(encoding='utf-8'))

    def test_multiple_day_prefers_first_custom_logo_or_default(self):
        import re
        fallback = 'img/calendar/default-championship.png'
        for logos, expected in [(['', 'own', 'own2'], 'own'), ([fallback, 'own', 'own2'], 'own'), (['', fallback, ''], fallback)]:
            with self.subTest(logos=logos):
                sources = [value if value in ('', fallback) else "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E#" + value for value in logos]
                markup = ''.join(re.sub(r'data-logo="[^"]*"', 'data-logo="' + source + '"', card(i, '2026-09-26', '2026-09-26')) for i, source in enumerate(sources))
                expected_src = fallback if expected == fallback else sources[1]
                self.check_page(SHELL.format(events=markup), """
const tile = document.querySelector('.multiple-events');
check(tile.querySelector('img').getAttribute('src') === """ + repr(expected_src) + """, 'Wrong shared-day preview');
check(tile.querySelector('span').textContent === '+3', 'Count changed');
tile.click();
check(document.querySelectorAll('.calendar-popup-tiles .calendar-day').length === 3, 'Selector lost events');
""")


if __name__ == '__main__':
    unittest.main()
