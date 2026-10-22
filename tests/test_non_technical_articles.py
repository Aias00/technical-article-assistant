import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NonTechnicalArticlesTests(unittest.TestCase):
    def test_summary_promotion_and_opinion_format_without_technical_artifacts(self):
        for kind in ('work-summary', 'promotion', 'opinion'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                source = ROOT / 'examples' / f'{kind}.md'
                before = source.read_bytes()
                output = Path(tmp) / 'article.html'
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--input', str(source), '--output', str(output)], cwd='/tmp', capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(output.is_file())
                self.assertEqual(source.read_bytes(), before)
