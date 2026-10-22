import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('basic', ROOT / 'scripts/basic_presentation.py')
basic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(basic)


def make_plan(source):
    return {'style': 'basic', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'slides': [
        {'id': 'context', 'title': '范围', 'layout': 'cover', 'bullets': ['已有材料，不扩大结论。'], 'notes': ['说明输入范围。']},
        {'id': 'next', 'title': '下一步', 'bullets': ['补充尚未测量的记录。'], 'notes': ['保留待核实事项。']}]}


class BasicPresentationTests(unittest.TestCase):
    def test_offline_text_is_escaped_and_notes_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('原稿')
            plan = make_plan(source)
            plan['slides'][0]['bullets'] = ['字面量 <script> 不能当HTML执行。']
            plan['slides'][0]['notes'] = ['保留 </script> 字面量。']
            result = basic.build(source, plan, folder / 'slides')
            soup = BeautifulSoup((folder / 'slides/index.html').read_text(), 'html.parser')
            self.assertEqual(len(soup.select('section.slide')), 2)
            self.assertIn('<script>', soup.select('section.slide')[0].get_text())
            self.assertEqual(len(soup.find_all('script')), 1)
            self.assertFalse(soup.select('script[src], link[href], img[src]'))
            self.assertEqual(result['rendered_slides'], 2)
            self.assertFalse(result['browser_verified'])

    def test_incremental_reuses_only_unchanged_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('原稿')
            plan = make_plan(source)
            basic.build(source, plan, folder / 'slides')
            result = basic.build(source, plan, folder / 'slides', reuse=True)
            self.assertEqual((result['rendered_slides'], result['reused_slides']), (0, 2))
            source.write_text('改稿')
            plan['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
            plan['slides'][1]['bullets'] = ['已修改的下一步。']
            result = basic.build(source, plan, folder / 'slides', reuse=True)
            self.assertEqual((result['rendered_slides'], result['reused_slides']), (1, 1))
            self.assertIn('已修改', (folder / 'slides/index.html').read_text())
            self.assertEqual((folder / 'slides/source-article.md').read_text(), '改稿')

    def test_manual_edits_and_template_changes_are_handled(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('原稿')
            plan = make_plan(source)
            basic.build(source, plan, folder / 'slides')
            template = folder / 'template.html'
            template.write_text(basic.TEMPLATE.read_text() + '\n<!-- updated -->')
            with patch.object(basic, 'TEMPLATE', template):
                result = basic.build(source, plan, folder / 'slides', reuse=True)
            self.assertEqual(result['reused_slides'], 0)
            index = folder / 'slides/index.html'
            index.write_text(index.read_text() + 'manual-edit')
            with self.assertRaisesRegex(ValueError, 'changed manually'):
                basic.build(source, plan, folder / 'slides', reuse=True)
            self.assertTrue(index.read_text().endswith('manual-edit'))

    def test_stale_empty_and_dense_plans_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'revised.md'
            source.write_text('原稿')
            plan = make_plan(source)
            with self.assertRaisesRegex(ValueError, 'does not match'):
                basic.validate_plan(plan, 'changed')
            plan['slides'][0]['bullets'] = ['太长'] * 5
            with self.assertRaisesRegex(ValueError, 'split dense'):
                basic.validate_plan(plan)
            plan['slides'] = []
            with self.assertRaisesRegex(ValueError, 'at least one'):
                basic.validate_plan(plan)

    def test_joint_quick_path_without_git_or_node(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('# 总结\n\n仅整理已有材料。')
            plan = folder / 'plan.json'
            plan.write_text(json.dumps(make_plan(source), ensure_ascii=False))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--input', str(source), '--output', str(folder / 'article.html'), '--slides-plan', str(plan)], env={'PATH': '', 'PYTHONIOENCODING': 'utf-8'}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((folder / 'article.html').is_file())
            self.assertTrue((folder / 'slides/index.html').is_file())
            timings = json.loads((folder / 'timings.json').read_text())
            self.assertEqual(timings['presentation_style'], 'basic')
            self.assertEqual(timings['status'], 'passed')
            self.assertNotIn('upstream_setup', [stage['stage'] for stage in timings['stages']])
