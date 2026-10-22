#!/usr/bin/env python3
"""Generate article HTML and a basic or advanced slide deck, recording local stage timings."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import presentation

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['check-format', 'format'], default='check-format')
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--style-check', choices=['advisory', 'strict', 'off'], default='advisory')
    parser.add_argument('--theme', default='ai-tech')
    parser.add_argument('--cover', type=Path)
    parser.add_argument('--slides-plan', type=Path, help='Host-authored basic or advanced content plan')
    parser.add_argument('--upstream', type=Path, default=presentation.DEFAULT_UPSTREAM)
    parser.add_argument('--reuse', action='store_true', help='Reuse unchanged basic slides; manual HTML edits are protected')
    parser.add_argument('--timings', type=Path, help='Defaults to timings.json next to the article output')
    args = parser.parse_args()
    started = time.perf_counter()
    source, output = args.input.resolve(), args.output.resolve()
    timing_path = args.timings.resolve() if args.timings else output.parent / 'timings.json'
    protected = {source, output}
    if args.slides_plan:
        protected.add(args.slides_plan.resolve())
    if timing_path in protected:
        parser.error('Timings must not overwrite input, plan or article output.')
    if not source.is_file():
        parser.error(f'Input not found: {source}')
    if source == output:
        parser.error('Output must differ from input')
    plan = None
    if args.slides_plan:
        try:
            plan = presentation.load_plan(args.slides_plan.resolve(), hashlib.sha256(source.read_bytes()).hexdigest())
            if args.reuse and plan['style'] != 'basic':
                parser.error('--reuse only supports basic slides.')
            if (output.parent / 'slides').exists() and not args.reuse:
                parser.error('Slides output already exists; use --reuse for basic slides or a new output directory.')
        except (ValueError, OSError) as error:
            parser.error(str(error))
    stages = []

    def timed(name, callback):
        before = time.perf_counter()
        try:
            return callback()
        finally:
            stages.append({'stage': name, 'seconds': round(time.perf_counter() - before, 6)})

    def finish(success):
        timing_path.parent.mkdir(parents=True, exist_ok=True)
        timing_path.write_text(json.dumps({'status': 'passed' if success else 'failed', 'presentation_style': plan['style'] if plan else None, 'local_seconds': round(time.perf_counter() - started, 6), 'scope': 'Script stages only; model writing, research, Python environment setup and manual visual checks are excluded. Advanced upstream setup/download is included when used.', 'stages': stages}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return 0 if success else 1

    steps = [('scripts/markdown_to_html.py', ['--input', str(source), '--output', str(output), '--theme', args.theme]), ('scripts/check_html.py', ['--html', str(output)])]
    if args.mode == 'check-format':
        if args.style_check != 'off':
            steps.insert(0, ('scripts/check_banned_scaffolding.py', ['--input', str(source), '--policy', args.style_check]))
        steps.insert(0, ('scripts/inspect_article.py', ['--input', str(source)]))
    if args.cover:
        steps.append(('scripts/check_cover.py', ['--cover', str(args.cover.resolve())]))
    for script, options in steps:
        result = timed(Path(script).stem, lambda: subprocess.run([sys.executable, str(ROOT / script), *options], check=False))
        if result.returncode:
            print(f'[FAIL] {script}; generated files, if any, are not approved.', file=sys.stderr)
            return finish(False)
    if plan:
        try:
            directory = output.parent / 'slides'
            if plan['style'] == 'basic':
                from basic_presentation import build
                result = timed('basic_slides', lambda: build(source, plan, directory, args.reuse))
                print(f'[OK] Basic slides: {result["rendered_slides"]} rendered, {result["reused_slides"]} reused. Visual checks pending.')
            else:
                upstream = args.upstream.resolve()
                timed('upstream_setup', lambda: presentation.setup(upstream))
                timed('upstream_prepare', lambda: presentation.prepare(upstream, source, directory, plan['style']))
                timed('upstream_render', lambda: presentation.render(directory, args.slides_plan.resolve()))
                timed('upstream_validate', lambda: presentation.validate(directory))
        except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
            print(f'[FAIL] Joint delivery incomplete: {error}. Article or slide files may be partial.', file=sys.stderr)
            return finish(False)
        print(f'[OK] Article and presentation: {output}, {directory / "index.html"}')
    print(f'[OK] Local checks passed: {output}. Semantic and visual verification are separate.')
    return finish(True)


if __name__ == '__main__':
    raise SystemExit(main())
