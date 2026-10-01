"""Browser regressions for the shared card entrance component."""
import os
import subprocess
import tempfile
from pathlib import Path
import unittest

import test_calendar_browser as calendar_tests

ROOT = Path(__file__).resolve().parents[1]
STYLES = (ROOT / 'css/styles.css').read_text(encoding='utf-8')
MARKUP = '<div data-entry-group><a id="a" href="#end">A</a><a id="b" href="#end">B</a><a id="c" href="#end">C</a></div><div id="end"></div>'
OBSERVER = """
window.observers = [];
window.IntersectionObserver = class {
    constructor(callback) { this.callback = callback; this.targets = new Set(); observers.push(this); }
    observe(target) { this.targets.add(target); }
    unobserve(target) { this.targets.delete(target); }
};
"""


@unittest.skipUnless(os.environ.get('BROWSER_BIN'), 'Run validate.py --browser')
class CardEntranceTests(unittest.TestCase):
    check_page = calendar_tests.CalendarBrowserTests.check_page

    def run_page(self, assertions, setup=OBSERVER, markup=MARKUP):
        self.check_page(markup, assertions, scripts=['card-entrances'],
                        bootstrap='KimSite.initCardEntrances();', setup=setup, styles=STYLES)

    def test_order_stagger_idempotence_focus_and_single_entry(self):
        self.run_page("""
KimSite.initCardEntrances();
check(observers.length === 1 && observers[0].targets.size === 3, 'Duplicate observers/registration');
const [a,b,c] = ['a','b','c'].map(id => document.getElementById(id));
observers[0].callback([c,a,b].map(target => ({target, isIntersecting:true})));
check([a,b,c].map(e => getComputedStyle(e).animationDelay).join(',') === '0s,0.2s,0.4s', 'Incorrect visual order or stagger');
check(getComputedStyle(a).animationName === 'card-entry', 'Shared animation missing');
check([a,b,c].every(e => getComputedStyle(e).opacity === '1'), 'Entrance changed opacity');
b.focus();
check(getComputedStyle(b).opacity === '1' && getComputedStyle(b).animationName === 'none', 'Focused card hidden by delay: ' + JSON.stringify({active:document.activeElement.id,classes:b.className,opacity:getComputedStyle(b).opacity}));
a.dispatchEvent(new AnimationEvent('animationend', {animationName:'card-entry'}));
check(!a.classList.contains('is-entering'), 'Finished transform not cleared');
observers[0].callback([{target:a,isIntersecting:true}]);
check(!a.classList.contains('is-entering'), 'Entry repeated');
const added = document.createElement('a'); added.textContent = 'New'; a.parentElement.append(added);
KimSite.initCardEntrances(a.parentElement);
check(observers[0].targets.has(added) && observers.length === 1, 'Dynamic group needs a separate implementation');
""")

    def test_reduced_motion_change_finishes_running_animation(self):
        self.run_page("""
const a = document.querySelector('#a');
observers[0].callback([{target:a,isIntersecting:true}]);
check(a.classList.contains('is-entering'), 'Animation did not start');
preference.matches = true; preference.changed();
check(!document.querySelector('.is-entering, .is-entry-ready'), 'Motion preference did not clear active and prepared cards');
const b = document.querySelector('#b');
observers[0].callback([{target:b,isIntersecting:true}]);
check(!b.classList.contains('is-entering'), 'Motion preference ignored');
""", setup=OBSERVER + "window.preference = {matches:false, addEventListener:(name, callback)=>preference.changed=callback}; window.matchMedia=()=>preference;")

    def test_no_observer_or_reduced_motion_leaves_content_visible(self):
        for setup in ['window.IntersectionObserver=undefined;', "window.matchMedia=()=>({matches:true});"]:
            with self.subTest(setup=setup):
                self.run_page("""
check(!document.querySelector('.is-entering'), 'Fallback started animation');
check([...document.querySelectorAll('[data-entry-group] > *')].every(e => getComputedStyle(e).opacity === '1'), 'Fallback hides content');
""", setup=setup)

    def test_real_observer_reveals_after_scroll(self):
        # Real compositor frames are needed: dump-dom's virtual clock can outrun IO.
        source = (ROOT / 'js/card-entrances.js').read_text(encoding='utf-8')
        markup = '<div style="height:2000px"></div><div data-entry-group><div id="a" style="height:100px">Card</div></div>'
        checks = """
window.runFrameChecks = async () => {
    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
    const card = document.querySelector('#a');
    let started = 0;
    card.addEventListener('animationstart', () => started++);
    KimSite.initCardEntrances();
    await wait(150);
    if (started) throw new Error('Offscreen card entered early');
    if (getComputedStyle(card).opacity !== '1' || new DOMMatrix(getComputedStyle(card).transform).m42 !== 80) throw new Error('Starting position not prepared');
    card.scrollIntoView({behavior:'instant'});
    for (let i=0; i<30 && !started; i++) await wait(50);
    if (started !== 1) throw new Error('Scrolling did not start exactly one entrance');
    let previous = 80;
    for (let i=0; i<8; i++) {
        const style = getComputedStyle(card);
        const offset = new DOMMatrix(style.transform).m42;
        if (style.opacity !== '1' || offset > previous + 0.1 || offset < -0.1) throw new Error('Flicker or downward jump during entry');
        previous = offset;
        await wait(100);
    }
    await wait(parseFloat(getComputedStyle(card).animationDuration) * 1000 + 300);
    if (getComputedStyle(card).opacity !== '1' || card.classList.contains('is-entering')) throw new Error('Animation did not finish cleanly');
    window.scrollTo({top:0, behavior:'instant'});
    await wait(150);
    card.scrollIntoView({behavior:'instant'});
    await wait(150);
    if (started !== 1) throw new Error('Animation repeated');
    return true;
};
"""
        with tempfile.TemporaryDirectory(prefix='card-frames-') as folder:
            page = Path(folder) / 'test.html'
            page.write_text('<!doctype html><meta charset="utf-8"><style>' + STYLES + '</style>' + markup + '<script>' + source + checks + '</script>', encoding='utf-8')
            result = subprocess.run(['node', str(ROOT / 'tests/browser_frames.mjs'), page.as_uri(), str(Path(folder) / 'profile')], capture_output=True, text=True, timeout=25)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
