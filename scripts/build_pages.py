"""Build the static, public-only copy of the site for GitHub Pages.

Reads  ./site   (the full local site, including the admin/CMS page)
Writes ./dist   (what gets published)

The local site (python server.py) is NOT changed by this script.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site"
OUT = ROOT / "dist"

# Files that only make sense with the local backend (server.py).
REMOVE_FILES = [
    "administration.html",
    "assets/js/admin.js",
    "assets/js/local-api-client.js",
    "assets/js/public-content.js",
]

# Links to the admin page, in the three places they appear in every page.
LINK_PATTERNS = [
    # footer list item
    re.compile(r'[ \t]*<li><a href="administration\.html">[^<]*</a></li>\r?\n?'),
    # desktop dropdown / mobile menu panel entry
    re.compile(r'<a href="administration\.html"><strong>.*?</strong><small>.*?</small></a>', re.S),
    # mobile "More" row
    re.compile(r'<a href="administration\.html">Administration</a>'),
]

# Script tags for the local backend client and CMS content loader.
SCRIPT_PATTERN = re.compile(
    r'[ \t]*<script src="assets/js/(?:local-api-client|public-content|admin)\.js" defer></script>\r?\n?'
)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)

    for rel in REMOVE_FILES:
        (OUT / rel).unlink(missing_ok=True)

    # Empty placeholder folder from the local project; not needed online.
    shutil.rmtree(OUT / "supabase", ignore_errors=True)

    for page in OUT.glob("*.html"):
        with open(page, encoding="utf-8", newline="") as fh:
            text = fh.read()
        for pattern in LINK_PATTERNS:
            text = pattern.sub("", text)
        text = SCRIPT_PATTERN.sub("", text)
        with open(page, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # Safety check: nothing public may still reference the admin/backend.
    problems = []
    for page in OUT.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        for needle in ("administration.html", "local-api-client", "public-content.js", "admin.js"):
            if needle in text:
                problems.append(f"{page.name} still references {needle}")
    if problems:
        print("BUILD FAILED:\n  " + "\n  ".join(problems))
        return 1

    # Safety check: every local link/asset in the output must exist.
    missing = []
    for page in OUT.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        for ref in re.findall(r'(?:href|src)="([^"#?]+)"', text):
            if re.match(r"^(https?:|mailto:|tel:|data:|//)", ref):
                continue
            if not (OUT / ref).exists():
                missing.append(f"{page.name} -> {ref}")
    if missing:
        print("BUILD FAILED (broken local references):\n  " + "\n  ".join(sorted(set(missing))))
        return 1

    print(f"OK: built {len(list(OUT.glob('*.html')))} pages into {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
