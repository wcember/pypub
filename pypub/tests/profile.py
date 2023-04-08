"""
profile basic epub generation and return stats
"""
import os
import pstats
import logging
import unittest
import cProfile

from .. import Epub, create_chapter_from_url

#** Functions **#

def _create_epub():
    try:
        epub    = Epub('My First Epub')
        chapter = create_chapter_from_url('https://en.wikipedia.org/wiki/Grand_Teton_National_Park')
        epub.add_chapter(chapter)
        epub.create('./profile-test.epub')
    finally:
        try:
            os.remove('./profile-test.epub')
        except Exception:
            pass

#** Tests **#

class Profiling(unittest.TestCase):
    """profile based unit-tests"""

    def test_epub_profile(self):
        """complete profile on generating the given epub"""
        # enable profile
        pr = cProfile.Profile()
        pr.enable()
        # generate stats
        ps = pstats.Stats(pr, stream=_create_epub()).sort_stats('cumulative')
        ps.print_stats()
        # disable profile
        pr.disable()
        self.assertEqual(True, True)

#** Main **#

if __name__ == '__main__':
    logging.getLogger('pypub').setLevel(logging.DEBUG)
    unittest.main()
