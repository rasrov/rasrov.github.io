"""Generate local WebP variants on demand, preserving originals and existing good variants."""

import argparse
from copy import deepcopy
import hashlib
from html import escape, unescape
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import tempfile

if __package__:
    from . import build, render_calendar
    from .snapshot_write import write_outputs
    from .validation import read_json, local_file
    from .validate_resources import validate_resources
else:
    import build, render_calendar
    from snapshot_write import write_outputs
    from validation import read_json, local_file
    from validate_resources import validate_resources

ROOT = Path(__file__).resolve().parents[1]
RASTER = {'.png', '.jpg', '.jpeg', '.webp'}
IMG = re.compile(r'<img\b[^>]*>', re.I)
ATTR = re.compile(r"""\s+([\w-]+)\s*=\s*(["'])(.*?)\2""", re.S)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_path(root, name):
    path = Path(name)
    if (
        path.as_posix() != name
        or path.parts[:1] != ('img',)
        or '..' in path.parts
        or 'optimized' in path.parts
        or path.suffix.lower() not in RASTER
    ):
        raise ValueError(f'Expected an original PNG/JPEG/WebP under img/: {name}')
    return local_file(root, name, 'index.html', name)


def recipe(name, entry, width):
    from PIL import __version__, features

    logo = '/calendar/' in name or '/sponsors/' in name or 'logo' in Path(name).stem
    sizes = [v['width'] for v in entry.get('variants', [])] or (
        [160, 320, 640] if logo else [480, 960, 1440]
    )
    sizes = sorted(set(min(value, width) for value in sizes))
    return {
        'version': 1,
        'widths': sizes,
        'quality': 82,
        'method': 6,
        'lossless': logo,
        'resample': 'lanczos',
        'pillow': __version__,
        'webp': features.version('webp'),
    }


def destination(name, width):
    path = Path(name)
    # Calendar paths remain under img/calendar/, as required by its logo contract.
    directory = (
        Path('img/calendar/optimized')
        if path.parent == Path('img/calendar')
        else Path('img/optimized') / path.parent.relative_to('img')
    )
    return (directory / f'{path.stem}-{path.suffix[1:].lower()}-{width}w.webp').as_posix()


def rewrite_images(page, manifest, previous=None):
    lookup = {key: key for key in manifest}
    for key, entry in manifest.items():
        lookup.update({variant['src']: key for variant in entry['variants']})

    for key, entry in (previous or {}).items():
        if key in manifest:
            lookup.update({variant['src']: key for variant in entry['variants']})

    def rewrite(match):
        tag = match.group(0)
        attrs = {m[1].lower(): unescape(m[3]) for m in ATTR.finditer(tag)}
        original = lookup.get(attrs.get('src', ''))
        if original is None:
            return tag
        entry = manifest[original]
        variants = sorted(entry['variants'], key=lambda v: v['width'])
        if not variants:
            return tag
        chosen = next((v for v in variants if v['src'] == attrs.get('src')), variants[-1])
        values = {
            'src': chosen['src'],
            'srcset': ', '.join(f'{v["src"]} {v["width"]}w' for v in variants),
            'width': str(entry['width']),
            'height': str(entry['height']),
        }
        if 'sizes' not in attrs:
            values['sizes'] = '100vw'

        def replace_attr(m):
            key = m[1].lower()
            if key not in values:
                return m[0]
            return f' {m[1]}="{escape(values[key], quote=True)}"'

        tag = ATTR.sub(replace_attr, tag)
        addition = ''.join(
            f' {key}="{escape(value, quote=True)}"'
            for key, value in values.items()
            if key not in attrs
        )
        end = '/>' if tag.endswith('/>') else '>'
        return tag[: -len(end)] + addition + end

    return IMG.sub(rewrite, page)


