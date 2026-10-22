import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('joint_presentation', ROOT / 'scripts/presentation.py')
presentation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(presentation)


def plan_for(source):
    return {'style': 'magazine', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'slides': [{'id': 'review-flow', 'title': '技术核稿', 'classes': 'hero dark', 'content_html': '<div class="frame"><h1 class="h-hero">技术核稿</h1><p>基于证据，保留待核实项。</p></div>', 'notes': {'purpose': '说明核稿范围', 'talk': ['核对资料', '保留不确定性', '区分排版与事实'], 'transition': '讨论核验问题'}}]}


class JointDeliveryTests(unittest.TestCase):
    def test_render_creates_real_slides_outline_and_safe_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('# 技术核稿\n\n基于证据。')
            plan = plan_for(source)
            plan['slides'][0]['notes']['talk'][0] = '保留字面量 </script>，不结束脚本'
            plan_path = folder / 'plan.json'
            plan_path.write_text(json.dumps(plan, ensure_ascii=False))
            (folder / 'presentation.json').write_text(json.dumps({'article_sha256': plan['source_sha256'], 'style': 'magazine'}))
            (folder / 'index.html').write_text('<div id="deck"><!-- SLIDES_HERE --></div><script>const SPEAKER_NOTES = [];window.__SPEAKER_NOTES__ = SPEAKER_NOTES;</script>')
            presentation.render(folder, plan_path)
            soup = BeautifulSoup((folder / 'index.html').read_text(), 'html.parser')
            self.assertEqual(len(soup.select('section.slide')), 1)
            self.assertIn('技术核稿', soup.get_text())
            self.assertEqual(len(soup.find_all('script')), 1)
            self.assertIn('\\u003c/script>', soup.script.string)
            self.assertTrue((folder / 'outline.md').is_file())
            self.assertEqual(json.loads((folder / 'presentation.json').read_text())['status'], 'authored_not_validated')
            with self.assertRaisesRegex(ValueError, 'already authored'):
                presentation.render(folder, plan_path)

    def test_stale_or_empty_plan_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('原稿')
            plan = plan_for(source)
            path = folder / 'plan.json'
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'does not match'):
                presentation.load_plan(path, 'changed-source')
            plan['slides'] = []
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'at least one'):
                presentation.load_plan(path)

    def test_duplicate_ids_and_missing_notes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('原稿')
            plan = plan_for(source)
            path = folder / 'plan.json'
            plan['slides'].append(plan['slides'][0])
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'unique'):
                presentation.load_plan(path)
            plan['slides'] = [dict(plan['slides'][0], notes={})]
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'purpose and transition'):
                presentation.load_plan(path)

    def test_declared_images_are_copied_and_missing_references_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'revised.md'
            source.write_text('原稿')
            image = folder / 'source-image.png'
            image.write_bytes(b'image-test-bytes')
            plan = plan_for(source)
            plan['images'] = [{'source': 'source-image.png', 'name': 'diagram.png'}]
            plan['slides'][0]['content_html'] += '<img src="images/diagram.png">'
            plan_path = folder / 'plan.json'
            plan_path.write_text(json.dumps(plan))
            deck = folder / 'deck'
            deck.mkdir()
            (deck / 'presentation.json').write_text(json.dumps({'article_sha256': plan['source_sha256'], 'style': 'magazine'}))
            template = '<div id="deck"><!-- SLIDES_HERE --></div><script>const SPEAKER_NOTES = [];</script>'
            (deck / 'index.html').write_text(template)
            presentation.render(deck, plan_path)
            self.assertEqual((deck / 'images/diagram.png').read_bytes(), image.read_bytes())
            plan['slides'][0]['content_html'] += '<img src="images/missing.png">'
            plan_path.write_text(json.dumps(plan))
            (deck / 'index.html').write_text(template)
            with self.assertRaisesRegex(ValueError, 'image missing'):
                presentation.render(deck, plan_path)
            self.assertEqual((deck / 'index.html').read_text(), template)
