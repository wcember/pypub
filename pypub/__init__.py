"""
epub library designed to build and generate ebooks in ePub format
"""

#** Variables **#
__all__ = [
    'Epub',
    'Chapter',

    'create_chapter_from_url',
    'create_chapter_from_file',
    'create_chapter_from_string'
]

from .epub import *
from .chapter import *
