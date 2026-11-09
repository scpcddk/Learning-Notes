"""Cover table overflow without treating fenced examples as real tables."""

import unittest

from check_markdown_tables import make_checker


class MarkdownTableTests(unittest.TestCase):
    def test_reports_truncated_cells_inside_blockquote(self):
        text = "> | Item | Example |\n> | --- | --- |\n> | OR | `a || b` |\n"
        env = {"overflow": []}
        make_checker().parse(text, env)
        self.assertEqual(env["overflow"], [(3, 2, 4)])

    def test_allows_escaped_pipes_and_ignores_fenced_table(self):
        text = (
            "| Item | Example |\n| --- | --- |\n| OR | `a \\|\\| b` |\n\n"
            "```markdown\n| Item | Example |\n| --- | --- |\n| OR | `a || b` |\n```\n"
        )
        env = {"overflow": []}
        make_checker().parse(text, env)
        self.assertEqual(env["overflow"], [])
