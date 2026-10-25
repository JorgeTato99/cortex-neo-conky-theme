"""Render every README language from one layout and inline translation catalogs."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def render_readmes(root=ROOT):
    """Keep structure, examples and images shared; translations supply inline text."""
    source = root / "docs/readme"
    template = (source / "template.md.in").read_text(encoding="utf-8")
    catalogs = {}
    for path in sorted(source.glob("*.json")):
        language = path.stem
        if not re.fullmatch(r"[a-z]{2}(?:-[A-Z]{2})?", language):
            raise ValueError(f"Invalid README language: {language}")
        values = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(values, dict) or any(
            not isinstance(value, str)
            or not value.strip()
            or any(marker in value for marker in ("\n", "\r", "```", "!["))
            or value.startswith("#")
            for value in values.values()
        ):
            raise ValueError(f"README translations must be nonempty inline text: {language}")
        catalogs[language] = values
    if "en" not in catalogs:
        raise ValueError("The English README catalog is required")
    screenshots = json.loads(
        (root / "assets/screenshots/manifest.json").read_text(encoding="utf-8")
    )
    images = {image["id"]: image for image in screenshots["screenshots"]}
    english_keys = catalogs["en"].keys()
    for language, translations in catalogs.items():
        if translations.keys() != english_keys:
            raise ValueError(f"README translation keys differ from English: {language}")
    languages = sorted(catalogs, key=lambda name: (name != "en", name))
    links = " · ".join(
        f"[{catalogs[name]['LANGUAGE_NAME']}]({'README.md' if name == 'en' else 'README.' + name + '.md'})"
        for name in languages
    )
    outputs = {}
    for language, translations in catalogs.items():
        values = {
            **translations,
            "LANGUAGE": language,
            "LANGUAGE_LINKS": links,
            "DOCS_ROOT": "docs" if language == "en" else f"docs/{language}",
            "CHANGELOG_FILE": "CHANGELOG.md" if language == "en" else f"CHANGELOG.{language}.md",
            "CONTRIBUTING_FILE": "CONTRIBUTING.md"
            if language == "en"
            else f"docs/{language}/contributing.md",
            "NOTICES_FILE": "THIRD_PARTY_NOTICES.md"
            if language == "en"
            else f"docs/{language}/third-party-notices.md",
        }
        for name in ("ryzen", "dell"):
            image = images[name]
            values[name.upper() + "_RESOLUTION"] = " × ".join(map(str, image["resolution"]))
            scale = f"{image['desktop_scale'] * 100:.2f}".rstrip("0").rstrip(".")
            if language == "es":
                scale = scale.replace(".", ",")
            values[name.upper() + "_SCALE"] = scale + " %"
        unknown = set(TOKEN.findall(template)) - values.keys()
        if unknown:
            raise ValueError(f"Unknown README fields: {sorted(unknown)}")
        output = TOKEN.sub(lambda match, values=values: values[match[1]], template)
        outputs["README.md" if language == "en" else f"README.{language}.md"] = output
    # Keep the historical explicit English URL identical to the primary README.
    outputs["README.en.md"] = outputs["README.md"]
    return outputs


def stale_readmes(root=ROOT):
    return [
        name
        for name, expected in render_readmes(root).items()
        if not (root / name).is_file() or (root / name).read_text(encoding="utf-8") != expected
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated READMEs differ")
    options = parser.parse_args()
    if options.check:
        stale = stale_readmes()
        print("README generation: " + (", ".join(stale) if stale else "OK"))
        return bool(stale)
    for name, text in render_readmes().items():
        (ROOT / name).write_text(text, encoding="utf-8", newline="\n")
        print("Generated " + name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
