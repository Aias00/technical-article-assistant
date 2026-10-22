import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StylePolicyTests(unittest.TestCase):
    def check(self, text, policy):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/check_banned_scaffolding.py'), '--policy', policy], input=text, capture_output=True, text=True)

    def test_advisory_and_off_do_not_block_deliberate_expression(self):
        text = '这不是新增成果，而是对原有流程的整理。'
        advisory = self.check(text, 'advisory')
        self.assertEqual(advisory.returncode, 0)
        self.assertIn('Style suggestions', advisory.stderr)
        self.assertEqual(self.check(text, 'off').returncode, 0)
        self.assertNotEqual(self.check(text, 'strict').returncode, 0)

    def test_metadata_code_and_quotes_are_excluded_even_in_strict_mode(self):
        text = '''---
title: 也就是说
---
正常正文。

````python
# 也就是说
```
也就是说
````

~~~~text
如果只
~~~~

    这一步很关键

`而不是`与``不是而是``是字面量。
> 也就是说，保留引用。
他说：“这一步很关键”。
'''
        result = self.check(text, 'strict')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_real_prose_after_protected_regions_keeps_line_location(self):
        result = self.check('---\ntitle: 也就是说\n---\n\n也就是说，检查这一行。', 'strict')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('line 5:', result.stderr)

    def test_default_pipeline_preserves_non_technical_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'summary.md'
            output = Path(tmp) / 'summary.html'
            text = '# 季度总结\n\n这不是新增成果，而是对原有流程的整理。'
            source.write_text(text)
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--input', str(source), '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('这不是新增成果，而是对原有流程的整理。', output.read_text())
            self.assertEqual(source.read_text(), text)
