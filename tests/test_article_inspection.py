import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ArticleInspectionTests(unittest.TestCase):
    def inspect(self, folder, text):
        source = folder / 'article.md'
        source.write_text(text)
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/inspect_article.py'), '--input', str(source)], cwd='/tmp', capture_output=True, text=True)
        return result, json.loads(result.stdout)

    def test_relative_images_resolve_from_article_and_remote_images_are_not_fetched(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'image name.png').write_bytes(b'test')
            result, report = self.inspect(folder, '![本地](image%20name.png)\n\n![远端](https://example.invalid/image.png)')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([image['status'] for image in report['images']], ['exists', 'not_checked'])

    def test_missing_image_and_unclosed_fence_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, report = self.inspect(Path(tmp), '![缺图](missing.png)\n\n```python\nprint(1)')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(len(report['errors']), 2)

    def test_snippets_are_inventoried_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            sentinel = folder / 'must-not-exist'
            result, report = self.inspect(folder, f'````python\nfrom pathlib import Path\nPath({str(sentinel)!r}).touch()\n# ``` is content\n````\n')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertEqual(report['snippets'][0]['language'], 'python')
            self.assertEqual(report['snippets'][0]['execution_status'], 'not_run')

    def test_check_format_stops_before_creating_html_for_missing_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'article.md'
            source.write_text('![缺图](missing.png)')
            output = folder / 'article.html'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--input', str(source), '--output', str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
