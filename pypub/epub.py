"""
Epub Object Definition and Generation
"""
from dataclasses import dataclass, field
from typing import Optional, List, Type

from .chapter import Chapter
from .builder import AssignedChapter, Assignment, EpubSpec, EpubBuilder

#** Variables **#
__all__ = ['Epub']

#** Classes **#

@dataclass
class Epub(EpubSpec):
    builder_factory: Type[EpubBuilder] = field(repr=False, default=EpubBuilder)

    def __post_init__(self):
        self.chapters: List[AssignedChapter] = []
        self.last_chapter = 1
        self.builder      = self.builder_factory(self)
    
    def assign_chapter(self) -> Assignment:
        """
        retrieve a valid assignment for an ebook chapter

        :return: chapter assignment information
        """
        id         = f'chapter_{self.last_chapter}'
        order      = self.last_chapter
        link       = f'{self.last_chapter}.xhtml'
        assignment = Assignment(id, link, order)
        self.last_chapter += 1
        return assignment

    def add_chapter(self, chapter: Chapter):
        """
        add a chapter to the ebook for later generation

        :param chapter: chapter to add to epub
        """
        assignment = self.assign_chapter()
        self.chapters.append((assignment, chapter))
        self.logger.debug(f'epub=%r added chapter %d: %r' % (
            self.title, assignment.play_order, chapter.title))

    def build_epub_dir(self) -> str:
        """
        generate and compile an uncompressed epub build directory

        :return: directory of epub content
        """
        dirs = self.builder.begin()
        for assign, chapter in self.chapters:
            self.builder.render_chapter(assign, chapter)
        self.builder.index()
        return dirs.basedir 
 
    def create(self, fpath: Optional[str] = None) -> str:
        """
        generate an epub book at the given filepath

        :param fpath: filepath of finalized epub
        :return:      filepath of finished epub
        """
        try:
            self.build_epub_dir()
            return self.builder.compress(fpath)
        finally:
            self.builder.cleanup()
