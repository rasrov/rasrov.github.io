"""Render three public Instagram posts via Facebook Business Discovery."""
import argparse
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OWN_IG_ID = "17841401870042081"
TARGET = "kim_angel"
VERSION = "v26.0"
START = "<!-- instagram:generated:start -->"
END = "<!-- instagram:generated:end -->"

def parse_date(value):
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ValueError("Timestamp without timezone")
    return date

def select_posts(items):
    unique = {}
    for item in items:
        if item.get("media_type") not in ("IMAGE", "VIDEO", "CAROUSEL_ALBUM"):
            continue
        post_id = str(item.get("id", ""))
        if not post_id.isdigit():
            raise ValueError("Invalid media ID")
        link = urlparse(item.get("permalink", ""))
        if (link.scheme != "https" or link.netloc != "www.instagram.com"
                or not re.fullmatch(r"/(?:p|reel)/[A-Za-z0-9_-]+/", link.path)
                or link.query or link.fragment):
            raise ValueError("Unexpected Instagram permalink")
        date = parse_date(item["timestamp"])
        if date > datetime.now(timezone.utc):
            continue
        unique[post_id] = {key: item[key] for key in ("id", "permalink", "media_type", "timestamp")}
    selected = sorted(unique.values(), key=lambda p: (parse_date(p["timestamp"]), str(p["id"])), reverse=True)[:3]
    if len(selected) != 3:
        raise ValueError("Fewer than three valid posts; published site will not be replaced")
    return selected

def fetch_posts(token):
    # Read a larger recent batch and sort by timestamp rather than visual pinning.
    fields = "business_discovery.username(" + TARGET + "){username,media.limit(50){id,permalink,media_type,timestamp}}"
    url = f"https://graph.facebook.com/{VERSION}/{OWN_IG_ID}?" + urlencode({"fields": fields})
    request = Request(url, headers={"Authorization": "Bearer " + token})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                data = json.load(response)
            if "error" in data:
                raise RuntimeError("Meta rejected the request; check token and permissions")
            profile = data["business_discovery"]
            if profile.get("username") != TARGET:
                raise ValueError("Unexpected Instagram profile")
            return select_posts(profile["media"]["data"])
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                # Response body and request headers may contain sensitive data.
                raise RuntimeError(f"Meta HTTP {error.code}; check token expiry and permissions") from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError("Meta unavailable after three attempts") from None
        time.sleep(2 ** attempt)

def replace_posts(page, posts):
    posts = select_posts(posts)
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError("Missing or duplicate Instagram markers")
    cards = []
    for post in posts:
        link = html.escape(post["permalink"], quote=True)
        cards.append(
            '\n                    <article class="social-post">\n'
            f'                        <blockquote class="instagram-media" data-instgrm-permalink="{link}" data-instgrm-version="14">\n'
            f'                            <a href="{link}" target="_blank" rel="noopener noreferrer">Ver esta publicaciÃ³n de @kim_angel en Instagram â†—</a>\n'
            '                        </blockquote>\n'
            '                    </article>')
    before, rest = page.split(START)
    _, after = rest.split(END)
    return before + START + "".join(cards) + "\n                " + END + after

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-cache", action="store_true")
    args = parser.parse_args()
    cache = ROOT / "data/instagram.json"
    if args.from_cache:
        posts = select_posts(json.loads(cache.read_text(encoding="utf-8"))["posts"])
    else:
        token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "").strip()
        if not token:
            raise ValueError("Add INSTAGRAM_ACCESS_TOKEN to GitHub Actions secrets; see docs/instagram.md")
        posts = fetch_posts(token)
    index = ROOT / "index.html"
    result = replace_posts(index.read_text(encoding="utf-8"), posts)
    # Only a minimal public allowlist is saved. Never tokens, paging URLs or raw responses.
    snapshot = json.dumps({"username": TARGET, "posts": posts}, ensure_ascii=False, indent=2) + "\n"
    cache.write_text(snapshot, encoding="utf-8", newline="\n")
    index.write_text(result, encoding="utf-8", newline="\n")
    print("Rendered three recent Instagram posts.")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, RuntimeError, OSError):
        # Avoid echoing provider payloads or credentials on unexpected errors.
        print("Instagram update failed. Check INSTAGRAM_ACCESS_TOKEN, its expiry and permissions; published site unchanged.", file=sys.stderr)
        sys.exit(1)
