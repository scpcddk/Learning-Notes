"""Keep subject routes and repository links working after the engineering move."""
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote

import build_site


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.hrefs = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        if tag == 'a':
            self.hrefs.append(dict(attributes).get('href'))


class SoftwareEngineeringTests(unittest.TestCase):
    def test_subject_readers_are_reachable_from_catalogs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo, output = root/'repo', root/'site'
            sources = {
                '软件工程/计算机组成原理/笔记/数字逻辑.md': '[课件](../课件资源/讲义.pdf)\n\n公式 $x+y$。',
                '软件工程/软件需求与分析/课件/课程.md': '# 需求分析',
                '通识与拓展/思维/问题解决.md': '# 问题解决',
                '数学/概率论与数理统计/基础概念/事件.md': '# 随机事件\n\n概率 $P(A)$。',
            }
            for relative, content in sources.items():
                path = repo/relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
            pdf = repo/'软件工程/计算机组成原理/课件资源/讲义.pdf'
            pdf.parent.mkdir()
            pdf.write_bytes(b'%PDF-1.7\n')
            archive = pdf.with_name('附录.zip')
            archive.write_bytes(b'PK\x05\x06' + bytes(18))
            with patch.object(build_site, 'REPO', repo):
                subjects = build_site.build_subject_readers(output, 'https://github.com/example/notes', 'main')
                build_site.build_catalogs(output, 'https://github.com/example/notes', 'main', [], subjects)
            for catalog, href in [
                ('index.html', 'general-studies/'),
                ('math/index.html', '../probability-statistics/'),
                ('software-engineering/index.html', '../computer-organization/'),
                ('software-engineering/index.html', '../software-requirements/'),
            ]:
                self.assertIn(href, Links((output/catalog).read_text(encoding='utf-8')).hrefs)
                target = (output/catalog).parent / href / 'index.html'
                self.assertTrue(build_site.DATA.search(target.read_text(encoding='utf-8')))
            subject = output/'computer-organization'
            content = (subject/'index.html').read_text(encoding='utf-8')
            notes = json.loads(build_site.DATA.search(content)[2])
            note = next(entry for entry in notes if entry['format'] == 'MD')
            lecture = next(entry for entry in notes if entry['kind'] == 'pdf')
            self.assertTrue(note['math'])
            self.assertIn(f'href="#{lecture["id"]}"', note['full'])
            self.assertEqual((subject/lecture['pdf']).read_bytes(), pdf.read_bytes())
            download = next(entry for entry in notes if entry['format'] == 'ZIP')
            self.assertEqual((subject/download['download']).read_bytes(), archive.read_bytes())
            self.assertIn('../software-engineering/', Links(content).hrefs)

    def test_moved_subjects_keep_routes_and_use_new_source_paths(self):
        scratch = Path(tempfile.gettempdir())
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            self.assertTrue(Path(temporary).resolve().is_relative_to(scratch.resolve()))
            root = Path(temporary)
            repo, output = root/'repo', root/'site'
            engineering = repo/'软件工程'
            for relative in ['计算机组成原理/笔记', '计算机组成原理/课件资源', '计算机组成原理/习题',
                             '软件需求与分析/课件', '软件需求与分析/软需', '软件测试/练习']:
                (engineering/relative).mkdir(parents=True)
            with patch.object(build_site, 'REPO', repo):
                build_site.build_catalogs(output, 'https://github.com/example/notes', 'main', [])
            homepage = (output/'index.html').read_text(encoding='utf-8')
            hub = (output/'software-engineering/index.html').read_text(encoding='utf-8')
            computer = (output/'computer-organization/index.html').read_text(encoding='utf-8')
            requirements = (output/'software-requirements/index.html').read_text(encoding='utf-8')
            self.assertIn('软件工程与计算基础', homepage)
            self.assertIn('software-engineering/', Links(homepage).hrefs)
            self.assertIn('../computer-organization/', Links(hub).hrefs)
            self.assertIn('../software-requirements/', Links(hub).hrefs)
            self.assertIn('../software-engineering/', Links(computer).hrefs)
            self.assertIn('../software-engineering/', Links(requirements).hrefs)
            new_link = 'https://github.com/example/notes/tree/main/'+quote('软件工程/计算机组成原理/笔记')
            old_link = 'https://github.com/example/notes/tree/main/'+quote('计算机组成原理/笔记')
            self.assertIn(new_link, Links(computer).hrefs)
            self.assertNotIn(old_link, Links(computer).hrefs)
            self.assertIn('软件需求与分析', requirements)
            self.assertTrue((output/'software-engineering/阅读资源/software-engineering-hero-v2.webp').is_file())
            for slug, name, subject in [
                ('computer-organization', 'computer-organization-hero-v3.webp', computer),
                ('software-requirements', 'software-requirements-hero.webp', requirements),
            ]:
                resource = f'阅读资源/{name}'
                self.assertTrue((output/slug/resource).is_file())
                self.assertIn(f'src="../{slug}/{resource}"', hub)
                self.assertIn(f'src="{resource}"', subject)
            added_subject = next(href for href in Links(hub).hrefs if href and href.startswith('../software-')
                                 and href != '../software-requirements/')
            self.assertTrue((output/added_subject.removeprefix('../')/'index.html').is_file())


if __name__ == '__main__':
    unittest.main()
