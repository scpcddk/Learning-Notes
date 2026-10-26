"""Check automatic frontend discovery and preserve executable teaching examples."""
import contextlib
import html
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import build_site


class FrontendReaderTests(unittest.TestCase):
    def setUp(self):
        self.scratch = build_site.PAGE_ROOT.parent / "review-output"
        self.scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="frontend-", dir=self.scratch)
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / "repo"
        self.notes = self.repo / "前端基础"
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
            build_site.build_frontend(self.output, "https://github.com/example/notes", "main")
        text = (self.output / "front-end/index.html").read_text(encoding="utf-8")
        self.config = json.loads(re.search(r'id="language-data">(.*?)</script>', text, re.S)[1])
        self.pages = json.loads(build_site.DATA.search(text)[2])
        return text

    def test_updates_and_pending_remain_in_their_sections(self):
        self.write("标记语言/Markdown.md", "# Markdown\n\n第一版。")
        self.write("标记语言/HTML.md", "")
        self.write("标记语言/CSS.md", "")
        self.write("JavaScript/JavaScript.md", "# JavaScript\n\n交互。")
        removed = self.write("Vue/npm.md", "# npm\n\n依赖。")
        self.build()
        self.assertEqual([s["title"] for s in self.config["sections"]], ["标记与排版", "JavaScript", "Vue"])
        self.assertEqual([s["pending"] for s in self.config["sections"]], [2, 0, 0])
        self.assertTrue(all(not s["cover"] for s in self.config["sections"]))
        self.assertTrue(all(len(s["topics"]) == 1 and s["topics"][0]["title"] == "待学" for s in self.config["sections"]))
        original = next(p for p in self.pages if p["title"] == "HTML")
        self.assertEqual((original["section"], original["topic"]), ("标记语言", "待学"))
        self.write("标记语言/HTML.md", "# HTML\n\n补充正文。")
        self.write("JavaScript/新笔记.md", "# 新笔记\n\n自动加入。")
        self.write("Vue/新主题/起点.md", "# 起点\n\n新增子目录。")
        removed.unlink()
        self.build()
        changed = next(p for p in self.pages if p["title"] == "HTML")
        self.assertEqual(changed["id"], original["id"])
        self.assertEqual(changed["topic"], "")
        self.assertIn("补充正文", changed["full"])
        self.assertEqual(self.config["pending"], 1)
        self.assertIn("起点", [p["title"] for p in self.pages])
        self.assertIn("新笔记", [p["title"] for p in self.pages])
        self.assertNotIn("npm", [p["title"] for p in self.pages])
        build_site.validate(self.output)

    def test_math_and_code_links_assets_are_preserved(self):
        source = 'const text = `${sensor.temp} $HOME`;\nconst schema = {"$ref": "#/data"};\n'
        vue = '<script setup>\nconst message = "safe"\n</script>\n<template><p v-bind:title="message">{{ message }}</p></template>\n'
        self.write("JavaScript/JavaScript.md", '# JS\n\n```js\n' + source + '```\n\n[排版](../标记语言/LaTeX.md#公式)\n\n![示意](image.svg)')
        self.write("JavaScript/image.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.write("Vue/Vue.md", '# Vue\n\n```vue\n' + vue + '```')
        self.write("标记语言/Markdown.md", '# Markdown\n\n~~删除线~~ 与 `~~原始语法~~`。')
        self.write("标记语言/LaTeX.md", '# LaTeX\n\n## 公式\n\n| 命令 | 结果 |\n| --- | --- |\n| `$x^2$` | $x^2$ |\n\n```tex\n$E=mc^2$\n\\[x^2\\]\n```\n')
        text = self.build()
        latex = next(p for p in self.pages if p["title"] == "LaTeX")
        js = next(p for p in self.pages if p["title"] == "JavaScript")
        component = next(p for p in self.pages if p["title"] == "Vue")
        markdown = next(p for p in self.pages if p["title"] == "Markdown")
        self.assertIn('<s>删除线</s>', markdown["full"])
        self.assertIn('<code>~~原始语法~~</code>', markdown["full"])
        self.assertIn('<span class="math-inline">\\(x^2\\)</span>', latex["full"])
        self.assertIn('<code>$x^2$</code>', latex["full"])
        self.assertIn('$E=mc^2$\n\\[x^2\\]', latex["full"])
        self.assertNotIn('math-inline', js["full"])
        self.assertEqual(html.unescape(re.search(r'<pre><code[^>]*>(.*?)</code>', js["full"], re.S)[1]), source)
        self.assertEqual(html.unescape(re.search(r'<pre><code[^>]*>(.*?)</code>', component["full"], re.S)[1]), vue)
        self.assertNotIn('<script setup>', component["full"])
        self.assertIn('href="#' + latex["headings"][1]["id"] + '"', js["full"])
        self.assertIn('src="assets/', js["full"])
        folder = self.output / "front-end"
        self.assertEqual(len(list((folder / "阅读资源").glob("*.png"))), 1)
        self.assertTrue((folder / "mathjax/tex-svg.js").is_file())
        self.assertTrue((folder / "mathjax/LICENSE").is_file())
        self.assertNotIn('<!--MATH_ASSETS-->', text)
        build_site.validate(self.output)


if __name__ == "__main__":
    unittest.main()
