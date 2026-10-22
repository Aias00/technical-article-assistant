import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def run_script(self, relative, *args):
        return subprocess.run([sys.executable, str(ROOT / relative), *map(str, args)], capture_output=True, text=True, cwd='/tmp')

    def test_checker_ignores_fenced_code(self):
        result = self.run_script('scripts/check_banned_scaffolding.py', '--input', ROOT / 'tests/fixtures/sample_clean.md')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_checker_rejects_known_issues(self):
        result = self.run_script('scripts/check_banned_scaffolding.py', '--input', ROOT / 'tests/fixtures/sample_with_issues.md')
        self.assertNotEqual(result.returncode, 0)

    def test_formatter_preserves_body_and_removes_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'input.md'
            output = Path(tmp) / 'result.html'
            source.write_text('---\ntitle: 测试标题\nsummary: 私有元数据\n---\n# 测试标题\n\n正文保留。\n', encoding='utf-8')
            result = self.run_script('scripts/markdown_to_html.py', '--input', source, '--output', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            html = output.read_text()
            self.assertIn('正文保留', html)
            self.assertNotIn('私有元数据', html)
            self.assertNotIn('<h1', html)


if __name__ == '__main__':
    unittest.main()
