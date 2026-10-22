#!/usr/bin/env python3
"""Suggest prose edits; strict mode can enforce the selected style rules."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("不是……而是……", re.compile(r"不是[^。！？\n]{0,80}而是")),
    ("不只是……而是……", re.compile(r"不只是[^。！？\n]{0,80}而是")),
    ("不……而是……", re.compile(r"不[^\n。！？]{0,60}?而是")),
    ("而不是", re.compile(r"而不是")),
    ("如果只", re.compile(r"如果只")),
    ("也就是说", re.compile(r"也就是说")),
    ("这一步很关键", re.compile(r"这一步很关键")),
]


@dataclass
class Hit:
    line_no: int
    label: str
    excerpt: str


def iter_prose_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    raw_lines = text.splitlines()
    metadata_end = -1
    if raw_lines and raw_lines[0].lstrip('\ufeff').strip() == '---':
        metadata_end = next((i for i, line in enumerate(raw_lines[1:], 1) if line.strip() in ('---', '...')), -1)
    fence = None
    for index, raw in enumerate(raw_lines):
        if index <= metadata_end:
            continue
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', raw)
        if marker:
            token, tail = marker.groups()
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence or raw.startswith(('    ', '\t')) or raw.lstrip().startswith('>'):
            continue
        prose = re.sub(r'(`+)(?!`).*?\1(?!`)', '', raw)
        prose = re.sub(r'“[^”]*”|「[^」]*」|『[^』]*』|"[^"\n]*"', '', prose)
        result.append((index + 1, prose))
    return result


def find_hits(text: str) -> list[Hit]:
    hits: list[Hit] = []
    for line_no, line in iter_prose_lines(text):
        for label, pattern in PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            start = max(0, match.start() - 18)
            end = min(len(line), match.end() + 18)
            excerpt = line[start:end].strip()
            hits.append(Hit(line_no=line_no, label=label, excerpt=excerpt))
    return hits


def read_text(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Suggest edits for selected Chinese prose patterns; no authorship or factual judgment."
    )
    parser.add_argument("--input", help="Path to the text or markdown file to check")
    parser.add_argument("--policy", choices=["advisory", "strict", "off"], default="advisory")
    args = parser.parse_args()
    if args.policy == "off":
        print("SKIPPED: prose style checking disabled")
        return 0

    text = read_text(args.input)
    hits = find_hits(text)

    if not hits:
        print("OK: no banned scaffolding patterns found in prose")
        return 0

    print("Blocked: selected style rules matched" if args.policy == "strict" else "Style suggestions: review matches in context; wording is unchanged", file=sys.stderr)
    for hit in hits:
        print(
            f"line {hit.line_no}: {hit.label} -> {hit.excerpt}",
            file=sys.stderr,
        )
    return 1 if args.policy == "strict" else 0


if __name__ == "__main__":
    raise SystemExit(main())
