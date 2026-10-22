#!/usr/bin/env python3
"""Prepare Python dependencies once, then launch a bundled script across platforms."""
import argparse
import json
import subprocess
import sys
import time
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = "import markdown, bs4, cssutils, pygments; from importlib.metadata import version; import json; print(json.dumps({x:version(x) for x in ['Markdown','beautifulsoup4','cssutils','Pygments']}))"


def ready(python):
    try:
        result = subprocess.run([str(python), '-I', '-c', PROBE], capture_output=True, text=True, timeout=30)
        return json.loads(result.stdout) if result.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Inspect only: never install or create an environment')
    parser.add_argument('--venv', type=Path, help='Explicit environment directory; default uses an existing ready interpreter or .venv')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Optional bundled script and arguments, e.g. -- run.py --input ...')
    args = parser.parse_args()
    started = time.perf_counter()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10+ is required.')
    environment = args.venv.resolve() if args.venv else ROOT / '.venv'
    python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    versions = ready(python)
    if versions is None and not args.venv:
        active = ready(Path(sys.executable))
        if active is not None:
            python, versions = Path(sys.executable), active
    installed = False
    if versions is None:
        if args.check:
            parser.exit(1, 'Core dependencies are not ready. Run bootstrap.py once without --check.\n')
        if not python.is_file():
            venv.EnvBuilder(with_pip=True, symlinks=sys.platform != 'win32').create(environment)
        subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')], check=True)
        versions = ready(python)
        if versions is None:
            parser.exit(1, 'Environment probe failed after dependency installation.\n')
        installed = True
    print(json.dumps({'python': str(python), 'installed_dependencies': installed, 'versions': versions, 'seconds': round(time.perf_counter() - started, 4)}, ensure_ascii=False), flush=True)
    command = args.command
    if command and command[0] == '--':
        command = command[1:]
    if command and not args.check:
        script = (ROOT / 'scripts' / command[0]).resolve()
        if script.parent != ROOT / 'scripts' or script.suffix != '.py' or not script.is_file() or script.name == 'bootstrap.py':
            parser.error('Choose a bundled Python script other than bootstrap.py.')
        return subprocess.run([str(python), str(script), *command[1:]], check=False).returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
