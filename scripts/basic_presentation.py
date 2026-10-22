#!/usr/bin/env python3
"""Render a text-only, offline HTML deck from a compact content plan; no third-party imports."""
import argparse
import hashlib
import json
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'assets' / 'slides-basic.html'


def digest(value):
    return hashlib.sha256(value).hexdigest()


def validate_plan(plan, expected_sha=None):
    if not isinstance(plan, dict) or plan.get('style') != 'basic':
        raise ValueError('Basic plan needs style=basic.')
    if expected_sha is not None and plan.get('source_sha256') != expected_sha:
        raise ValueError('Presentation plan does not match the revised article; regenerate the plan.')
    if plan.get('images'):
        raise ValueError('Basic mode is text-only; use an advanced plan for images.')
    slides = plan.get('slides')
    if not isinstance(slides, list) or not slides:
        raise ValueError('Basic plan needs at least one authored slide.')
    ids = set()
    for slide in slides:
        if not isinstance(slide, dict):
            raise ValueError('Every slide must be an object.')
        identifier = slide.get('id')
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier) or identifier in ids:
            raise ValueError('Every slide needs a unique lowercase semantic id.')
        ids.add(identifier)
        title = slide.get('title')
        if not isinstance(title, str) or not title.strip() or len(title) > 40:
            raise ValueError('Basic slide titles need 1-40 characters; split long titles.')
        bullets = slide.get('bullets')
        if not isinstance(bullets, list) or not 1 <= len(bullets) <= 4 or any(not isinstance(x, str) or not x.strip() or len(x) > 90 for x in bullets):
            raise ValueError('Basic slides need 1-4 bullets of at most 90 characters each; split dense content.')
        notes = slide.get('notes')
        if not isinstance(notes, list) or not notes or any(not isinstance(x, str) or not x.strip() for x in notes):
            raise ValueError('Basic slides need speaker notes as a non-empty text array.')
        if slide.get('layout', 'bullets') not in ('cover', 'bullets', 'closing'):
            raise ValueError('Unknown basic slide layout.')
    return plan


def build(source, plan, destination, reuse=False):
    source_hash = digest(source.read_bytes())
    validate_plan(plan, source_hash)
    template = TEMPLATE.read_text(encoding='utf-8')
    template_hash = digest(template.encode())
    manifest_path = destination / 'presentation.json'
    previous = {}
    if destination.exists():
        if not reuse:
            raise ValueError('Slides output already exists; use --reuse or choose a new output directory.')
        if not manifest_path.is_file():
            raise ValueError('Refusing to reuse a directory without a basic presentation manifest.')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('engine') != 'basic-v1':
            raise ValueError('Reuse only supports this skill\'s basic presentations.')
        # Preserve manual HTML edits: never replace them through an incremental build.
        index = destination / 'index.html'
        if not index.is_file() or digest(index.read_bytes()) != manifest.get('html_sha256'):
            raise ValueError('Presentation HTML has changed manually; use a new output directory.')
        cache_path = destination / '.cache' / 'slides.json'
        if cache_path.is_file():
            cache = json.loads(cache_path.read_text(encoding='utf-8'))
            if cache.get('template_sha256') == template_hash:
                previous = cache.get('slides', {})
    destination.mkdir(parents=True, exist_ok=True)
    fragments, notes, outline, cache = [], [], ['# 演示大纲与讲稿', ''], {}
    reused = 0
    for slide in plan['slides']:
        identifier = slide['id']
        fingerprint = digest(json.dumps(slide, ensure_ascii=False, sort_keys=True).encode())
        old = previous.get(identifier, {})
        if old.get('sha256') == fingerprint and isinstance(old.get('html'), str):
            fragment = old['html']
            reused += 1
        else:
            items = ''.join(f'<li>{escape(item)}</li>' for item in slide['bullets'])
            fragment = f'<section class="slide {escape(slide.get("layout", "bullets"))}" data-slide-id="{identifier}"><div class="eyebrow">ARTICLE / PRESENTATION</div><h1>{escape(slide["title"])}</h1><ul>{items}</ul><div class="page-number"></div></section>'
        fragments.append(fragment)
        cache[identifier] = {'sha256': fingerprint, 'html': fragment}
        notes.append({'id': identifier, 'title': slide['title'], 'talk': slide['notes']})
        outline.extend([f'## {slide["title"]} ({identifier})', *[f'- {x}' for x in slide['bullets']], '', '讲稿：', *[f'- {x}' for x in slide['notes']], ''])
    payload = json.dumps(notes, ensure_ascii=False).replace('<', r'\u003c')
    html = template.replace('<!-- SLIDES_HERE -->', '\n'.join(fragments)).replace('/* NOTES_HERE */ []', payload)
    (destination / 'index.html').write_text(html, encoding='utf-8')
    (destination / 'outline.md').write_text('\n'.join(outline), encoding='utf-8')
    (destination / 'slides-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (destination / 'source-article.md').write_bytes(source.read_bytes())
    shutil.copy2(ROOT / 'LICENSE', destination / 'LICENSE')
    (destination / '.cache').mkdir(exist_ok=True)
    (destination / '.cache/slides.json').write_text(json.dumps({'template_sha256': template_hash, 'slides': cache}, ensure_ascii=False), encoding='utf-8')
    manifest = {'engine': 'basic-v1', 'style': 'basic', 'article_sha256': source_hash, 'html_sha256': digest((destination / 'index.html').read_bytes()), 'template_sha256': template_hash, 'status': 'local_structure_checked_visual_pending', 'slide_count': len(fragments), 'rendered_slides': len(fragments) - reused, 'reused_slides': reused, 'checks': ['plan_schema', 'source_hash', 'escaped_text', 'bounded_content'], 'browser_verified': False}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--reuse', action='store_true')
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding='utf-8'))
        result = build(args.input.resolve(), plan, args.output_dir.resolve(), args.reuse)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
