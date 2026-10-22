#!/usr/bin/env python3
"""Inspect local Markdown assets and fences; list snippets without executing them."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
from bs4 import BeautifulSoup


def inspect(source):
    text = source.read_text(encoding='utf-8')
    errors = []
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if not match:
            continue
        marker, tail = match.groups()
        if fence is None:
            fence = (marker[0], len(marker), number)
        elif marker[0] == fence[0] and len(marker) >= fence[1] and not tail.strip():
            fence = None
    if fence:
        errors.append(f'Unclosed code fence at line {fence[2]}')
    soup = BeautifulSoup(markdown.markdown(text, extensions=['fenced_code', 'tables']), 'html.parser')
    images = []
    for image in soup.find_all('img'):
        src = image.get('src', '')
        url = urlsplit(src)
        if url.scheme or url.netloc:
            images.append({'source': src, 'status': 'not_checked', 'reason': 'non-local reference'})
            continue
        path = (source.parent / unquote(url.path)).resolve()
        exists = bool(url.path) and path.is_file()
        images.append({'source': src, 'path': str(path), 'status': 'exists' if exists else 'missing'})
        if not exists:
            errors.append(f'Local image missing: {src}')
    snippets = []
    for index, block in enumerate(soup.find_all('pre'), 1):
        code = block.find('code')
        if code is None:
            code = block
        language = next((item[9:] for item in code.get('class', []) if item.startswith('language-')), None)
        snippets.append({'id': f'code-{index}', 'language': language, 'sha256': hashlib.sha256(code.get_text().encode()).hexdigest(), 'execution_status': 'not_run'})
    return {'input': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'status': 'failed' if errors else 'passed', 'scope': 'Local image existence and top-level fence closure only; no fact, visual or runtime verification.', 'images': images, 'snippets': snippets, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, help='Optional JSON inspection report')
    args = parser.parse_args()
    source = args.input.resolve()
    if not source.is_file():
        parser.error(f'Input not found: {source}')
    if args.output and args.output.resolve() == source:
        parser.error('Report must differ from input')
    report = inspect(source)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding='utf-8')
    sys.stdout.write(payload)
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
