import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BootstrapTests(unittest.TestCase):
    def test_check_reuses_ready_interpreter_without_installing(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/bootstrap.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['installed_dependencies'])

    def test_check_never_creates_explicit_missing_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            environment = Path(tmp) / 'missing'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/bootstrap.py'), '--check', '--venv', str(environment)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(environment.exists())

    def test_launcher_preserves_script_exit_status(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/bootstrap.py'), '--', 'run.py', '--input', '/missing/article.md', '--output', '/unused/article.html'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Input not found', result.stderr)
