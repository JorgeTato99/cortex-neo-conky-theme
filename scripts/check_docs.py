"""Check local Markdown destinations without network calls or new dependencies."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def broken_links(root=ROOT):
    errors = []
    sources = [*root.glob("*.md"), *root.glob("docs/**/*.md"), *root.glob(".github/**/*.md")]
    for source in sources:
        text = source.read_text(encoding="utf-8")
        text = re.sub(r"^```.*?^```[^\n]*", "", text, flags=re.MULTILINE | re.DOTALL)
        for reference in re.findall(r"\]\(([^)\s]+)\)", text):
            url = urlsplit(reference)
            if url.scheme or url.netloc or not url.path:
                continue
            destination = source.parent / unquote(url.path)
            if not destination.exists():
                errors.append(f"{source.relative_to(root)}: {reference}")
    return errors


def main():
    errors = broken_links()
    for error in errors:
        print("BROKEN_LINK", error)
    if not errors:
        print("Local documentation links: OK")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
