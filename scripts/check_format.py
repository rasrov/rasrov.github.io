"""Check repository text hygiene and Python formatting; --fix applies formatting only."""

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ('scripts', 'tests', 'css', 'js', 'data', 'docs', 'img', '.github')
EXTENSIONS = {
    '.py',
    '.js',
    '.mjs',
    '.css',
    '.html',
    '.json',
    '.yml',
    '.yaml',
    '.md',
    '.txt',
    '.toml',
    '.xml',
    '.svg',
    '.ps1',
}
CONFIG_FILES = {'.editorconfig', '.gitattributes', '.gitignore', 'CNAME'}


def text_files(root):
    root = Path(root)
    candidates = list(root.iterdir())
    for name in DIRECTORIES:
        directory = root / name
        if directory.is_dir():
            candidates.extend(directory.rglob('*'))
    return sorted(
        path
        for path in candidates
        if path.is_file()
        and not path.is_symlink()
        and (path.suffix in EXTENSIONS or path.name in CONFIG_FILES)
        and '__pycache__' not in path.parts
    )


def normalize(data, markdown=False):
    text = data.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    if not markdown:
        text = '\n'.join(line.rstrip(' \t') for line in text.split('\n'))
    if text and not text.endswith('\n'):
        text += '\n'
    return text.encode('utf-8')


def check_text(root=ROOT, fix=False):
    errors = []
    for path in text_files(root):
        location = path.relative_to(root).as_posix()
        data = path.read_bytes()
        try:
            expected = normalize(data, markdown=path.suffix == '.md')
        except UnicodeDecodeError:
            errors.append(f'{location}: invalid UTF-8 (convert encoding manually)')
            continue
        if data != expected:
            if fix:
                path.write_bytes(expected)
            else:
                errors.append(
                    f'{location}: expected UTF-8 without BOM, LF, final newline and no trailing whitespace (Markdown spaces are preserved)'
                )
        for number, line in enumerate(expected.decode('utf-8').splitlines(), 1):
            leading = line[: len(line) - len(line.lstrip(' \t'))]
            if '\t' in leading:
                errors.append(f'{location}:{number}: use spaces for indentation')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fix', action='store_true', help='Normalize text files and format Python')
    args = parser.parse_args()
    errors = check_text(ROOT, fix=args.fix)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        raise SystemExit(1)
    command = [sys.executable, '-m', 'ruff', 'format']
    if not args.fix:
        command.append('--check')
    result = subprocess.run([*command, 'scripts', 'tests'], cwd=ROOT)
    if result.returncode:
        print(
            'Install requirements-dev.txt, then run python scripts/check_format.py --fix.',
            file=sys.stderr,
        )
        raise SystemExit(result.returncode)
    print('Text conventions and Python formatting valid.')


if __name__ == '__main__':
    main()
