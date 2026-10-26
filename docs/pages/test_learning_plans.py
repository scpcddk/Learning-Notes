"""Check status-based discovery and faithful task-list rendering for study plans."""
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import build_site


class LearningPlansReaderTests(unittest.TestCase):
    def setUp(self):
        self.scratch = build_site.PAGE_ROOT.parent / "review-output"
        self.scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="plans-", dir=self.scratch)
        self.base = Path(self.temporary.name).resolve()
        assert self.base.parent == self.scratch.resolve()
        self.repo = self.base / "repo"
        self.notes = self.repo / "学习计划"
        self.notes.mkdir(parents=True)
        self.output = self.base / "site"
        self.output.mkdir()
        (self.output / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        self.patch = patch.object(build_site, "REPO", self.repo)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        assert self.base.parent == self.scratch.resolve()
        self.temporary.cleanup()

    def write(self, name, text):
        path = self.notes / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            build_site.build_learning_plans(self.output, "https://github.com/example/notes", "main")
        text = (self.output / "learning-plans/index.html").read_text(encoding="utf-8")
        self.config = json.loads(re.search(r'id="language-data">(.*?)</script>', text, re.S)[1])
        self.pages = json.loads(build_site.DATA.search(text)[2])
        return text

    def test_status_groups_single_cover_extensionless_and_updates(self):
        self.write("进行中/新计划.md", "# 新计划\n\n第一版。")
        self.write("阶段性完成/MySQL.md", "# MySQL\n\n阶段回顾。")
        self.write("已结束或舍弃/数学建模编程手一月计划", "# 数学建模\n\n旧路线。")
        self.write("学习指南.html", "<!doctype html><html><body><h1>学习方法</h1><p>特殊检索内容</p></body></html>")
        text = self.build()
        self.assertEqual([s["title"] for s in self.config["sections"]], ["进行中", "阶段性完成", "已结束或舍弃", "学习方法"])
        self.assertTrue(all(not s["cover"] for s in self.config["sections"]))
        self.assertEqual(len(list((self.output / "learning-plans/阅读资源").glob("*.png"))), 1)
        self.assertEqual(self.config["notes"], 3)
        self.assertEqual(next(p for p in self.pages if p["title"] == "数学建模编程手一月计划")["kind"], "note")
        guide = next(p for p in self.pages if p["kind"] == "diagram")
        self.assertEqual(guide["section"], "学习方法")
        self.assertIn("特殊检索内容", guide["search"])
        self.assertNotIn('>编程语言</a>', text)
        original = next(p for p in self.pages if p["title"] == "新计划")
        self.write("进行中/新计划.md", "# 新计划\n\n第二版。")
        self.write("进行中/后续.md", "# 后续\n\n自动收录。")
        self.build()
        changed = next(p for p in self.pages if p["title"] == "新计划")
        self.assertEqual(changed["id"], original["id"])
        self.assertIn("第二版", changed["full"])
        self.assertEqual(next(s for s in self.config["sections"] if s["title"] == "进行中")["notes"], 2)
        build_site.validate(self.output)

    def test_checkboxes_code_examples_and_internal_links(self):
        source = '''# 任务

- [x] 已完成记录
- [ ] 待执行任务

```md
- [x] 示例，不能计入进度
```

[回顾](../阶段性完成/MySQL.md#复习)
'''
        original = self.write("进行中/任务.md", source)
        self.write("阶段性完成/MySQL.md", "# MySQL\n\n## 复习\n\n内容。")
        self.build()
        task = next(p for p in self.pages if p["title"] == "任务")
        target = next(p for p in self.pages if p["title"] == "MySQL")
        self.assertEqual(task["tasks"], {"done": 1, "total": 2})
        self.assertEqual(task["full"].count('type="checkbox" disabled'), 2)
        self.assertIn('disabled checked', task["full"])
        self.assertIn('- [x] 示例，不能计入进度', task["full"])
        self.assertIn('href="#' + target["headings"][1]["id"] + '"', task["full"])
        self.assertEqual(original.read_text(encoding="utf-8"), source)
        build_site.validate(self.output)


if __name__ == "__main__":
    unittest.main()
