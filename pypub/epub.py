"""
Epub Object Definition and Generation
"""
import os
import uuid
import shutil
import tempfile
import zipfile
import logging
from logging import Logger
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, NamedTuple

from PIL import Image, ImageDraw, ImageFont
from jinja2 import Environment, FileSystemLoader

from .chapter import Chapter
from .factory import ChapterFactory, SimpleChapterFactory

#** Variables **#
__all__ = ['Epub']

#: base library directory
BASE = os.path.dirname(__file__)

#: static directory path
STATIC = os.path.join(BASE, 'static/')

#: templates directory to render content from
TEMPLATES = os.path.join(BASE, 'templates/')

#: base image used to generate cover
COVER_IMG = os.path.join(STATIC, 'img/cover.png')

#: font used to generater cover text
COVER_FONT = os.path.join(STATIC, 'fonts/free_mono.ttf')

#: jinja2 environment to load templates
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES))

#: default logging instance for library
default_logger = logging.getLogger('pypub')

#** Functions **#

def epub_dirs(basedir: Optional[str] = None) -> 'EpubDirs':
    """generate directories for epub data"""
    basedir = basedir or tempfile.mkdtemp()
    oebps   = os.path.join(basedir, 'OEBPS')
    metainf = os.path.join(basedir, 'META-INF')
    images  = os.path.join(oebps, 'images')
    styles  = os.path.join(oebps, 'styles')
    os.makedirs(oebps)
    os.makedirs(metainf)
    os.makedirs(images)
    os.makedirs(styles)
    return EpubDirs(basedir, oebps, metainf, images, styles)

def copy_static(fpath: str, into: str):
    """copy static filepath into the `into` directory"""
    fname = os.path.basename(fpath)
    src   = os.path.join(STATIC, fpath)
    dst   = os.path.join(into, fname)
    shutil.copyfile(src, dst)

def generate_font(text: str, target_ratio: float, maxsize: int, maxwidth: int):
    """generate font that fits the size of the image w/o overflow"""
    size = 5
    font = ImageFont.truetype(COVER_FONT, 5)
    # iterate until the text size is just larger than the criteria
    while font.getlength(text) <= target_ratio*maxwidth and size < maxsize:
        size += 1
        font = ImageFont.truetype(COVER_FONT, size)
    return font

def generate_cover(title: str, author: str, images: str) -> str:
    """generate cover image using PIL text overlay"""
    title  = title.title()
    author = author.title()
    fill   = (255, 255, 255, 255)
    with Image.open(COVER_IMG).convert("RGBA") as image:
        width, height = image.size
        draw = ImageDraw.Draw(image)
        # draw title on the top of the cover
        font = generate_font(title, 0.9, 60, width)
        w, _ = draw.textsize(title, font=font)
        draw.text(((width-w)/2, 10), title, font=font, fill=fill)
        # draw author on the bottom of the cover
        font = generate_font(title, 0.5, 40, width)
        w, h = draw.textsize(author, font=font)
        draw.text(((width-w)/2, height-int(h*1.5)), author, font=font, fill=fill)
        # write cover directly into epub directory
        fpath = os.path.join(images, 'cover.png')
        image.save(fpath)
        return 'cover.png'

def get_extension(fname: str) -> str:
    """get extension of the given filename"""
    return fname.rsplit('.', 1)[-1]

def render_template(name: str, into: str, kwargs: dict):
    """render template in templates directory"""
    fname    = name.rsplit('.j2', 1)[0]
    dest     = os.path.join(into, os.path.basename(fname))
    template = jinja_env.get_template(name)
    content  = template.render(**kwargs)
    with open(dest, 'w') as f:
        f.write(content)

#** Classes **#

@dataclass
class Assignment:
    id:         str
    link:       str
    play_order: int

@dataclass
class EpubDirs:
    """epub directory structure"""
    basedir: str
    oebps:   str
    metainf: str
    images:  str
    styles:  str

class MimeFile(NamedTuple):
    name: str
    mime: str

