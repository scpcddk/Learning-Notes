"""Check automatic cloud-native discovery, duplicate routes and resource packaging."""
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import build_site


class CloudNativeReaderTests(unittest.TestCase):
    def setUp(self):
        self.scratch = build_site.PAGE_ROOT.parent / "review-output"
        self.scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="cloud-", dir=self.scratch)
        self.base = Path(self.temporary.name).resolve()
        assert self.base.parent == self.scratch.resolve()
        self.repo = self.base / "repo"
        self.notes = self.repo / "云原生"
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
            build_site.build_cloud_native(self.output, "https://github.com/example/notes", "main")
        text = (self.output / "cloud-native/index.html").read_text(encoding="utf-8")
        self.config = json.loads(re.search(r'id="language-data">(.*?)</script>', text, re.S)[1])
        self.pages = json.loads(build_site.DATA.search(text)[2])
        return text

    def test_discovery_updates_pending_sections_and_shared_template_paths(self):
        self.write("Docker/容器.md", "# 容器\n\n第一版。")
        self.write("DevOps/CI-CD.md", "# 交付\n\n发布记录。")
        for name in ("Kubernetes/Helm.md", "可观测性/Loki.md", "微服务.md", "数据库与中间件/Redis.md"):
            self.write(name, "")
        self.write("运维与服务部署/ANIC项目/环境.md", "# 环境\n\n实测记录。")
        text = self.build()
        self.assertEqual([s["title"] for s in self.config["sections"]],
                         ["Docker", "DevOps", "数据库与中间件", "运维与服务部署", "Kubernetes", "可观测性", "微服务"])
        self.assertEqual(self.config["pending"], 4)
        self.assertEqual(self.config["notes"], 3)
        self.assertNotIn("<!--HOME_URL-->", text)
        self.assertIn('href="../favicon.svg"', text)
        self.assertIn("../pdfjs/web/viewer.html", text)
        self.assertNotIn('href="../../"', text)
        self.assertNotIn('>编程语言</a>', text)
        original = next(p for p in self.pages if p["title"] == "容器")
        self.write("Docker/容器.md", "# 容器\n\n更新内容。")
        new = self.write("Docker/网络.md", "# 网络\n\n自动加入。")
        self.write("服务网格/起点.md", "# 起点\n\n新增板块。")
        self.build()
        changed = next(p for p in self.pages if p["title"] == "容器")
        self.assertEqual(changed["id"], original["id"])
        self.assertIn("更新内容", changed["full"])
        self.assertIn("服务网格", [s["title"] for s in self.config["sections"]])
        new.unlink()
        self.build()
        self.assertNotIn("网络", [p["title"] for p in self.pages])
        build_site.validate(self.output)

    def test_duplicate_aliases_headings_images_and_materials(self):
        manual = "# 部署\n\n## 验证\n\n相同的部署记录。"
        self.write("数据库与中间件/EMQX/部署.md", manual)
        self.write("运维与服务部署/换热站项目/部署.md", manual)
        self.write("数据库与中间件/EMQX/不同记录.md", manual + "\n新增了内容。")
        self.write("Docker/入口.md", '''# 入口

[去部署](../数据库与中间件/EMQX/部署.md#验证)

<img src="..\\数据库与中间件\\EMQX\\image.svg">

```sh
echo "$HOME ${APP_IMAGE}"
```
''')
        self.write("数据库与中间件/EMQX/image.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.write("数据库与中间件/EMQX/协议.pdf", "%PDF-1.7\n")
        self.write("数据库与中间件/EMQX/课件.pptx", "original slides")
        self.write("Docker/图解.html", "<!doctype html><html><body><h1>图解</h1></body></html>")
        self.write("数据库与中间件/MySQL/练习/基础练习.md", "# 基础练习\n\n独立作答。")
        self.build()
        self.assertEqual(next(p for p in self.pages if p["title"] == "基础练习")["kind"], "practice")
        self.assertEqual(len([p for p in self.pages if p["title"] == "部署"]), 1)
        target = next(p for p in self.pages if p["title"] == "部署")
        self.assertEqual(target["section"], "运维与服务部署")
        self.assertIn("不同记录", [p["title"] for p in self.pages])
        entry = next(p for p in self.pages if p["title"] == "入口")
        self.assertIn('href="#' + target["headings"][1]["id"] + '"', entry["full"])
        self.assertIn('src="assets/', entry["full"])
        self.assertIn("$HOME ${APP_IMAGE}", entry["full"])
        folder = self.output / "cloud-native"
        self.assertTrue((folder / "阅读资源/cloud-native-hero.png").is_file())
        self.assertEqual(len(list((folder / "assets").iterdir())), 1)
        for page in self.pages:
            for field in ("embed", "pdf"):
                if field in page:
                    self.assertTrue((folder / page[field]).is_file())
        build_site.validate(self.output)


if __name__ == "__main__":
    unittest.main()
