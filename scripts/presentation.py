#!/usr/bin/env python3
"""Prepare and validate article-based HTML presentations with pinned Guizang assets."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

UPSTREAM_URL = 'https://github.com/op7418/guizang-ppt-skill.git'
UPSTREAM_REVISION = 'c91369c449d34755d320a8b81d0734000d99d1ab'
DEFAULT_UPSTREAM = Path.home() / '.cache' / 'technical-article-assistant' / 'guizang-ppt-skill' / UPSTREAM_REVISION


def git(path, *args):
    return subprocess.run(['git', '-C', str(path), *args], check=True, capture_output=True, text=True).stdout.strip()


def verify_upstream(path):
    if git(path, 'rev-parse', 'HEAD') != UPSTREAM_REVISION:
        raise ValueError('Upstream revision differs from the pinned version; use setup in a separate directory.')
    if git(path, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Upstream checkout has local changes; refusing to package an unverified source tree.')
    for item in ('LICENSE', 'assets/template.html', 'assets/template-swiss.html', 'assets/motion.min.js', 'scripts/validate-presenter-mode.mjs', 'scripts/validate-swiss-deck.mjs'):
        if not (path / item).is_file():
            raise ValueError(f'Upstream resource missing: {item}')


def setup(destination):
    if destination.exists():
        verify_upstream(destination)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
        checkout = Path(tmp) / 'checkout'
        subprocess.run(['git', 'clone', '--no-checkout', '--depth', '1', UPSTREAM_URL, str(checkout)], check=True)
        git(checkout, 'fetch', '--depth', '1', 'origin', UPSTREAM_REVISION)
        git(checkout, 'checkout', '--detach', UPSTREAM_REVISION)
        verify_upstream(checkout)
        checkout.rename(destination)


def empty_template(html):
    # Swiss ships sample slides and notes; normalize both styles to one empty slot.
    start = html.index('<div id="deck">') + len('<div id="deck">')
    nav = html.index('<div id="nav">', start)
    end = html.rfind('</div>', start, nav)
    if end < start:
        raise ValueError('Unsupported upstream deck structure.')
    html = html[:start] + '\n<!-- SLIDES_HERE -->\n' + html[end:]
    start = html.index('const SPEAKER_NOTES =')
    end = html.index('window.__SPEAKER_NOTES__', start)
    return html[:start] + 'const SPEAKER_NOTES = [];\n' + html[end:]


def prepare(upstream, source, destination, style):
    verify_upstream(upstream)
    if not source.is_file():
        raise ValueError(f'Article not found: {source}')
    if destination.exists():
        raise ValueError('Presentation output directory already exists; choose a new directory.')
    if destination.is_relative_to(upstream):
        raise ValueError('Presentation output must be outside the upstream checkout.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    template = 'template-swiss.html' if style == 'swiss' else 'template.html'
    with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
        staged = Path(tmp) / 'deck'
        staged.mkdir()
        shutil.copytree(upstream, staged / 'upstream-source', ignore=shutil.ignore_patterns('.git'))
        (staged / 'assets').mkdir()
        (staged / 'images').mkdir()
        shutil.copy2(upstream / 'assets/motion.min.js', staged / 'assets/motion.min.js')
        shutil.copy2(upstream / 'LICENSE', staged / 'LICENSE')
        html = empty_template((upstream / 'assets' / template).read_text(encoding='utf-8'))
        notice = f'<!-- Based on {UPSTREAM_URL} at {UPSTREAM_REVISION}; AGPL-3.0. Corresponding source: upstream-source/. -->\n'
        (staged / 'index.html').write_text(notice + html, encoding='utf-8')
        shutil.copy2(source, staged / 'source-article.md')
        manifest = {'upstream': UPSTREAM_URL, 'revision': UPSTREAM_REVISION, 'license': 'AGPL-3.0', 'style': style, 'status': 'prepared_not_authored', 'article': str(source), 'article_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'source_snapshot': 'source-article.md', 'corresponding_source': 'upstream-source/'}
        (staged / 'presentation.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (staged / 'NOTICE.md').write_text('# Presentation provenance\n\nGuizang PPT Skill by 歸藏 / op7418.\n\n' + f'Upstream: {UPSTREAM_URL}\nRevision: {UPSTREAM_REVISION}\n\nThis presentation uses AGPL-3.0 templates; retain LICENSE and upstream-source when distributing. The editable index.html is the source of the adapted deck. Local assets are copied without changing their upstream notices.\n\nThis directory is an unfilled scaffold, not a completed presentation. Fonts and icons may request external services; offline readability and browser behavior require testing.\n', encoding='utf-8')
        staged.rename(destination)


class SlideCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'section' and 'slide' in dict(attrs).get('class', '').split():
            self.count += 1


def validate(directory):
    manifest = json.loads((directory / 'presentation.json').read_text(encoding='utf-8'))
    if manifest.get('revision') != UPSTREAM_REVISION or manifest.get('style') not in ('magazine', 'swiss'):
        raise ValueError('Unknown presentation version or style.')
    index = directory / 'index.html'
    counter = SlideCounter()
    counter.feed(index.read_text(encoding='utf-8'))
    if not counter.count:
        raise ValueError('No authored slides; a prepared template is not a finished presentation.')
    if not shutil.which('node'):
        raise ValueError('Node.js is required for upstream presentation validation.')
    scripts = ['validate-presenter-mode.mjs']
    if manifest['style'] == 'swiss':
        scripts.append('validate-swiss-deck.mjs')
    for name in scripts:
        subprocess.run(['node', str(directory / 'upstream-source/scripts' / name), str(index)], check=True)
    manifest['status'] = 'upstream_checks_passed_manual_checks_pending'
    manifest['checks'] = scripts
    (directory / 'presentation.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Upstream checks passed for {counter.count} slides. Inspect skipped-render warnings; manual browser and presenter checks remain required.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    install = commands.add_parser('setup', help='Download pinned upstream separately from this skill')
    install.add_argument('--destination', type=Path, default=DEFAULT_UPSTREAM)
    stage = commands.add_parser('prepare', help='Stage a template; the host must author slides and notes')
    stage.add_argument('--upstream', type=Path, default=DEFAULT_UPSTREAM)
    stage.add_argument('--input', type=Path, required=True)
    stage.add_argument('--output-dir', type=Path, required=True)
    stage.add_argument('--style', choices=['magazine', 'swiss'], default='magazine')
    check = commands.add_parser('validate')
    check.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'setup':
            setup(args.destination.resolve())
            print(f'Pinned upstream ready: {args.destination.resolve()}')
        elif args.command == 'prepare':
            prepare(args.upstream.resolve(), args.input.resolve(), args.output_dir.resolve(), args.style)
            print(f'Scaffold prepared, slides not yet authored: {args.output_dir.resolve()}')
        else:
            validate(args.directory.resolve())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
