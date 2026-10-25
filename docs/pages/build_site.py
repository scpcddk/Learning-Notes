"""Package the two reading pages for GitHub Pages without publishing source files.

Run the subject generators first, then:
    python docs/pages/build_site.py --output <site-directory>

The output is a static site. Repository links point back to GitHub, while the two
reading pages link to each other through stable, relative website routes.
"""
import argparse
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import quote, unquote, urlsplit

REPO = Path(__file__).resolve().parents[2]
SUBJECTS = (
    ("calculus", REPO / "数学/高等数学/阅读页面"),
    ("linear-algebra", REPO / "数学/线性代数/阅读页面"),
)
DATA = re.compile(r'(<script type="application/json" id="chapter-data">)([\s\S]*?)(</script>)')
HREF = re.compile(r'(?P<prefix>\bhref\s*=\s*)(?P<q>["\'])(?P<url>[^"\']*)(?P=q)')


def build(output, repository, branch):
    output = output.resolve()
    if output == REPO or REPO.is_relative_to(output):
        raise ValueError("The output must not replace the repository or its parent.")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Expected repository in owner/name format.")
    output.mkdir(parents=True, exist_ok=True)
    github = "https://github.com/" + repository
    targets = {(source / "速查笔记.html").resolve(): output / slug / "index.html"
               for slug, source in SUBJECTS}

    def link(url, source, destination):
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            return url
        # HTML fragments assembled at runtime are handled by their JSON source.
        if any(character in parts.path for character in ("'", '"', "+")):
            return url
        target = (source / unquote(parts.path)).resolve()
        if target in targets:
            relative = Path(os.path.relpath(targets[target].parent, destination)).as_posix()
            return relative + "/" + ("#" + parts.fragment if parts.fragment else "")
        if not target.is_relative_to(REPO):
            raise ValueError(f"Link outside repository: {url}")
        if not target.exists():
            raise FileNotFoundError(f"Missing link target: {target}")
        relative = quote(target.relative_to(REPO).as_posix())
        kind = "tree" if target.is_dir() else "blob"
        return f"{github}/{kind}/{quote(branch, safe='')}/{relative}" + (
            "#" + parts.fragment if parts.fragment else "")

    def markup(text, source, destination):
        return HREF.sub(lambda match: match["prefix"] + match["q"] +
                        link(match["url"], source, destination) + match["q"], text)

    for slug, source in SUBJECTS:
        destination = output / slug
        destination.mkdir(parents=True, exist_ok=True)
        text = (source / "速查笔记.html").read_text(encoding="utf-8")
        match = DATA.search(text)
        if not match:
            raise ValueError(f"No embedded note data in {source}")
        pages = json.loads(match[2])
        for page in pages:
            if page.get("source"):
                page["source"] = link(page["source"], source, destination)
            for field in ("summary", "full"):
                page[field] = markup(page[field], source, destination)
        payload = json.dumps(pages, ensure_ascii=False).replace("</", r"<\/")
        text = text[:match.start(2)] + "<!--PROTECTED_NOTE_DATA-->" + text[match.end(2):]
        text = markup(text, source, destination)
        text = text.replace("<!--PROTECTED_NOTE_DATA-->", payload)
        text = text.replace("<span>我的学习笔记</span>", '<a href="../">数学导航</a>')
        text = text.replace("</head>", '<link rel="icon" href="../favicon.svg" type="image/svg+xml"><style>.breadcrumb{min-width:0}.breadcrumb b{min-width:0;overflow:hidden;text-overflow:ellipsis}.breadcrumb>a,.top-actions{flex-shrink:0}</style></head>')
        (destination / "index.html").write_text(text, encoding="utf-8", newline="\n")
        shutil.copytree(source / "阅读资源", destination / "阅读资源", dirs_exist_ok=True)
        runtime = source / "阅读交互.js"
        if runtime.exists():
            (destination / runtime.name).write_text(
                markup(runtime.read_text(encoding="utf-8"), source, destination),
                encoding="utf-8", newline="\n")
        print(f"Packaged {slug}: {len(pages)} reading sections.")

    template = (REPO / "docs/pages/index.html").read_text(encoding="utf-8")
    template = template.replace("<!--REPO_URL-->", escape(github, quote=True))
    template = template.replace("<!--MATH_URL-->", escape(
        f"{github}/blob/{quote(branch, safe='')}/{quote('数学/README.md')}", quote=True))
    (output / "index.html").write_text(template, encoding="utf-8", newline="\n")
    shutil.copyfile(REPO / "docs/pages/site.css", output / "site.css")
    shutil.copyfile(REPO / "docs/pages/favicon.svg", output / "favicon.svg")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    validate(output)
    print("Validated static resources and page links.")


def validate(output):
    class ResourceParser(HTMLParser):
        def __init__(self, page):
            super().__init__()
            self.page = page

        def handle_starttag(self, tag, attributes):
            attrs = dict(attributes)
            target = attrs.get("href") if tag in ("a", "link") else attrs.get("src") if tag in ("script", "img") else None
            if not target:
                return
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                return
            path = (self.page.parent / unquote(parts.path)).resolve()
            if not path.is_relative_to(output) or not path.exists():
                raise FileNotFoundError(f"{self.page.name}: {target}")

    for page in output.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        parser = ResourceParser(page)
        parser.feed(text)
        match = DATA.search(text)
        if match:
            for entry in json.loads(match[2]):
                parser.feed(entry["summary"])
                parser.feed(entry["full"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "scpcddk/Learning-Notes"))
    parser.add_argument("--branch", default="main")
    arguments = parser.parse_args()
    build(arguments.output, arguments.repository, arguments.branch)
