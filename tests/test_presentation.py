import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('presentation', ROOT / 'scripts/presentation.py')
presentation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(presentation)


class PresentationTests(unittest.TestCase):
    def test_prepare_preserves_license_source_and_article_for_both_styles(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            upstream = folder / 'upstream'
            (upstream / 'assets').mkdir(parents=True)
            seed = '<div id="deck"><section class="slide" data-slide-id="sample"></section></div><div id="nav"></div><script>const SPEAKER_NOTES = [1];window.__SPEAKER_NOTES__ = SPEAKER_NOTES;</script>'
            (upstream / 'assets/template.html').write_text('magazine' + seed)
            (upstream / 'assets/template-swiss.html').write_text('swiss' + seed)
            (upstream / 'assets/motion.min.js').write_text('/* upstream runtime */')
            (upstream / 'LICENSE').write_text('AGPL source license')
            source = folder / 'article.md'
            source.write_text('原稿保持。')
            for style in ('magazine', 'swiss'):
                destination = folder / style
                with patch.object(presentation, 'verify_upstream'):
                    presentation.prepare(upstream, source, destination, style)
                html = (destination / 'index.html').read_text()
                self.assertIn(style, html)
                self.assertNotIn('data-slide-id="sample"', html)
                self.assertIn('const SPEAKER_NOTES = [];', html)
                self.assertEqual((destination / 'LICENSE').read_text(), 'AGPL source license')
                self.assertTrue((destination / 'upstream-source/assets/motion.min.js').is_file())
                self.assertEqual((destination / 'source-article.md').read_text(), '原稿保持。')
                manifest = json.loads((destination / 'presentation.json').read_text())
                self.assertEqual(manifest['status'], 'prepared_not_authored')
                with self.assertRaisesRegex(ValueError, 'No authored slides'):
                    presentation.validate(destination)
            self.assertEqual(source.read_text(), '原稿保持。')

    def test_prepare_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'article.md'
            source.write_text('原稿')
            with patch.object(presentation, 'verify_upstream'), self.assertRaisesRegex(ValueError, 'already exists'):
                presentation.prepare(folder, source, folder, 'magazine')

    def test_version_mismatch_is_rejected(self):
        with patch.object(presentation, 'git', return_value='different-revision'), self.assertRaisesRegex(ValueError, 'revision differs'):
            presentation.verify_upstream(Path('/unused'))

    def test_prepare_refuses_output_inside_upstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'article.md'
            source.write_text('原稿')
            with patch.object(presentation, 'verify_upstream'), self.assertRaisesRegex(ValueError, 'outside the upstream'):
                presentation.prepare(folder, source, folder / 'nested-output', 'magazine')
