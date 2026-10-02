"""Profile actual calendar data/CSS offline; viewport and CPU emulation are not a phone."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

if __package__:
    from .build import render_page
else:
    from build import render_page

ROOT = Path(__file__).resolve().parents[1]


def instrument(source, before, after):
    if source.count(before) != 1:
        raise ValueError('Profiling hook no longer matches source; review instrumentation')
    return source.replace(before, after)


def profile(browser, width, cpu):
    page = render_page(ROOT)
    page = page.replace('<head>', '<head><base href="' + ROOT.as_uri() + '/">')
    # Preserve iframe geometry without loading remote players.
    page = re.sub(r'(<iframe\b[^>]*\bsrc=)["\'][^"\']*["\']', r'\1"about:blank"', page)
    probe = '<script>window.profileData={agenda:[],hero:[],errors:[]};addEventListener("error",e=>profileData.errors.push(e.message));</script>'
    page = page.replace('</head>', probe + '</head>')
    for name in ('calendar', 'hero'):
        source = (ROOT / 'js' / (name + '.js')).read_text(encoding='utf-8')
        if name == 'calendar':
            source = instrument(
                source,
                'function sizeAgenda() {',
                'function sizeAgenda() { const measuredAt = performance.now();',
            )
            marker = 'eventList.style.minHeight = `${Math.ceil(height) * Math.min(pageSize, monthEvents.length)}px`;'
            source = instrument(
                source,
                marker,
                marker
                + '\nprofileData.agenda.push({ms:performance.now()-measuredAt,count:monthEvents.length,width});',
            )
        else:
            source = instrument(
                source,
                'function updateHero() {',
                'function updateHero() { const measuredAt = performance.now();',
            )
            source = instrument(
                source,
                '            framePending = false;',
                '            profileData.hero.push(performance.now()-measuredAt);\n            framePending = false;',
            )
        page, count = re.subn(
            r'<script src="js/' + name + r'\.js"></script>',
            lambda _: '<script>' + source + '</script>',
            page,
        )
        if count != 1:
            raise ValueError('Expected one script tag for ' + name)
    page = page.replace(
        '</body>',
        '<script>'
        + (ROOT / 'scripts/profile_calendar.mjs').read_text(encoding='utf-8')
        + '</script></body>',
    )
    with tempfile.TemporaryDirectory(prefix='calendar-profile-') as folder:
        target = Path(folder) / 'profile.html'
        target.write_text(page, encoding='utf-8', newline='\n')
        result = subprocess.run(
            [
                'node',
                str(ROOT / 'tests/browser_frames.mjs'),
                target.as_uri(),
                str(Path(folder) / 'browser'),
                'runCalendarProfile',
                str(width),
                str(cpu),
            ],
            env={**os.environ, 'BROWSER_BIN': browser},
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120,
            check=True,
        )
    report = json.loads(result.stdout)
    report['cpu_factor'] = cpu
    report['physical_mobile'] = False
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', default=os.environ.get('BROWSER_BIN'))
    parser.add_argument('--width', type=int, default=390)
    parser.add_argument('--cpu', type=float, default=1)
    args = parser.parse_args()
    if not args.browser or not Path(args.browser).is_file() or args.width <= 0 or args.cpu < 1:
        parser.error('Provide a browser executable, positive width and CPU factor >= 1')
    print(json.dumps(profile(args.browser, args.width, args.cpu), indent=2))


if __name__ == '__main__':
    main()
