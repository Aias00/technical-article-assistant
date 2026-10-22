import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


class WechatDeliveryTests(unittest.TestCase):
    def test_copyable_body_keeps_inline_typography_without_head_styles(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'article.md'
            output = Path(tmp) / 'article.html'
            source.write_text('## 排查步骤\n\n正文保留。\n\n```python\nprint("hello")\n```\n')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--mode', 'format', '--input', str(source), '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            soup = BeautifulSoup(output.read_text(), 'html.parser')
            for tag in soup.select('style, link'):
                tag.decompose()
            body = soup.body
            containers = body.find_all(recursive=False)
            self.assertTrue(any('font-size: 16px' in tag.get('style', '') and 'line-height: 1.8' in tag.get('style', '') for tag in containers), 'Copyable body lacks inline base typography')
            self.assertTrue(body.h2.get('style'))
            self.assertTrue(body.p.get('style'))
            self.assertIn('print', body.get_text())
