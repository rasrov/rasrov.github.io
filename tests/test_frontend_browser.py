import os
import re
import unittest
from pathlib import Path

import test_calendar_browser as calendar_tests

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = re.findall(r'<script src="js/([^"/]+)\.js"', (ROOT / 'index.html').read_text(encoding='utf-8'))
PIXEL = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10'/%3E"
MENU = '<nav class="hero-nav"><button class="nav-toggle" aria-expanded="false">Menu</button><a href="#target">Target</a></nav><p id="target">Target</p><button id="outside">Outside</button>'


@unittest.skipUnless(os.environ.get('BROWSER_BIN'), 'Run validate.py --browser')
class FrontendBrowserTests(unittest.TestCase):
    check_page = calendar_tests.CalendarBrowserTests.check_page

    def run_page(self, markup, assertions, **kwargs):
        self.check_page(markup, assertions, scripts=SCRIPTS, bootstrap='', **kwargs)

    def test_missing_sections_and_malformed_cards_do_not_break_menu(self):
        self.run_page(MENU + '<section id="calendario"></section><article class="hall-result"></article><button data-copy-code="X">No feedback</button>', """
const toggle = document.querySelector('.nav-toggle');
toggle.click();
check(toggle.getAttribute('aria-expanded') === 'true', 'Menu unavailable without hero');
check(!document.querySelector('.calendar-event-list'), 'Incomplete calendar initialized');
check(typeof window.viewerState === 'undefined' && typeof window.updateHero === 'undefined', 'Leaked component state');
""")

    def test_menu_closes_on_link_outside_and_escape_without_duplicate_handlers(self):
        self.run_page(MENU, """
KimSite.initMobileNavigation();
const toggle = document.querySelector('.nav-toggle');
for (const action of ['link', 'outside', 'escape']) {
    toggle.click();
    check(toggle.getAttribute('aria-expanded') === 'true', 'Duplicate menu handler');
    if (action === 'link') document.querySelector('nav a').click();
    else if (action === 'outside') document.querySelector('#outside').click();
    else document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
    check(toggle.getAttribute('aria-expanded') === 'false', 'Menu did not close: ' + action);
    check(!document.documentElement.classList.contains('mobile-nav-open'), 'Menu class remained');
    if (action === 'escape') check(document.activeElement === toggle, 'Escape focus missing');
}
""")

    def test_dynamic_navigation_controls_are_explicit_and_idempotent(self):
        self.run_page('', """
const button = document.createElement('button');
button.dataset.navDirection = 'next';
document.body.append(button);
KimSite.enhanceNavigationControls(button);
const icon = button.querySelector('svg');
KimSite.enhanceNavigationControls(document);
check(icon && button.querySelector('svg') === icon, 'Control not initialized idempotently');
""")

    def test_copy_success_failure_and_focus(self):
        self.run_page('<button data-copy-code="KIM">Copy</button><span role="status"></span>', """
KimSite.initDiscountCodes();
const button = document.querySelector('[data-copy-code]');
const feedback = button.nextElementSibling;
button.focus(); button.click();
await new Promise(resolve => setTimeout(resolve, 10));
check(feedback.textContent === 'Copiado', 'Copy success missing');
check(document.activeElement === button && !document.querySelector('textarea'), 'Copy did not restore focus/cleanup');
window.copyWorks = false;
button.click();
await new Promise(resolve => setTimeout(resolve, 10));
check(feedback.textContent.includes('No se pudo copiar. Código: KIM'), 'Copy failure missing');
check(!button.hasAttribute('data-copied'), 'Stale success feedback');
""", setup="Object.defineProperty(navigator, 'clipboard', {value: undefined, configurable: true}); window.copyWorks = true; document.execCommand = () => window.copyWorks;")

    def test_broken_social_image_preserves_post_link(self):
        self.run_page('<a id="post" href="https://www.instagram.com/p/example/"><span>Fallback</span><img class="social-image" src="' + PIXEL + '"></a>', """
const image = document.querySelector('.social-image');
if (image) image.dispatchEvent(new Event('error'));
check(!document.querySelector('.social-image'), 'Broken image remained');
check(document.querySelector('#post').textContent === 'Fallback', 'Fallback/link removed');
""")

    def test_gallery_navigation_zoom_and_close_focus(self):
        markup = '<article class="hall-result"><h4>Example</h4><div class="hall-top"><span>2026</span></div><div class="hall-slides" hidden><img src="' + PIXEL + '" alt="First"><img src="' + PIXEL + '" alt="Second" hidden></div></article>'
        self.run_page(markup, """
KimSite.initHallGallery();
check(document.querySelectorAll('.hall-viewer').length === 1, 'Duplicate viewer');
const preview = document.querySelector('.hall-preview');
preview.click();
check(preview.getAttribute('aria-expanded') === 'true', 'Gallery did not open');
check(document.activeElement.classList.contains('hall-close'), 'Gallery focus missing');
document.querySelector('.hall-next').click();
check(document.querySelector('.hall-counter').textContent === '2 / 2', 'Next photo failed');
document.querySelector('.hall-gallery').dispatchEvent(new KeyboardEvent('keydown', {key:'ArrowLeft', bubbles:true}));
check(document.querySelector('.hall-counter').textContent === '1 / 2', 'Arrow navigation failed');
const expand = document.querySelector('.hall-expand'); expand.click();
const viewer = document.querySelector('.hall-viewer');
check(viewer.open, 'Viewer did not open');
const zoom = document.querySelector('.viewer-zoom'); zoom.click();
check(zoom.getAttribute('aria-pressed') === 'true', 'Zoom failed');
document.querySelector('.viewer-next').click();
check(zoom.getAttribute('aria-pressed') === 'false', 'Zoom not reset');
check(document.querySelector('.viewer-photo').alt === 'Second', 'Viewer photo mismatch');
check([...document.querySelectorAll('[data-nav-direction]')].every(b => b.querySelector('svg')), 'Dynamic arrows missing');
document.querySelector('.viewer-close').click();
await new Promise(resolve => setTimeout(resolve, 50));
check(!viewer.open && document.activeElement === expand, 'Viewer close focus missing');
document.querySelector('.hall-gallery').dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}));
check(document.activeElement === preview && preview.getAttribute('aria-expanded') === 'false', 'Gallery close focus missing');
""")

    def test_hero_initialization_with_and_without_navigation(self):
        self.run_page('<main><div class="hero-section" style="height:600px"></div><section class="about-section">About</section></main>', """
KimSite.initHero();
check(!document.documentElement.style.getPropertyValue('--hero-height').includes('NaN'), 'Invalid hero height');
check(document.documentElement.style.getPropertyValue('--portrait-opacity') === '1', 'Hero not initialized');
""", styles=':root { --nav-height: 60px; }')

    def test_complete_page_initializes_with_real_styles(self):
        page = (ROOT / 'index.html').read_text(encoding='utf-8')
        markup = re.search(r'<body>(.*)</body>', page, re.S).group(1)
        markup = re.sub(r'<script\b.*?</script>', '', markup, flags=re.S)
        markup = re.sub(r'<iframe\b.*?</iframe>', '', markup, flags=re.S)
        def local_image(match):
            tag = re.sub(r'\s+(?:src|srcset|data-full-src)="[^"]*"', '', match.group(0))
            return tag.replace('<img', '<img src="' + PIXEL + '"', 1)
        markup = re.sub(r'<img\b[^>]*>', local_image, markup)
        self.run_page(markup, """
check(document.querySelectorAll('.hall-result.has-gallery').length === 7, 'Full-page galleries missing');
check(document.querySelectorAll('.hall-viewer').length === 1, 'Full-page viewer missing/duplicated');
check(document.querySelectorAll('.calendar-event-list').length === 1, 'Full-page calendar missing');
check([...document.querySelectorAll('button[data-nav-direction]')].every(button => button.querySelector('svg')), 'Uninitialized controls');
check(document.querySelector('.hero-nav').inert, 'Hero navigation state changed');
check(document.querySelector('.calendar-days').children.length >= 28, 'Calendar grid missing');
""", styles=(ROOT / 'css/styles.css').read_text(encoding='utf-8'))

    def test_page_without_application_scripts_keeps_links_and_agenda(self):
        markup = re.search(r'<body>(.*)</body>', (ROOT / 'index.html').read_text(encoding='utf-8'), re.S).group(1)
        markup = re.sub(r'<script\b.*?</script>|<iframe\b.*?</iframe>', '', markup, flags=re.S)
        markup = re.sub(r'<img\b[^>]*>', '', markup)
        self.check_page(markup, """
const nav = document.querySelector('.hero-nav');
const links = [...nav.querySelectorAll('.nav-links a')];
check(!nav.inert && getComputedStyle(nav).opacity === '1', 'Static navigation inaccessible');
check(getComputedStyle(document.querySelector('.nav-toggle')).display === 'none', 'Dead menu button visible');
check(links.every(a => a.getBoundingClientRect().height > 0), 'Static links hidden');
links[1].focus();
check(document.activeElement === links[1], 'Static link cannot receive focus');
check(getComputedStyle(document.querySelector('.hero')).position !== 'fixed', 'Cover blocks content');
check(getComputedStyle(document.querySelector('.calendar-panel')).display === 'none', 'Dead calendar controls visible');
check([...document.querySelectorAll('.calendar-event')].every(e => !e.hidden && e.getBoundingClientRect().height > 0), 'Static agenda hidden');
""", scripts=[], bootstrap='', styles=(ROOT / 'css/styles.css').read_text(encoding='utf-8'))

    def test_missing_component_script_does_not_stop_other_components(self):
        self.check_page(MENU, """
document.querySelector('.nav-toggle').click();
check(document.querySelector('.nav-toggle').getAttribute('aria-expanded') === 'true', 'Missing hero script blocked menu');
""", scripts=['mobile-navigation', 'main'], bootstrap='')
