"""Check public HTML/CSS/static JS paths, the image inventory and sitemap offline."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

if __package__:
    from .validation import local_file, read_json, require
else:
    from validation import local_file, read_json, require

ROOT = Path(__file__).resolve().parents[1]


def srcset_urls(value):
    # URLs extend to whitespace (data URLs can contain commas); descriptors end at a comma.
    position = 0
    while position < len(value):
        while position < len(value) and (value[position].isspace() or value[position] == ','):
            position += 1
        start = position
        while position < len(value) and not value[position].isspace():
            position += 1
        url = value[start:position]
        if not url:
            break
        yield url.rstrip(',')
        if not url.endswith(','):
            while position < len(value) and value[position] != ',':
                position += 1


class Document(HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.name = name
        self.ids = set()
        self.references = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        location = f'{self.name}:{self.getpos()[0]}'
        if attrs.get('id'):
            require(attrs['id'] not in self.ids, location, f'duplicate HTML id {attrs["id"]!r}')
            self.ids.add(attrs['id'])
        for key in ('src', 'href', 'poster', 'data-full-src', 'data-logo'):
            if attrs.get(key):
                self.references.append((attrs[key], location + '.' + key))
        if attrs.get('srcset'):
            for url in srcset_urls(attrs['srcset']):
                self.references.append((url, location + '.srcset'))
        if tag == 'meta' and attrs.get('property') == 'og:image' and attrs.get('content'):
            self.references.append((attrs['content'], location + '.og:image'))
        if tag == 'link' and 'canonical' in attrs.get('rel', '').split():
            self.canonicals.append(attrs.get('href', ''))

    handle_startendtag = handle_starttag


def validate_resources(root=ROOT):
    root = Path(root).resolve()
    documents = {}
    for path in sorted(root.rglob('*.html')):
        name = path.relative_to(root).as_posix()
        document = Document(name)
        document.feed(path.read_text(encoding='utf-8'))
        documents[path] = document
    index = documents.get(root / 'index.html')
    require(index is not None and len(index.canonicals) == 1, 'index.html.canonical', 'expected one canonical URL')
    canonical = urlsplit(index.canonicals[0])
    require(canonical.scheme == 'https' and bool(canonical.netloc) and canonical.path == '/' and not canonical.query and not canonical.fragment,
            'index.html.canonical', 'expected an HTTPS site-root URL')
    origin = canonical.netloc

    def reference(value, source, location, page_url=False):
        url = urlsplit(value)
        if url.netloc and url.netloc != origin:
            require(not page_url, location, 'sitemap page is outside the canonical origin')
            return  # Remote resources are not fetched by offline validation.
        if url.scheme and url.scheme not in ('http', 'https'):
            return
        path = url.path or ('/' if url.netloc else Path(source).name)
        target = local_file(root, path, source, location)
        if url.fragment and target.suffix.lower() == '.html':
            require(target in documents and unquote(url.fragment) in documents[target].ids,
                    location, f'missing HTML fragment {url.fragment!r}')

    for path, document in documents.items():
        for value, location in document.references:
            reference(value, path.relative_to(root).as_posix(), location)
    for path in sorted((root / 'css').rglob('*.css')):
        name = path.relative_to(root).as_posix()
        css = re.sub(r'/\*.*?\*/', '', path.read_text(encoding='utf-8'), flags=re.S)
        urls = re.findall(r"url\(\s*['\"]?([^'\")]+?)['\"]?\s*\)", css)
        urls += re.findall(r"@import\s+['\"]([^'\"]+)['\"]", css)
        for value in urls:
            if not value.startswith('#'):
                reference(value, name, name + '.url')
    for path in sorted((root / 'js').rglob('*.js')):
        for value in re.findall(r"['\"]((?:img|css|js)/[^'\"]+)['\"]", path.read_text(encoding='utf-8')):
            reference(value, 'index.html', path.relative_to(root).as_posix() + '.static-path')
    manifest_path = root / 'img/image-manifest.json'
    manifest = read_json(manifest_path)
    require(isinstance(manifest, dict), 'img/image-manifest.json', 'expected an object')
    variants_seen = set()
    for original, entry in manifest.items():
        loc = f'img/image-manifest.json[{original}]'
        require(isinstance(entry, dict) and isinstance(entry.get('variants'), list), loc, 'expected dimensions and variants array')
        records = [(original, entry)]
        for number, variant in enumerate(entry['variants']):
            vloc = f'{loc}.variants[{number}]'
            require(isinstance(variant, dict) and isinstance(variant.get('src'), str), vloc, 'expected a variant with src')
            require(variant['src'] not in variants_seen, vloc + '.src', 'duplicate variant path')
            variants_seen.add(variant['src'])
            records.append((variant['src'], variant))
        for value, metadata in records:
            mloc = loc + ':' + value
            require(value.startswith('img/'), mloc, 'expected an img/ path')
            asset = local_file(root, value, 'index.html', mloc)
            for field in ('width', 'height', 'bytes'):
                require(type(metadata.get(field)) is int and metadata[field] > 0, mloc + '.' + field, 'expected a positive integer')
            require(asset.stat().st_size == metadata['bytes'], mloc + '.bytes', 'file size differs from inventory')
    try:
        sitemap = ET.parse(root / 'sitemap.xml').getroot()
    except (ET.ParseError, OSError):
        raise ValueError('sitemap.xml: invalid or unreadable XML') from None
    namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    image_namespace = '{http://www.google.com/schemas/sitemap-image/1.1}'
    require(sitemap.tag == namespace + 'urlset', 'sitemap.xml', 'expected a namespaced urlset')
    pages = sitemap.findall(namespace + 'url')
    require(bool(pages), 'sitemap.xml', 'expected at least one URL')
    seen = set()
    for number, page in enumerate(pages):
        loc = f'sitemap.xml.url[{number}]'
        value = page.findtext(namespace + 'loc', '')
        require(urlsplit(value).scheme == 'https' and bool(urlsplit(value).netloc), loc, 'expected absolute HTTPS URL')
        require(value not in seen, loc, 'duplicate page URL')
        seen.add(value)
        reference(value, 'index.html', loc, page_url=True)
        for image in page.findall(image_namespace + 'image'):
            value = image.findtext(image_namespace + 'loc', '')
            require(urlsplit(value).scheme == 'https' and bool(urlsplit(value).netloc), loc + '.image', 'expected absolute HTTPS image URL')
            reference(value, 'index.html', loc + '.image')
    return len(documents)


if __name__ == '__main__':
    validate_resources(ROOT / '_site')
    print('Public resource references valid.')
