"""design_lint.py 与 learn.py 的测试：检查工具必须能抓住故意做坏的输入，也不能冤枉干净的。

运行：python3 -m unittest scripts/tests/test_design_lint.py -v
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import design_lint as dl  # noqa: E402
import learn  # noqa: E402

FX = HERE / 'fixtures'


class LintFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = ['lint_slop.html', 'lint_reskin.html', 'lint_clean.html', 'lint_broken.html']
        cls.f = dict(zip(names, dl.collect([str(FX / n) for n in names])))

    def test_slop_hits_the_2026_clusters(self):
        red, yellow = dl.judge(self.f['lint_slop.html'])
        text = '\n'.join(yellow)
        self.assertIn('特征1', text)          # 暖奶油＋陶土色＋衬线
        self.assertIn('特征4', text)          # 同一圆角同一阴影的卡片
        self.assertIn('特征5', text)          # 全大写小标签、中点、箭头
        self.assertIn('只给一个词换色', text)
        self.assertIn('01/02/03', text)

    def test_clean_page_is_not_accused(self):
        red, yellow = dl.judge(self.f['lint_clean.html'])
        self.assertEqual(red, [])
        self.assertEqual(yellow, [])

    def test_broken_page_goes_red(self):
        red, _ = dl.judge(self.f['lint_broken.html'])
        text = '\n'.join(red)
        self.assertIn('图裂了', text)
        self.assertIn('正文字号', text)
        self.assertIn('对比度', text)

    def test_reskin_is_caught_by_layout_not_colour(self):
        a = dl.fingerprint(self.f['lint_slop.html'])
        b = dl.fingerprint(self.f['lint_reskin.html'])
        c = dl.fingerprint(self.f['lint_clean.html'])
        hits, pd, lc = dl.similar(a, b)
        self.assertGreater(pd, 0.06)          # 颜色确实换了
        self.assertTrue(any('骨架' in h for h in hits), hits)   # 但骨架没换
        self.assertFalse(dl.similar(a, c)[0])  # 真不同的两版不报

    def test_warm_cream_is_classified_warm(self):
        self.assertEqual(dl.bg_class((0xF4, 0xF1, 0xEA)), '浅·暖纸')
        self.assertEqual(dl.bg_class((0xFA, 0xF8, 0xF4)), '浅·暖纸')
        self.assertEqual(dl.bg_class((0xFA, 0xFA, 0xFA)), '浅·中性白')


class Ledger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ['HUASHU_DESIGN_HOME'] = self.tmp.name

    def tearDown(self):
        os.environ.pop('HUASHU_DESIGN_HOME', None)
        self.tmp.cleanup()

    def test_add_then_check_flags_the_same_look(self):
        self.assertEqual(dl.main(['ledger', 'add', str(FX / 'lint_slop.html'), '--project', '测试项目']), 0)
        rows = dl.ledger_read()
        self.assertEqual(len(rows), 1)
        self.assertIn('暖纸', rows[0]['desc'])
        # 同一个样子再来一次：必须报撞
        self.assertEqual(dl.main(['ledger', 'check', str(FX / 'lint_slop.html')]), 1)
        # 完全不同的样子：不报
        self.assertEqual(dl.main(['ledger', 'check', str(FX / 'lint_clean.html')]), 0)


class Learn(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ['HUASHU_DESIGN_HOME'] = self.tmp.name

    def tearDown(self):
        os.environ.pop('HUASHU_DESIGN_HOME', None)
        self.tmp.cleanup()

    def test_refuses_entries_nobody_can_check(self):
        with self.assertRaises(learn.LearnError):
            learn.add_entry('guess', 'deck', '随便', '证据')
        with self.assertRaises(learn.LearnError):
            learn.add_entry('observed', '', '没有主题', '证据')
        with self.assertRaises(learn.LearnError):
            learn.add_entry('observed', 'deck', '没有证据', '')
        with self.assertRaises(learn.LearnError):
            learn.add_entry('preference', 'color', '他喜欢暖色', '对话')  # 偏好必须是原话

    def test_roundtrip(self):
        learn.add_entry('preference', 'color,cover', '「封面用暖纸底」——只用于他自己的封面', '2026-10-17 对话')
        learn.add_entry('observed', 'deck', '三版都用了同一个骨架被他一眼看出', 'B2 基准')
        out = learn.recall(['deck'])
        self.assertIn('封面用暖纸底', out)      # 偏好总是带出来
        self.assertIn('同一个骨架', out)
        self.assertIn('L2', learn.local_file().read_text(encoding='utf-8'))
        self.assertNotIn('同一个骨架', learn.recall(['motion']).split('## 过去项目的经验')[1])


if __name__ == '__main__':
    unittest.main()