@dataclass
class Epub:
    title:     str
    creator:   str            = 'pypub'
    language:  str            = 'en'
    rights:    str            = ''
    publisher: str            = 'pypub'
    date:      datetime       = field(default_factory=datetime.today) 
    cover:     Optional[str]  = None
    epub_dir:  Optional[str]  = None
    factory:   ChapterFactory = field(repr=False, default_factory=SimpleChapterFactory)
    logger:    Logger         = field(repr=False, default=default_logger)

    def __post_init__(self):
        self.uid:          str                              = str(uuid.uuid4())
        self.chapters:     List[Tuple[Assignment, Chapter]] = []
        self.last_chapter: int                              = 1

    def add_chapter(self, chapter: Chapter):
        """
        add a chapter to the ebook for later generation

        :param chapter: chapter to add to epub
        """
        # generate assignment
        id         = f'chapter_{self.last_chapter}'
        order      = self.last_chapter
        link       = f'{self.last_chapter}.xhtml'
        assignment = Assignment(id, link, order)
        # add assignment to chapters registry and update counter
        self.chapters.append((assignment, chapter))
        self.last_chapter += 1
        self.logger.debug(f'epub=%r added chapter %d: %r' % (
            self.title, order, chapter.title))

    def build_epub_dir(self, dirs: EpubDirs):
        """
        generate and compile an uncompressed epub build directory
        """
        self.logger.info('generating: %r (by: %s)' % (self.title, self.creator))
        # copy static files into directories
        copy_static('mimetype', dirs.basedir)
        copy_static('container.xml', dirs.metainf)
        copy_static('coverpage.xhtml', dirs.oebps)
        copy_static('css/coverpage.css', dirs.styles)
        copy_static('css/styles.css', dirs.styles)
        # render templates for chapters into directory
        template = jinja_env.get_template('page.xhtml.j2')
        for n, (assign, chapter) in enumerate(self.chapters, 1):
            self.logger.info('rendering chapter: #%d: %r' % (n, chapter.title))
            args    = (self.logger, chapter, dirs.images, template)
            kwargs  = {'epub': self, 'chapter': chapter}
            fpath   = os.path.join(dirs.oebps, assign.link)
            content = self.factory.render(*args, kwargs)
            with open(fpath, 'wb') as f:
                f.write(content)
        # generate cover-image
        self.logger.info('generating cover-image (%r by %r)' % (
            self.title, self.creator))
        cover_image = generate_cover(self.title, self.creator, dirs.images)
        # generate kwargs for the rest of the templates
        kwargs = {
            'epub':   self, 
            'cover':  MimeFile(cover_image, get_extension(cover_image)),
            'styles': os.listdir(dirs.styles),
            'images': [
                MimeFile(fname, get_extension(fname))
                for fname in os.listdir(dirs.images)
                if fname != cover_image
            ]
        }
        # render and write the rest of the templates
        self.logger.info('epub=%r, writing final templates' % self.title)
        render_template('book.ncx.j2', dirs.oebps, kwargs)
        render_template('book.opf.j2', dirs.oebps, kwargs)
        render_template('toc.xhtml.j2', dirs.oebps, kwargs)
    
    def create(self, fpath: Optional[str] = None) -> str:
        """
        generate an epub book at the given filepath

        :param fpath: filepath of finalized epub
        :return:      filepath of finished epub
        """
        # reformat and build fpath w/ defaults
        fname = os.path.basename(fpath) if fpath else self.title
        fname = fname.rsplit('.epub', 1)[0] + '.epub'
        fpath = os.path.dirname(fpath) if fpath else '.'
        fpath = os.path.join(fpath, fname)
        fzip  = fpath.rsplit('.epub', 1)[0] + '.zip'
        # generate epub and zip contents
        dirs = epub_dirs(self.epub_dir)
        try:
            # build unzipped content directory
            self.build_epub_dir(dirs)
            # zip contents of directory 
            self.logger.info('epub=%r, zipping content' % self.title)
            zipf = zipfile.ZipFile(fzip, 'w', zipfile.ZIP_DEFLATED)
            for root, _, files in os.walk(dirs.basedir):
                relpath = root.split(dirs.basedir, 1)[1]
                for file in files:
                    real   = os.path.join(root, file)
                    local  = os.path.join(relpath, file)
                    method = zipfile.ZIP_STORED if file == 'mimetype' else None
                    zipf.write(real, local, method)
            # rename zip to epub
            zipf.close()
            os.rename(fzip, fpath)
            return fpath
        finally:
            shutil.rmtree(dirs.basedir, ignore_errors=True)
