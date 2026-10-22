#!/usr/bin/env python3
"""Generate article HTML and optionally assemble a source-bound HTML slide deck."""
import argparse
import hashlib
import subprocess
import sys
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
    parser.add_argument('--cover', type=Path, help='Optional cover to check')
    parser.add_argument('--slides-plan', type=Path, help='Host-authored JSON plan: produce article HTML and a populated slide deck together')
    parser.add_argument('--upstream', type=Path, default=presentation.DEFAULT_UPSTREAM)
    args = parser.parse_args()
    source = args.input.resolve()
    output = args.output.resolve()
    if not source.is_file():
        parser.error(f'Input not found: {source}')
    if source == output:
        parser.error('Output must differ from input')
    if args.slides_plan:
        try:
            plan = presentation.load_plan(args.slides_plan.resolve(), hashlib.sha256(source.read_bytes()).hexdigest())
            if (output.parent / 'slides').exists():
                parser.error('Slides output already exists; use a new article output directory.')
        except (ValueError, OSError) as error:
            parser.error(str(error))
    steps = [
        ('scripts/markdown_to_html.py', ['--input', str(source), '--output', str(output), '--theme', args.theme]),
        ('scripts/check_html.py', ['--html', str(output)]),
    ]
    if args.mode == 'check-format':
        if args.style_check != 'off':
            steps.insert(0, ('scripts/check_banned_scaffolding.py', ['--input', str(source), '--policy', args.style_check]))
        steps.insert(0, ('scripts/inspect_article.py', ['--input', str(source)]))
    if args.cover:
        steps.append(('scripts/check_cover.py', ['--cover', str(args.cover.resolve())]))
    for script, options in steps:
        result = subprocess.run([sys.executable, str(ROOT / script), *options], check=False)
        if result.returncode:
            print(f'[FAIL] {script}; generated files, if any, are not approved.', file=sys.stderr)
            return result.returncode
    if args.slides_plan:
        try:
            upstream = args.upstream.resolve()
            presentation.setup(upstream)
            directory = output.parent / 'slides'
            presentation.prepare(upstream, source, directory, plan['style'])
            presentation.render(directory, args.slides_plan.resolve())
            presentation.validate(directory)
        except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
            print(f'[FAIL] Joint delivery incomplete: {error}. Article or slide files may be partial.', file=sys.stderr)
            return 1
        print(f'[OK] Article and authored presentation: {output}, {directory / "index.html"}')
    print(f'[OK] Local checks passed: {output}. AI review and human approval remain required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
