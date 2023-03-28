"""
Epub library designed to build and generate ebooks in ePub format
"""

#** Variables **#
__all__ = [
    'Epub',
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
from .chapter import *
from .factory import ChapterFactory, SimpleChapterFactory
