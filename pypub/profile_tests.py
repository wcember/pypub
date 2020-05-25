import cProfile
import pstats

from . import epub
from . import chapter

from .constants import *


def create_test_epub():
    my_first_epub = epub.Epub('My First Epub')
    my_first_chapter = chapter.create_chapter_from_url('https://en.wikipedia.org/wiki/Grand_Teton_National_Park')
    my_first_epub.add_chapter(my_first_chapter)
    my_first_epub.create_epub(os.path.join(TEST_DIR, 'epub_output'))

pr = cProfile.Profile()
pr.enable()

sortby = 'cumulative'
ps = pstats.Stats(pr, stream=create_test_epub()).sort_stats(sortby)
ps.print_stats()
