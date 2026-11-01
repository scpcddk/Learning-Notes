"""Check cover optimization without changing source art or embedded note content."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

import build_site


class CoverPerformanceTests(unittest.TestCase):
    def test_nested_readers_share_responsive_images_and_preserve_note_data(self):
        scratch = build_site.PAGE_ROOT.parent / 'review-output'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            output = Path(temporary).resolve()
            assets = output / 'images'
            assets.mkdir()
            original = assets / 'subject-hero-v2.png'
            Image.new('RGB', (1536, 1024), '#c5d8c2').save(original)
            Image.new('RGB', (100, 100), '#fff').save(assets / 'note.png')
            Image.new('RGB', (1536, 1024), '#eee').save(assets / 'unused-hero.png')
            checksum = hashlib.sha256(original.read_bytes()).hexdigest()
            reader = output / 'reader/index.html'
            reader.parent.mkdir()
            config = dict(coverUrl='../images/subject-hero-v2.png',
                          sections=[dict(cover='../images/subject-hero-v2.png')])
            note = dict(full='The original filename is subject-hero-v2.png.')
            reader.write_text(
                '<style data-design-system></style>'
                '<img src="../images/subject-hero-v2.png" loading="lazy">'
                '<img src="../images/note.png">'
                '<script type="application/json" id="language-data">' + json.dumps(config) + '</script>'
                '<script type="application/json" id="chapter-data">' + json.dumps([note]) + '</script>',
                encoding='utf-8')
            build_site.optimize_site_covers(output)
            text = reader.read_text(encoding='utf-8')
            converted = json.loads(build_site.READER_CONFIG.search(text)[2])
            self.assertTrue(converted['coverUrl'].endswith('-960.webp'))
            self.assertEqual(converted['coverUrl'], converted['sections'][0]['cover'])
            self.assertIn('loading="lazy"', text)
            self.assertIn('decoding="async"', text)
            self.assertIn('480w,', text)
            self.assertIn('960w,', text)
            self.assertIn('1440w"', text)
            self.assertIn('<img src="../images/note.png">', text)
            self.assertEqual(json.loads(build_site.DATA.search(text)[2]), [note])
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), checksum)
            self.assertEqual(len(list(assets.glob('*.webp'))), 3)
            for width in (480, 960, 1440):
                with Image.open(next(assets.glob(f'*-{width}.webp'))) as image:
                    self.assertEqual(image.size, (width, round(width * 2 / 3)))
            build_site.validate(output)
            build_site.optimize_site_covers(output)
            self.assertEqual(reader.read_text(encoding='utf-8'), text)

    def test_validator_rejects_missing_responsive_variant(self):
        scratch = build_site.PAGE_ROOT.parent / 'review-output'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            output = Path(temporary).resolve()
            Image.new('RGB', (480, 320)).save(output / 'small.webp')
            (output / 'index.html').write_text(
                '<img src="small.webp" srcset="small.webp 480w, missing.webp 960w">', encoding='utf-8')
            with self.assertRaises(FileNotFoundError):
                build_site.validate(output)
