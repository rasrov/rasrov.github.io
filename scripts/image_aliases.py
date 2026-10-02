"""Preserve published image URLs in the build without duplicating source assets."""

from pathlib import Path
import shutil

if __package__:
    from .validation import local_file, read_json, require
else:
    from validation import local_file, read_json, require


def materialize_image_aliases(root):
    root = Path(root).resolve()
    manifest = root / 'img/image-aliases.json'
    if not manifest.exists():
        return 0
    aliases = read_json(manifest)
    require(isinstance(aliases, dict), manifest, 'expected an old-to-new path mapping')
    prepared = []
    for old, new in aliases.items():
        for name in (old, new):
            require(isinstance(name, str), manifest, 'expected string paths')
            path = Path(name)
            require(
                path.as_posix() == name
                and path.parts[:1] == ('img',)
                and '..' not in path.parts
                and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.svg'},
                manifest,
                'expected an image path under img/',
            )
        require(new not in aliases, manifest, 'alias chains and cycles are forbidden')
        source = local_file(root, new, 'index.html', manifest)
        target = root / old
        require(
            target.resolve().is_relative_to(root) and not target.is_symlink(),
            manifest,
            'alias escapes build root',
        )
        require(not target.exists(), manifest, f'alias collides with source asset: {old}')
        prepared.append((source, target))
    for source, target in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return len(prepared)
