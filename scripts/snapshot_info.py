"""Show snapshot provenance and compare local downloads without network access."""

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from .validation import read_json
    from .validate_data import validate_metadata
else:
    from validation import read_json
    from validate_data import validate_metadata

ROOT = Path(__file__).resolve().parents[1]


def describe(path, provider):
    snapshot = read_json(path)
    if not isinstance(snapshot, dict):
        raise ValueError(f'{path}: expected an object')
    validate_metadata(snapshot, str(path), provider)
    metadata = snapshot.get('metadata', {'source': 'legacy-cache', 'fetched_at': None})
    digest = hashlib.sha256(
        json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode('utf-8')
    ).hexdigest()
    print(
        f'{path.name}: source={metadata["source"]}, fetched_at={metadata["fetched_at"] or "unknown"}, sha256={digest}'
    )
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--compare-dir',
        type=Path,
        help='Directory containing downloaded youtube.json and instagram.json',
    )
    args = parser.parse_args()
    for name, provider in (
        ('youtube', 'youtube-data-api'),
        ('instagram', 'meta-business-discovery'),
    ):
        print('Local:')
        local = describe(ROOT / 'data' / (name + '.json'), provider)
        if args.compare_dir:
            print('Comparison:')
            remote = describe(args.compare_dir / (name + '.json'), provider)
            print('Same snapshot' if local == remote else 'Different snapshots')


if __name__ == '__main__':
    main()
