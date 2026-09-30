"""Validate locally without credentials or edits to tracked source files."""
import argparse
import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

if __package__:
    from .generated_regions import replace_region
else:
    from generated_regions import replace_region

ROOT = Path(__file__).resolve().parents[1]


def run(*command, cwd=ROOT, env=None):
    subprocess.run(command, cwd=cwd, env=env, check=True)


def manual_content(page):
    for name in ('youtube', 'instagram', 'calendar'):
        page = replace_region(page, name, '')
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', action='store_true', help='Require Chrome/Edge calendar regression tests')
    args = parser.parse_args()
    for directory in ('scripts', 'tests'):
        for path in sorted((ROOT / directory).rglob('*.py')):
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Node.js is required for JavaScript syntax checks')
    for path in sorted((ROOT / 'js').glob('*.js')):
        run(node, '--check', str(path))
    env = os.environ.copy()
    if args.browser:
        candidates = [env.get('BROWSER_BIN'), shutil.which('google-chrome'), shutil.which('chromium'),
                      shutil.which('chromium-browser'),
                      r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                      r'C:\Program Files\Google\Chrome\Application\chrome.exe']
        browser = next((str(p) for p in candidates if p and Path(p).is_file()), None)
        if not browser:
            raise RuntimeError('Chrome/Edge not found. Set BROWSER_BIN to its executable path.')
        env['BROWSER_BIN'] = browser
    run(sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v', env=env)
    with tempfile.TemporaryDirectory(prefix='website-validation-') as folder:
        target = Path(folder)
        for directory in ('scripts', 'data', 'css', 'js', 'img'):
            shutil.copytree(ROOT / directory, target / directory, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('index.html', 'robots.txt', 'sitemap.xml', 'favicon.ico'):
            shutil.copy2(ROOT / name, target / name)
        source_paths = [target / 'index.html', *sorted((target / 'data').glob('*.json'))]
        source_bytes = {path: path.read_bytes() for path in source_paths}
        original = manual_content((target / 'index.html').read_text(encoding='utf-8'))
        previous = None
        for _ in range(2):
            run(sys.executable, '-B', 'scripts/build.py', cwd=target)
            output = (target / '_site/index.html').read_text(encoding='utf-8')
            if manual_content(output) != original:
                raise ValueError('Offline build changed manually authored HTML')
            if previous is not None and output != previous:
                raise ValueError('Offline build is not idempotent')
            if any(path.read_bytes() != content for path, content in source_bytes.items()):
                raise ValueError('Build modified source HTML or snapshots')
            previous = output
    print('Validation passed; source HTML and snapshots were not modified.')


if __name__ == '__main__':
    main()