def plan(root=ROOT, source=None, force=False):
    from PIL import Image, ImageOps

    root = Path(root).resolve()
    manifest = read_json(root / 'img/image-manifest.json')
    original_manifest = deepcopy(manifest)
    page = (root / 'index.html').read_text(encoding='utf-8')
    logos = read_json(root / 'data/competition-logos.json')
    names = set(manifest)
    # Discover only images already connected to the site, not unused files/favicons.
    names.update(logos.values())
    for match in IMG.finditer(page):
        attrs = {m[1].lower(): unescape(m[3]) for m in ATTR.finditer(match[0])}
        names.add(attrs.get('src', ''))
    names = {
        name
        for name in names
        if name.startswith('img/')
        and 'optimized' not in Path(name).parts
        and Path(name).suffix.lower() in RASTER
    }
    if source:
        source_path(root, source)
        names = {source}
    outputs, report = {}, {'generated': [], 'adopted': [], 'unchanged': []}
    for name in sorted(names):
        path = source_path(root, name)
        raw = path.read_bytes()
        entry = deepcopy(manifest.get(name, {}))
        with Image.open(BytesIO(raw)) as opened:
            if getattr(opened, 'is_animated', False):
                raise ValueError(f'Animated images require a separate policy: {name}')
            image = ImageOps.exif_transpose(opened)
            icc = image.info.get('icc_profile')
            if image.mode == 'CMYK' and icc:
                from PIL import ImageCms

                target_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB'))
                image = ImageCms.profileToProfile(
                    image, ImageCms.ImageCmsProfile(BytesIO(icc)), target_profile, outputMode='RGB'
                )
                icc = target_profile.tobytes()
            alpha = 'A' in image.getbands() or 'transparency' in image.info
            image = image.convert('RGBA' if alpha else 'RGB')
        spec = recipe(name, entry, image.width)
        optimization = entry.get('optimization', {})
        valid = bool(entry.get('variants')) and (
            entry.get('width'),
            entry.get('height'),
            entry.get('bytes'),
        ) == (image.width, image.height, len(raw))
        hashes = {}
        for variant in entry.get('variants', []):
            try:
                data = local_file(root, variant['src'], 'index.html', name).read_bytes()
                hashes[variant['src']] = digest(data)
                with Image.open(BytesIO(data)) as candidate:
                    valid = (
                        valid
                        and candidate.size == (variant['width'], variant['height'])
                        and len(data) == variant['bytes']
                    )
            except (ValueError, OSError):
                valid = False
        unchanged = (
            valid
            and optimization.get('source_sha256') == digest(raw)
            and optimization.get('variants_sha256') == hashes
            and optimization.get('recipe') == spec
        )
        if unchanged and not force:
            report['unchanged'].append(name)
            continue
        if valid and not optimization and not force:
            # First run adopts legacy files; their original encoding settings are unknown.
            report['adopted'].append(name)
            mode = 'adopted-existing'
        else:
            report['generated'].append(name)
            mode = 'generated'
            previous_paths = {v['width']: v['src'] for v in entry.get('variants', [])}
            variants, hashes = [], {}
            for width in spec['widths']:
                height = max(1, round(image.height * width / image.width))
                resized = image.resize((width, height), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                resized.save(
                    buffer,
                    'WEBP',
                    quality=spec['quality'],
                    method=spec['method'],
                    lossless=spec['lossless'],
                    exact=True,
                    icc_profile=icc or b'',
                )
                target = previous_paths.get(width, destination(name, width))
                if (
                    not target.startswith('img/')
                    or 'optimized' not in Path(target).parts
                    or '..' in Path(target).parts
                    or not target.endswith('.webp')
                ):
                    raise ValueError(f'Unsafe variant output: {target}')
                data = buffer.getvalue()
                if target in outputs:
                    raise ValueError(f'Variant collision: {target}')
                outputs[target] = data
                hashes[target] = digest(data)
                variants.append(
                    {'src': target, 'width': width, 'height': height, 'bytes': len(data)}
                )
            entry = {
                'width': image.width,
                'height': image.height,
                'bytes': len(raw),
                'variants': variants,
            }
        entry['optimization'] = {
            'source_sha256': digest(raw),
            'variants_sha256': hashes,
            'recipe': spec,
            'mode': mode,
        }
        manifest[name] = entry
    updated = set(report['adopted'] + report['generated'])
    if not updated:
        return {}, report
    # Keep full-resolution gallery links and sitemap originals unchanged.
    page = rewrite_images(page, {name: manifest[name] for name in updated}, original_manifest)
    originals = {
        v['src']: name for name, entry in original_manifest.items() for v in entry['variants']
    }
    for key, value in logos.items():
        original = originals.get(value, value)
        if original in updated:
            variants = manifest[original]['variants']
            logos[key] = next(
                (v['src'] for v in variants if v['width'] >= 320), variants[-1]['src']
            )
    outputs['img/image-manifest.json'] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    ).encode()
    outputs['data/competition-logos.json'] = (
        json.dumps(logos, ensure_ascii=False, indent=2) + '\n'
    ).encode()
    outputs['index.html'] = page.encode()
    # Validate all generated resources in isolation before installing any file.
    with tempfile.TemporaryDirectory(prefix='image-validation-') as folder:
        staged = Path(folder)
        for directory in build.PUBLIC_DIRECTORIES:
            shutil.copytree(root / directory, staged / directory)
        for name in build.PUBLIC_FILES:
            shutil.copy2(root / name, staged / name)
        for name, data in outputs.items():
            path = staged / name
            if not path.resolve().is_relative_to(staged):
                raise ValueError('Output escaped staging directory')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        calendar = render_calendar.render(
            read_json(staged / 'data/competitions.json')['events'],
            read_json(staged / 'data/competition-participation.json'),
            logos,
            root=staged,
        )
        outputs['index.html'] = render_calendar.replace_calendar(page, calendar).encode()
        (staged / 'index.html').write_bytes(outputs['index.html'])
        build.render_page(staged)  # Includes the shared JSON contracts.
        validate_resources(staged)
    return {
        name: data
        for name, data in outputs.items()
        if not (root / name).exists() or (root / name).read_bytes() != data
    }, report


def optimize(root=ROOT, source=None, force=False, dry_run=False):
    outputs, report = plan(root, source, force)
    if outputs and not dry_run:
        write_outputs(root, outputs, image_assets=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', help='Optional original path under img/')
    parser.add_argument('--force', action='store_true', help='Regenerate even intact variants')
    parser.add_argument(
        '--dry-run', action='store_true', help='Prepare and validate without installing outputs'
    )
    args = parser.parse_args()
    print(
        json.dumps(optimize(source=args.source, force=args.force, dry_run=args.dry_run), indent=2)
    )


if __name__ == '__main__':
    main()
