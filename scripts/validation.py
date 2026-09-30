"""Small shared validation primitives with file/field diagnostics."""
import json
import os
from pathlib import Path
from urllib.parse import unquote, urlsplit


def require(condition, location, message):
    if not condition:
        raise ValueError(f'{location}: {message}')


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, path, f'duplicate JSON key {key!r}')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError(f'{path}: non-finite numbers are not valid JSON')

    try:
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique, parse_constant=invalid_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f'{path}: invalid or unreadable JSON ({type(error).__name__})') from None


def local_file(root, reference, source, location):
    """Resolve a relative public resource; enforce containment and exact casing."""
    root = Path(root).resolve()
    url = urlsplit(reference)
    require(not url.scheme and not url.netloc, location, 'expected a local path')
    decoded = unquote(url.path)
    require('\\' not in decoded, location, 'use forward slashes')
    base = root if decoded.startswith('/') else (root / source).parent
    target = Path(os.path.abspath(base / decoded.lstrip('/')))
    require(target.is_relative_to(root) and target.resolve().is_relative_to(root), location, 'path escapes site root')
    if target.is_dir():
        target = target / 'index.html'
    require(target.is_file(), location, f'missing file {reference!r}')
    current = root
    for part in target.relative_to(root).parts:
        require(part in {entry.name for entry in current.iterdir()}, location, f'filename casing mismatch: {reference!r}')
        current = current / part
    return target
