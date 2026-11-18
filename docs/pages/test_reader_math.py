"""Keep reader formulas renderable across Markdown layouts and delimiters."""
import html
import unittest

from markdown_it import MarkdownIt

import build_site


class ReaderMathTests(unittest.TestCase):
    def setUp(self):
        self.md = MarkdownIt("commonmark", {"html": True}).enable("table")
        build_site.enable_reader_math(self.md)

    def test_display_formula_can_close_on_its_last_content_line(self):
        for opening, closing in [("$$", "$$"), (r"\[", r"\]")]:
            for first in [opening, opening + "x_1"]:
                for last in [closing, "=x_2" + closing + "  "]:
                    with self.subTest(first=first, last=last):
                        content = [first[len(opening):], "x_1 < x_2", last.rstrip()[:-len(closing)]]
                        expected = "\n".join(content).strip()
                        markup = self.md.render("\n".join([first, "x_1 < x_2", last]))
                        self.assertEqual(markup, '<div class="math-display">' +
                                         html.escape(r"\[" + expected + r"\]") + '</div>\n')

    def test_formula_stays_inside_its_quote_or_list(self):
        formula = "$$x_1\n=x_2$$"
        for prefix, container in [("> ", "blockquote"), ("> > ", "blockquote"), ("  ", "li")]:
            with self.subTest(prefix=prefix):
                source = "\n".join(prefix + line for line in formula.splitlines())
                if container == "li":
                    source = "- Formula\n\n" + source
                markup = self.md.render(source + "\n\n## After\n")
                expected = '<div class="math-display">\\[x_1\n=x_2\\]</div>'
                self.assertIn(expected, markup)
                self.assertLess(markup.index(expected), markup.index("</" + container + ">"))
                self.assertTrue(markup.endswith("<h2>After</h2>\n"))

    def test_screenshot_covariance_formula_from_original_note(self):
        path = build_site.REPO / "数学/概率论与数理统计/习题/第四章 随机变量的数字特征 习题.md"
        markup = self.md.render(path.read_text(encoding="utf-8"))
        expected = (r"\operatorname{cov}(X,Z)" + "\n" +
                    r"=\frac13D(X)+\frac12\operatorname{cov}(X,Y)" + "\n=3-3=0.")
        self.assertIn('<div class="math-display">\\[' + expected + '\\]</div>', markup)
        self.assertNotIn("$$", markup)

    def test_math_examples_in_code_remain_literal(self):
        code = "$$x_1\n=x_2$$\n\\[x_1\n=x_2\\]\n"
        for source in ["```tex\n" + code + "```", "\n".join("    " + line for line in code.splitlines())]:
            with self.subTest(source=source):
                markup = self.md.render(source)
                self.assertIn(html.escape(code), markup)
                self.assertNotIn('class="math-', markup)
        markup = self.md.render(r"`$$x_1=x_2$$` and `\[x_1=x_2\]`")
        self.assertEqual(markup, '<p><code>$$x_1=x_2$$</code> and <code>\\[x_1=x_2\\]</code></p>\n')

    def test_unclosed_formula_does_not_consume_another_list_item(self):
        markup = self.md.render("- $$x_1\n- outside$$\n\n## After\n")
        self.assertEqual(markup.count("<li>"), 2)
        self.assertNotIn('class="math-display"', markup)
        self.assertIn("<h2>After</h2>", markup)


if __name__ == "__main__":
    unittest.main()
