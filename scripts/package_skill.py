#!/usr/bin/env python3
"""Create one self-contained skill archive using an explicit allowlist."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def main():
    destination = ROOT / 'dist' / 'technical-article-assistant.zip'
    destination.parent.mkdir(exist_ok=True)
    files = [ROOT / name for name in ('SKILL.md', 'README.md', 'LICENSE', 'requirements.txt')]
    for folder in ('scripts', 'references', 'assets', 'examples'):
        files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, Path('technical-article-assistant') / path.relative_to(ROOT))
    print(destination)


if __name__ == '__main__':
    main()
