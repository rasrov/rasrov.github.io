"""Build a public _site/ from local snapshots without changing source files."""
from pathlib import Path
import shutil
import tempfile

if __package__:
    from . import render_calendar, update_instagram, update_youtube
    from .validate_data import validate_data
    from .validate_resources import validate_resources
else:
    from validate_data import validate_data
    from validate_resources import validate_resources
    import render_calendar
    import update_instagram
    import update_youtube

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = ('index.html', 'robots.txt', 'sitemap.xml', 'favicon.ico')
PUBLIC_DIRECTORIES = ('css', 'js', 'img', 'data')


def render_page(root):
    snapshots = validate_data(root)

    def read(name):
        return snapshots[name]

    page = (root / 'index.html').read_text(encoding='utf-8')
    page = update_youtube.replace_cards(page, read('youtube.json')['videos'])
    page = update_instagram.replace_posts(page, read('instagram.json')['posts'])
    calendar = render_calendar.render(read('competitions.json')['events'],
                                      read('competition-participation.json'),
                                      read('competition-logos.json'), root=root)
    return render_calendar.replace_calendar(page, calendar)


def build(root=ROOT):
    root = Path(root).resolve()
    output = root / '_site'
    if (root / '.snapshot-update').exists():
        raise ValueError('Snapshot update active or interrupted; inspect .snapshot-update before building')
    if output.is_symlink() or output.is_junction() or (output.exists() and not output.is_dir()):
        raise ValueError('_site must be an ordinary build directory')
    page = render_page(root)
    staging = Path(tempfile.mkdtemp(prefix='.site-build-', dir=root)).resolve()
    # All moves and recursive cleanup are confined to this build's root.
    if staging.parent != root or not staging.name.startswith('.site-build-'):
        raise ValueError('Invalid build staging directory')
    public = staging / 'public'
    backup = staging / 'previous'
    public.mkdir()
    try:
        for name in PUBLIC_FILES:
            shutil.copy2(root / name, public / name)
        for name in PUBLIC_DIRECTORIES:
            shutil.copytree(root / name, public / name)
        for path in root.glob('google*.html'):
            shutil.copy2(path, public / path.name)
        if (root / 'CNAME').is_file():
            shutil.copy2(root / 'CNAME', public / 'CNAME')
        (public / 'index.html').write_text(page, encoding='utf-8', newline='\n')
        (public / '.nojekyll').touch()
        validate_resources(public)
        if output.exists():
            output.rename(backup)
        try:
            public.rename(output)
        except OSError:
            if backup.exists():
                backup.rename(output)
            raise
    finally:
        # If rollback itself failed, retain the old output for manual recovery.
        if not backup.exists() or output.exists():
            shutil.rmtree(staging)
    return output


if __name__ == '__main__':
    print(f'Built {build()} from local snapshots; source files unchanged.')
