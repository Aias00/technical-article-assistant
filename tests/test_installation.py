import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def test_archive_runs_without_source_tree(self):
        subprocess.run([sys.executable, str(ROOT / 'scripts/package_skill.py')], check=True, capture_output=True)
        with tempfile.TemporaryDirectory() as tmp:
            with ZipFile(ROOT / 'dist/technical-article-assistant.zip') as archive:
                archive.extractall(tmp)
            installed = Path(tmp) / 'technical-article-assistant'
            self.assertEqual(list(installed.rglob('SKILL.md')), [installed / 'SKILL.md'])
            output = Path(tmp) / 'article.html'
            result = subprocess.run([sys.executable, str(installed / 'scripts/run.py'), '--input', str(installed / 'examples/article.md'), '--output', str(output)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('问题与排查', output.read_text())

    def test_format_only_preserves_flagged_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source.md'
            source.write_text('# 标题\n\n也就是说，这是一段原文。')
            output = Path(tmp) / 'article.html'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--mode', 'format', '--input', str(source), '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('也就是说，这是一段原文。', output.read_text())
            self.assertEqual(source.read_text(), '# 标题\n\n也就是说，这是一段原文。')

    def test_basic_deck_from_archive_uses_standard_library_only(self):
        subprocess.run([sys.executable, str(ROOT / 'scripts/package_skill.py')], check=True, capture_output=True)
        with tempfile.TemporaryDirectory() as tmp:
            with ZipFile(ROOT / 'dist/technical-article-assistant.zip') as archive:
                archive.extractall(tmp)
            installed = Path(tmp) / 'technical-article-assistant'
            output = Path(tmp) / 'deck'
            result = subprocess.run([sys.executable, '-S', str(installed / 'scripts/basic_presentation.py'), '--input', str(installed / 'examples/work-summary.md'), '--plan', str(installed / 'examples/basic-plan.json'), '--output-dir', str(output)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((output / 'index.html').is_file())
            self.assertIn('后续行动', (output / 'outline.md').read_text())
