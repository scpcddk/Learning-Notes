"""Check AI discovery, source-code reading, math and internal note links."""
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


class AIReaderTests(unittest.TestCase):
    def setUp(self):
        self.scratch = build_site.PAGE_ROOT.parent / "review-output"
        self.scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="ai-", dir=self.scratch)
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / "repo"
        self.notes = self.repo / "AI"
        self.notes.mkdir(parents=True)
        self.output = self.base / "site"
        self.output.mkdir()
        (self.output / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        self.repo_patch = patch.object(build_site, "REPO", self.repo)
        self.repo_patch.start()

    def tearDown(self):
        self.repo_patch.stop()
        assert self.base.parent == self.scratch.resolve()
        self.temporary.cleanup()

    def write(self, name, content):
        path = self.notes / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            build_site.build_ai(self.output, "https://github.com/example/notes", "main")
        text = (self.output / "ai/index.html").read_text(encoding="utf-8")
        self.config = json.loads(re.search(r'id="language-data">(.*?)</script>', text, re.S)[1])
        self.pages = json.loads(build_site.DATA.search(text)[2])
        build_site.validate(self.output)
        return text

    def test_sections_discovery_updates_and_test_files_are_excluded(self):
        self.write("基础知识/AI 原理.md", "# 模型原理\n\n第一版")
        pending = self.write("基础知识/补充理解/待补充.md", "")
        self.write("AI实践记录/错误处理.py", "print('实践')\n")
        self.write("AI实践记录/test_错误处理.py", "raise RuntimeError('不要发布测试')\n")
        self.write("提示词模板/知识点练习.md", "# 练习模板\n\n讲解、练习、检查。")
        removed = self.write("提示词模板/学习计划/旧模板.md", "# 旧模板")
        self.write("AI错题与易错点.md", "# 错题\n\n区分概念。")
        text = self.build()
        self.assertEqual([s["title"] for s in self.config["sections"]],
                         ["基础知识", "实践记录", "提示词模板", "错题与易错点"])
        self.assertEqual(self.config["coverUrl"], "阅读资源/ai-hero-v2.png")
        self.assertEqual(self.config["sidebarMode"], "all")
        self.assertTrue(all(not s["cover"] for s in self.config["sections"]))
        self.assertEqual(len(self.pages), 6)
        self.assertEqual(self.config["pending"], 1)
        self.assertNotIn("不要发布测试", text)
        template = next(p for p in self.pages if p["title"] == "知识点练习")
        self.assertEqual(template["kind"], "note")
        original = next(p for p in self.pages if p["pending"])
        pending.write_text("# 已补充\n\n正文更新", encoding="utf-8")
        removed.unlink()
        self.write("基础知识/新笔记.md", "# 自动新增")
        self.build()
        changed = next(p for p in self.pages if p["id"] == original["id"])
        self.assertFalse(changed["pending"])
        self.assertIn("正文更新", changed["full"])
        self.assertIn("新笔记", [p["title"] for p in self.pages])
        self.assertNotIn("旧模板", [p["title"] for p in self.pages])

    def test_chapter_outline_uses_real_heading_anchors(self):
        self.write("基础知识/AI 原理.md", """# AI 笔记

## 阅读导航

# 第一篇：整体认知

## 1. 模型是什么

### 1.1 补充说明

# 第二篇：应用开发

## 2. 调用接口

```text
# 第三篇：代码内的标题不能当目录
```
""")
        self.write("提示词模板/笔记风格.md", "# 第一篇：示例结构\n\n## 1. 示例标题")
        self.build()
        note = self.pages[0]
        self.assertEqual(self.pages[1]["chapters"], [])
        self.assertEqual([chapter["title"] for chapter in note["chapters"]], ["第一篇：整体认知", "第二篇：应用开发"])
        self.assertEqual([item["title"] for chapter in note["chapters"] for item in chapter["headings"]],
                         ["1. 模型是什么", "2. 调用接口"])
        for chapter in note["chapters"]:
            for heading in [chapter] + chapter["headings"]:
                self.assertIn('id="' + heading["id"] + '"', note["full"])

    def test_python_source_is_searchable_literal_and_linked_from_notes(self):
        source = '# 标题也必须保留为代码\nvalue = "</script> $HOME #{name} ${name}"\nprint(value)\n'
        self.write("AI实践记录/错误处理.py", source)
        self.write("基础知识/错误处理.md", "# 错误处理\n\n[完整实现](../AI实践记录/错误处理.py)")
        self.write("AI错题与易错点.md", "# 错题\n\n[原理](基础知识/错误处理.md#错误处理)")
        text = self.build()
        code = next(p for p in self.pages if p["format"] == "PY")
        note = next(p for p in self.pages if p["title"] == "错误处理")
        mistakes = next(p for p in self.pages if p["title"] == "AI错题与易错点")
        self.assertEqual(html.unescape(re.search(r'<pre><code[^>]*>(.*?)</code>', code["full"], re.S)[1]), source)
        self.assertEqual(code["search"], source)
        self.assertEqual(code["sourceLabel"], "查看 Python 源码 ↗")
        self.assertEqual(code["headings"], [])
        self.assertIn('href="#' + code["id"] + '"', note["full"])
        self.assertIn('href="#' + note["headings"][0]["id"] + '"', mistakes["full"])
        self.assertNotIn('value = "</script>', text)

    def test_math_diagrams_and_code_examples_keep_their_meanings(self):
        fenced = 'price = "$HOME $PATH"\nformula = "$$x_i$$"\n'
        text = r"""# 公式与图解

行内 $x_i^2$ 与 \(a_b\)，代码 `$TOKEN` 与 `\(literal\)`。

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}(QK^T/\sqrt{d_k})V
$$

\[
t_n = 2^{n+1}
\]

```mermaid
flowchart LR
  A[输入] --> B[输出]
```

```python
""" + fenced + '```\n'
        self.write("基础知识/公式.md", text)
        generated = self.build()
        note = self.pages[0]
        self.assertTrue(note["math"])
        self.assertTrue(note["diagrams"])
        self.assertEqual(note["full"].count('class="math-display"'), 2)
        self.assertEqual(note["full"].count('class="math-inline"'), 2)
        self.assertIn(r'\operatorname{Attention}', note["full"])
        self.assertIn('<code>$TOKEN</code>', note["full"])
        self.assertIn('<code>\\(literal\\)</code>', note["full"])
        python = re.search(r'<code class="language-python">(.*?)</code>', note["full"], re.S)[1]
        self.assertEqual(html.unescape(python), fenced)
        self.assertIn('class="mermaid-diagram"', note["full"])
        self.assertIn('查看流程图源码', note["full"])
        self.assertIn('src="阅读资源/mermaid.min.js"', generated)
        self.assertTrue((self.output / "ai/mathjax/tex-svg.js").is_file())
        self.assertTrue((self.output / "ai/阅读资源/LICENSE-mermaid").is_file())
        self.assertNotIn('<!--MATH_ASSETS-->', generated)


if __name__ == "__main__":
    unittest.main()
