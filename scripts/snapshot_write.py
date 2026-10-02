"""Stage related outputs and restore their original bytes on write failure."""

import json
import os
from pathlib import Path
import shutil


class RecoveryRequiredError(RuntimeError):
    pass


def write_outputs(root, outputs, *, image_assets=False):
    root = Path(root).resolve()
    allowed = {'index.html', 'data/youtube.json', 'data/instagram.json', 'data/competitions.json'}
    if image_assets:
        allowed |= {'img/image-manifest.json', 'data/competition-logos.json'}
    targets = []
    for name, content in outputs.items():
        asset = Path(name)
        generated_image = (
            image_assets
            and asset.as_posix() == name
            and asset.parts[:1] == ('img',)
            and 'optimized' in asset.parts
            and asset.suffix == '.webp'
            and '..' not in asset.parts
        )
        if (name not in allowed and not generated_image) or not isinstance(
            content, (str, bytes) if image_assets else str
        ):
            raise ValueError('Unexpected snapshot output')
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('Snapshot output must stay inside the project')
        if path.exists() and not path.is_file():
            raise ValueError('Snapshot output is not a file')
        targets.append((name, path, content))
    staging = root / '.snapshot-update'
    try:
        staging.mkdir()
    except FileExistsError:
        raise RecoveryRequiredError(
            f'Update already active or interrupted. Inspect {staging} before retrying.'
        ) from None
    installed = []
    cleanup = False
    try:
        records = []
        for number, (name, path, content) in enumerate(targets):
            backup = staging / f'{number}.previous'
            if path.exists():
                backup.write_bytes(path.read_bytes())
            prepared = staging / f'{number}.next'
            prepared.write_bytes(content.encode('utf-8') if isinstance(content, str) else content)
            records.append({'path': name, 'existed': path.exists(), 'backup': backup.name})
        (staging / 'recovery.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
        for number, (_, path, _) in enumerate(targets):
            path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging / f'{number}.next', path)
            installed.append(number)
        cleanup = True
    except Exception as original:
        failures = []
        for number in reversed(installed):
            path = targets[number][1]
            backup = staging / f'{number}.previous'
            try:
                if backup.exists():
                    # Keep the backup intact if restoration also fails.
                    restore = staging / f'{number}.restore'
                    restore.write_bytes(backup.read_bytes())
                    os.replace(restore, path)
                else:
                    path.unlink()
            except OSError:
                failures.append(number)
        if failures:
            raise RecoveryRequiredError(
                f'Automatic restoration failed. Recover original files using {staging}/recovery.json.'
            ) from original
        cleanup = True
        raise
    finally:
        # A crash or failed rollback leaves the journal/backups for manual recovery.
        if cleanup:
            if staging.parent != root or staging.name != '.snapshot-update' or staging.is_symlink():
                raise RecoveryRequiredError('Unexpected recovery directory; cleanup aborted')
            shutil.rmtree(staging)
