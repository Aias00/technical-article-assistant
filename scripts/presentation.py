#!/usr/bin/env python3
"""Prepare and validate article-based HTML presentations with pinned Guizang assets."""
import argparse
import hashlib
import json
import re
from html import escape
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

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
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs).get('src', ''))
        if tag == 'section' and 'slide' in dict(attrs).get('class', '').split():
            self.count += 1


def load_plan(path, expected_sha=None):
    plan = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(plan, dict) and plan.get('style') == 'basic':
        from basic_presentation import validate_plan
        return validate_plan(plan, expected_sha)
    if not isinstance(plan, dict) or plan.get('style') not in ('magazine', 'swiss'):
        raise ValueError('Plan style must be magazine or swiss.')
    if expected_sha is not None and plan.get('source_sha256') != expected_sha:
        raise ValueError('Presentation plan does not match the revised article; regenerate the plan.')
    slides = plan.get('slides')
    if not isinstance(slides, list) or not slides:
        raise ValueError('Presentation plan needs at least one authored slide.')
    images = plan.get('images', [])
    if not isinstance(images, list):
        raise ValueError('Plan images must be an array.')
    names = set()
    for image in images:
        if not isinstance(image, dict) or not isinstance(image.get('source'), str) or not isinstance(image.get('name'), str):
            raise ValueError('Each image needs source and name.')
        name = image['name']
        if not name or name in ('.', '..') or '/' in name or '\\' in name or name in names:
            raise ValueError('Image names must be unique filenames without path separators.')
        names.add(name)
        if not (path.parent / image['source']).resolve().is_file():
            raise ValueError(f'Plan image source missing: {image["source"]}')
    ids = set()
    for slide in slides:
        if not isinstance(slide, dict):
            raise ValueError('Every slide must be an object.')
        identifier = slide.get('id', '')
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier) or identifier in ids:
            raise ValueError('Every slide needs a unique lowercase semantic id.')
        ids.add(identifier)
        for field in ('title', 'content_html', 'classes'):
            if not isinstance(slide.get(field), str) or not slide[field].strip():
                raise ValueError(f'Slide {identifier}: {field} is required.')
        body = SlideCounter()
        body.feed(slide['content_html'])
        if body.count or re.search(r'</?section\b', slide['content_html'], re.I):
            raise ValueError('content_html must contain the slide interior, not section wrappers.')
        note = slide.get('notes')
        if not isinstance(note, dict) or any(not isinstance(note.get(field), str) or not note[field].strip() for field in ('purpose', 'transition')):
            raise ValueError(f'Slide {identifier}: notes need purpose and transition.')
        talk = note.get('talk')
        if not isinstance(talk, list) or not talk or any(not isinstance(item, str) or not item.strip() for item in talk):
            raise ValueError(f'Slide {identifier}: notes need non-empty talk items.')
        if plan['style'] == 'swiss' and not re.fullmatch(r'S(?:0[1-9]|1[0-9]|2[0-2])|SWISS-(?:COVER|CLOSING)-ASCII', str(slide.get('layout', ''))):
            raise ValueError(f'Slide {identifier}: registered Swiss layout is required.')
    return plan


def render(directory, plan_path):
    manifest_path = directory / 'presentation.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    plan = load_plan(plan_path, manifest['article_sha256'])
    if plan['style'] != manifest['style']:
        raise ValueError('Presentation plan style differs from the prepared template.')
    index = directory / 'index.html'
    html = index.read_text(encoding='utf-8')
    if html.count('<!-- SLIDES_HERE -->') != 1 or 'const SPEAKER_NOTES = [];' not in html:
        raise ValueError('Template is already authored or has changed; prepare a new output directory.')
    copies = []
    for image in plan.get('images', []):
        source = (plan_path.parent / image['source']).resolve()
        target = directory / 'images' / image['name']
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError(f'Image target already differs: {target}')
        copies.append((source, target))
    declared = {f'images/{image["name"]}' for image in plan.get('images', [])}
    for slide in plan['slides']:
        body = SlideCounter()
        body.feed(slide['content_html'])
        for src in body.images:
            url = urlsplit(src)
            if url.scheme or url.netloc:
                continue
            relative = unquote(url.path)
            target = (directory / relative).resolve()
            if not relative or not target.is_relative_to(directory.resolve()) or (relative not in declared and not target.is_file()):
                raise ValueError(f'Presentation image missing or outside deck: {src}')
    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        if source != target.resolve():
            shutil.copy2(source, target)
    sections, notes, outline = [], [], ['# 演示大纲', '']
    for slide in plan['slides']:
        attrs = {'class': 'slide ' + slide['classes'], 'data-slide-id': slide['id'], 'data-title': slide['title']}
        if slide.get('layout'):
            attrs['data-layout'] = slide['layout']
        if slide.get('animation'):
            attrs['data-animate'] = slide['animation']
        attributes = ' '.join(f'{key}="{escape(str(value), quote=True)}"' for key, value in attrs.items())
        sections.append(f"<section {attributes}>\n{slide['content_html']}\n</section>")
        note = dict(slide['notes'], id=slide['id'], title=slide['title'])
        notes.append(note)
        outline.extend([f"## {slide['title']} ({slide['id']})", f"目的：{note['purpose']}", f"版式：{slide.get('layout', slide['classes'])}", *[f'- {item}' for item in note['talk']], f"转场：{note['transition']}", ''])
    notes_json = json.dumps(notes, ensure_ascii=False).replace('<', r'\u003c')
    html = html.replace('<!-- SLIDES_HERE -->', '\n'.join(sections))
    html = html.replace('const SPEAKER_NOTES = [];', f'const SPEAKER_NOTES = {notes_json};')
    index.write_text(html, encoding='utf-8')
    (directory / 'outline.md').write_text('\n'.join(outline), encoding='utf-8')
    (directory / 'slides-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifest['status'] = 'authored_not_validated'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


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
    author = commands.add_parser('render', help='Assemble authored slides and notes from a source-bound JSON plan')
    author.add_argument('--directory', type=Path, required=True)
    author.add_argument('--plan', type=Path, required=True)
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
        elif args.command == 'render':
            render(args.directory.resolve(), args.plan.resolve())
            print('Slides and speaker notes authored; validation remains required.')
        else:
            validate(args.directory.resolve())
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
