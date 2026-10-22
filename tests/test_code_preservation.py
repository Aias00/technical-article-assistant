import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


class CodePreservationTests(unittest.TestCase):
    def test_code_comments_and_h1_literals_survive_formatting(self):
        for fence in ('```', '~~~~'):
            with self.subTest(fence=fence), tempfile.TemporaryDirectory() as tmp:
                source = Path(tmp) / 'source.md'
                output = Path(tmp) / 'article.html'
                source.write_text(f'# 外部标题\n\n{fence}python\n# KEEP_COMMENT\nprint("ok")\n{fence}\n\n    # INDENTED_COMMENT\n')
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--mode', 'format', '--input', str(source), '--output', str(output)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                soup = BeautifulSoup(output.read_text(), 'html.parser')
                self.assertIsNone(soup.h1)
                code = '\n'.join(block.get_text() for block in soup.find_all('pre'))
                self.assertIn('# KEEP_COMMENT', code)
                self.assertIn('# INDENTED_COMMENT', code)
