import unittest
import test_pipeline
from pathlib import Path
import tempfile


class EntrypointTests(unittest.TestCase):
    run_script = test_pipeline.PipelineTests.run_script
    def test_end_to_end_without_cover_or_publisher(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'article.md'
            output = Path(tmp) / 'article.html'
            source.write_text('# 标题\n\n正文内容。\n')
            result = self.run_script('scripts/run.py', '--input', source, '--output', output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())

    def test_style_failure_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'article.md'
            output = Path(tmp) / 'article.html'
            source.write_text('也就是说，这是一段测试。')
            result = self.run_script('scripts/run.py', '--input', source, '--output', output)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_cannot_overwrite_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'article.md'
            source.write_text('原稿。')
            result = self.run_script('scripts/run.py', '--input', source, '--output', source)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_text(), '原稿。')
