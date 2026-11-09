"""Report cells that Markdown would silently discard from a table row."""

from pathlib import Path
import subprocess
import sys

from markdown_it import MarkdownIt
from markdown_it.rules_block.table import escapedSplit, getLine, table


def check_table(state, start_line, end_line, silent):
    first_token = len(state.tokens)
    matched = table(state, start_line, end_line, silent)
    if not matched or silent:
        return matched

    separator = getLine(state, start_line + 1).strip().removeprefix("|").removesuffix("|")
    expected = separator.count("|") + 1
    for token in state.tokens[first_token:]:
        if token.type != "tbody_open":
            continue
        for line in range(*token.map):
            cells = escapedSplit(getLine(state, line).strip())
            actual = len(cells) - (cells[0] == "") - (cells[-1] == "")
            if actual > expected:
                state.env["overflow"].append((line + 1, expected, actual))
    return matched


def make_checker():
    parser = MarkdownIt("commonmark", {"html": True}).enable("table")
    parser.block.ruler.at("table", check_table, {"alt": ["paragraph", "reference"]})
    return parser


def main():
    root = Path(__file__).resolve().parents[2]
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.md"],
        cwd=root,
    ).decode("utf-8").split("\0")
    parser = make_checker()
    failed = False
    for path in sorted(set(paths) - {""}):
        source = root / path
        if not source.is_file():
            continue
        env = {"overflow": []}
        parser.parse(source.read_text(encoding="utf-8-sig"), env)
        for line, expected, actual in env["overflow"]:
            print(
                f"{path}:{line}: expected {expected} table cells, got {actual}; "
                r"escape literal pipes as \|.",
                file=sys.stderr,
            )
            failed = True
    if not failed:
        print("Markdown tables have no rows with discarded cells.")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
