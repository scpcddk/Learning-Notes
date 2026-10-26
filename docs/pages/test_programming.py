"""Regression checks for directory-driven readers. Run: python -m unittest discover -s docs/pages -p test_programming.py"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_site


class ProgrammingReaderTests(unittest.TestCase):
    def setUp(self):
        self.scratch = build_site.PAGE_ROOT.parent / "review-output"
        self.scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="programming-", dir=self.scratch)
        self.base = Path(self.temporary.name).resolve()
        assert self.base.parent == self.scratch.resolve()
        self.repo = self.base / "repo"
        self.notes = self.repo / "编程语言"
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
            return build_site.build_programming(self.output, "https://github.com/example/notes", "main")

    def pages(self, slug):
        text = (self.output / "programming-languages" / slug / "index.html").read_text(encoding="utf-8")
        return json.loads(build_site.DATA.search(text)[2])

    def test_add_edit_remove_notes_and_add_language(self):
        self.write("Python/基础/起点.md", "# 起点\n\n第一版。")
        self.build()
        original = self.pages("python")[0]
        self.write("Python/基础/起点.md", "# 起点\n\n第二版，补上函数。")
        extra = self.write("Python/基础/函数.md", "# 函数\n\n新笔记。")
        self.write("Rust/基础/所有权.md", "# 所有权\n\n新的语言。")
        languages = self.build()
        pages = self.pages("python")
        self.assertEqual(len(pages), 2)
        changed = next(p for p in pages if p["title"] == "起点")
        self.assertEqual(changed["id"], original["id"])
        self.assertIn("第二版", changed["full"])
        rust = next(item for item in languages if item["title"] == "Rust")
        self.assertEqual(rust["cover"], "programming-hero.png")
        self.assertIn("所有权", self.pages(rust["slug"])[0]["full"])
        extra.unlink()
        self.build()
        self.assertEqual(len(self.pages("python")), 1)

    def test_code_literals_navigation_images_and_empty_notes(self):
        self.write("Python/基础/起点.md", '''---
markmap:
  initialExpandLevel: 2
---
# 起点

`==keep==` 与 ==强调==。

```python
price = "$HOME"
equal = a == b
unsafe = "</script><script>bad()</script>"
```

[去函数](函数.md#参数)
[跨语言](../../JAVA/类.md#方法)
![插图](image.svg)
''')
        self.write("Python/基础/函数.md", "# 函数\n\n## 参数\n\n内容。")
        self.write("JAVA/类.md", "# 类\n\n## 方法\n\n内容。")
        self.write("Python/待补充.md", "")
        image = self.notes / "Python/基础/image.svg"
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        self.build()
        pages = self.pages("python")
        page = next(p for p in pages if p["title"] == "起点")
        target = next(p for p in pages if p["title"] == "函数")
        java = self.pages("java")[0]
        self.assertNotIn("initialExpandLevel", page["full"])
        self.assertIn('<code>==keep==</code>', page["full"])
        self.assertIn('<mark>强调</mark>', page["full"])
        self.assertIn('$HOME', page["full"])
        self.assertIn('a == b', page["full"])
        self.assertNotIn('<script>bad()', page["full"])
        self.assertIn('href="#' + target["headings"][1]["id"] + '"', page["full"])
        self.assertIn('href="../java/#' + java["headings"][1]["id"] + '"', page["full"])
        self.assertIn('src="assets/', page["full"])
        self.assertEqual(len(list((self.output / "programming-languages/python/assets").iterdir())), 1)
        self.assertTrue(next(p for p in pages if p["title"] == "待补充")["pending"])
        build_site.validate(self.output)

    def test_case_insensitive_category_order_and_materials(self):
        self.write("Python/Python后端/开发.md", "# 后端\n\n开发笔记。")
        self.write("Python/python基础语法/核心语法.md", "# 基础\n\n从语法开始。")
        self.write("Python/图解.html", "<!doctype html><html><body><h1>图解</h1></body></html>")
        self.write("Python/课件/讲义.pdf", "%PDF-1.7\n")
        self.write("Python/课件/原课件.pptx", "test resource")
        self.build()
        pages = self.pages("python")
        self.assertEqual(pages[0]["title"], "核心语法")
        diagram = next(p for p in pages if p["kind"] == "diagram")
        pdf = next(p for p in pages if p["kind"] == "pdf")
        resource = next(p for p in pages if p["kind"] == "resource")
        folder = self.output / "programming-languages/python"
        self.assertTrue((folder / diagram["embed"]).is_file())
        self.assertTrue((folder / pdf["pdf"]).is_file())
        self.assertNotIn("embed", resource)
        build_site.validate(self.output)


if __name__ == "__main__":
    unittest.main()
