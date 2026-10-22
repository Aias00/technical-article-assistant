#!/usr/bin/env python3
"""Run local style checks, formatting and HTML checks without external services."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['check-format', 'format'], default='check-format')
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--theme', default='ai-tech')
    parser.add_argument('--cover', type=Path, help='Optional cover to check')
    args = parser.parse_args()
    source = args.input.resolve()
    output = args.output.resolve()
    if not source.is_file():
        parser.error(f'Input not found: {source}')
    if source == output:
        parser.error('Output must differ from input')
    steps = [
        ('scripts/markdown_to_html.py', ['--input', str(source), '--output', str(output), '--theme', args.theme]),
        ('scripts/check_html.py', ['--html', str(output)]),
    ]
    if args.mode == 'check-format':
        steps.insert(0, ('scripts/check_banned_scaffolding.py', ['--input', str(source)]))
    if args.cover:
        steps.append(('scripts/check_cover.py', ['--cover', str(args.cover.resolve())]))
    for script, options in steps:
        result = subprocess.run([sys.executable, str(ROOT / script), *options], check=False)
        if result.returncode:
            print(f'[FAIL] {script}; generated files, if any, are not approved.', file=sys.stderr)
            return result.returncode
    print(f'[OK] Local checks passed: {output}. AI review and human approval remain required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
