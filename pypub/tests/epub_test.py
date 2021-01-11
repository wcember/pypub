import os
import shutil
import unittest
from typing import List

from .. import *

#** Variables **#
static = os.path.realpath(os.path.join(os.path.dirname(__file__),'static'))

example_html = os.path.join(static, 'example.html')
example_book = os.path.join(static, 'example_book')

#** Tests **#

class EpubTests(unittest.TestCase):

    def setUp(self):
        """generate epub object for testing"""
        chapter   = create_chapter_from_file(example_html)
        self.epub = Epub('title')
        self.epub.add_chapter(chapter)

    def _walk(self, path: str) -> List[str]:
        """generate a list of files included in tree"""
        tree = set()
        for root, dirs, files in os.walk(path):
            fpath = root.split(path, 1)[1]
            for file in files:
                tree.add(os.path.join(fpath, file))
        return tree

    def test_create_epub(self):
        """generate an epub directory-tree ready for zipping"""
        try:
            self.epub._generate()
            tree1 = self._walk(self.epub.EPUB_DIR)
            tree2 = self._walk(example_book)
            self.assertEqual(tree1, tree2)
        finally:
            shutil.rmtree(self.epub.EPUB_DIR, True)

#** Main **#

if __name__ == '__main__':
    unittest.main()
