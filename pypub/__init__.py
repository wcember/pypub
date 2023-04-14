"""
Epub library designed to build and generate ebooks in ePub format
"""
import sys
sys.path.insert(0, '../pyxml')

#** Variables **#
__all__ = [
    'Epub',
    'Assignment',
    'EpubBuilder',

    'Chapter',
    'ChapterFactory',
    'SimpleChapterFactory',

    'create_chapter_from_html',
    'create_chapter_from_text',
    'create_chapter_from_file',
    'create_chapter_from_url',
]

#** Imports **#
from .epub import Epub
from .builder import Assignment, EpubBuilder
from .chapter import *
from .factory import ChapterFactory, SimpleChapterFactory
