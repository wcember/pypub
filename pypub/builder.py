"""
Epub Book Generator
"""
import os
import uuid
import shutil
import zipfile
import tempfile
import logging
from logging import Logger
from datetime import datetime
from dataclasses import dataclass, field
from typing import NamedTuple, Optional, Tuple, List

from PIL import Image, ImageDraw, ImageFont
from jinja2 import Environment, FileSystemLoader, Template

from .chapter import Chapter
from .factory import ChapterFactory, SimpleChapterFactory

#** Variables **#
__all__ = ['AssignedChapter', 'Assignment', 'EpubSpec', 'EpubBuilder']

#: assigned chapter type definition
AssignedChapter = Tuple['Assignment', Chapter]

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

def copy_file(src: str, into: str):
    """copy filepath into the `into` directory"""
    fname = os.path.basename(src)
    dst   = os.path.join(into, fname)
    shutil.copyfile(src, dst)

def copy_static(fpath: str, into: str):
    """copy static filepath into the `into` directory"""
    src = os.path.join(STATIC, fpath)
    copy_file(src, into)

def generate_font(text: str, target_ratio: float, maxsize: int, maxwidth: int):
    """generate font that fits the size of the image w/o overflow"""
    size = 5
    font = ImageFont.truetype(COVER_FONT, 5)
    # iterate until the text size is just larger than the criteria
    while font.getlength(text) <= target_ratio*maxwidth and size < maxsize:
        size += 1
        font = ImageFont.truetype(COVER_FONT, size)
    return font

def get_textsize(draw, text, font) -> Tuple[int, int]:
    """retrieve text-size of the current draw image"""
    if hasattr(draw, 'textbbox'):
        return draw.textbbox((0, 0), text, font=font)[2:]
    return draw.textsize(text, font=font)

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
        w, _ = get_textsize(draw, title, font=font)
        draw.text(((width-w)/2, 10), title, font=font, fill=fill)
        # draw author on the bottom of the cover
        font = generate_font(title, 0.5, 40, width)
        w, h = get_textsize(draw, author, font=font)
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
    basedir: str
    oebps:   str
    metainf: str
    images:  str
    styles:  str

class MimeFile(NamedTuple):
    name: str
    mime: str

@dataclass
class EpubSpec:
    """
    Epub Builder Specification
    """
    title:     str
    creator:   str            = 'pypub'
    language:  str            = 'en'
    rights:    str            = ''
    publisher: str            = 'pypub'
    date:      datetime       = field(default_factory=datetime.now)
    cover:     Optional[str]  = None
    epub_dir:  Optional[str]  = None
    factory:   ChapterFactory = field(repr=False, default_factory=SimpleChapterFactory)
    logger:    Logger         = field(repr=False, default=default_logger)
    css_paths: List[str]      = field(repr=False, default_factory=list)

class EpubBuilder:
    """
    Epub Builder Class for Constructing Epub Books
    """

    def __init__(self, epub: EpubSpec):
        self.uid     = str(uuid.uuid4())
        self.epub    = epub
        self.logger  = epub.logger
        self.factory = epub.factory
        self.dirs:     Optional[EpubDirs]    = None
        self.cover:    Optional[str]         = None
        self.template: Optional[Template]    = None
        self.chapters: List[AssignedChapter] = []
    
    def __enter__(self):
        """begin epub building in context-manager"""
        self.begin()
        return self

    def __exit__(self, *_):
        """cleanup on exit of context-manager"""
        self.cleanup()

    def begin(self) -> EpubDirs:
        """begin building operations w/ basic file structure"""
        if self.dirs:
            return self.dirs
        args = (self.epub.title, self.epub.creator)
        self.logger.info('generating: %r (by: %s)' % args)
        # generate base directories and copy static files
        self.dirs = epub_dirs(self.epub.epub_dir)
        copy_static('mimetype', self.dirs.basedir)
        copy_static('container.xml', self.dirs.metainf)
        copy_static('coverpage.xhtml', self.dirs.oebps)
        copy_static('css/coverpage.css', self.dirs.styles)
        copy_static('css/styles.css', self.dirs.styles)
        for path in self.epub.css_paths:
            copy_file(path, self.dirs.styles)
        # generate cover-image
        if self.epub.cover is not None:
            self.cover = os.path.basename(self.epub.cover)
            copy_file(self.epub.cover, self.dirs.images)
            return self.dirs 
        self.logger.info('generating cover-image (%r by %r)' % args)
        self.cover = generate_cover(*args, self.dirs.images)
        # read jinja2 chapter template
        self.template = jinja_env.get_template('page.xhtml.j2')
        return self.dirs

    def render_chapter(self, assign: Assignment, chapter: Chapter):
        """render an assigned chapter into the ebook"""
        if not self.dirs or not self.template:
            raise RuntimeError('cannot render_chapter before `begin`')
        # log chapter generation
        self.chapters.append((assign, chapter))
        self.logger.info('rendering chapter #%d: %r' % (
            assign.play_order, chapter.title))
        # render chapter w/ appropriate kwargs
        args    = (self.logger, chapter, self.dirs.images, self.template)
        kwargs  = {'epub': self.epub, 'chapter': chapter}
        fpath   = os.path.join(self.dirs.oebps, assign.link)
        content = self.factory.render(*args, kwargs)
        with open(fpath, 'wb') as f:
            f.write(content)

    def index(self):
        """build index files for epub before finalizing"""
        if not self.dirs or not self.cover:
            raise RuntimeError('cannot index epub before `begin`')
        kwargs = {
            'epub':     self.epub, 
            'cover':    MimeFile(self.cover, get_extension(self.cover)),
            'styles':   os.listdir(self.dirs.styles),
            'chapters': self.chapters,
            'images':   [
                MimeFile(fname, get_extension(fname))
                for fname in os.listdir(self.dirs.images)
                if fname != self.cover
            ]
        }
        # render and write the rest of the templates
        self.logger.info('epub=%r, writing final templates' % self.epub.title)
        render_template('book.ncx.j2', self.dirs.oebps, kwargs)
        render_template('book.opf.j2', self.dirs.oebps, kwargs)
        render_template('toc.xhtml.j2', self.dirs.oebps, kwargs)

    def compress(self, fpath: Optional[str] = None) -> str:
        """compress build and zip content into epub"""
        if not self.dirs:
            raise RuntimeError('cannot finalize before `begin`')
        # reformat and build fpath w/ defaults
        fname = os.path.basename(fpath) if fpath else self.epub.title
        fname = fname.rsplit('.epub', 1)[0] + '.epub'
        fpath = os.path.dirname(fpath) if fpath else '.'
        fpath = os.path.join(fpath, fname)
        fzip  = fpath.rsplit('.epub', 1)[0] + '.zip'
        # zip contents of directory 
        self.logger.info('epub=%r, zipping content' % self.epub.title)
        zipf = zipfile.ZipFile(fzip, 'w', zipfile.ZIP_DEFLATED)
        for root, _, files in os.walk(self.dirs.basedir):
            relpath = root.split(self.dirs.basedir, 1)[1]
            for file in files:
                real   = os.path.join(root, file)
                local  = os.path.join(relpath, file)
                method = zipfile.ZIP_STORED if file == 'mimetype' else None
                zipf.write(real, local, method)
        # rename zip to epub
        zipf.close()
        os.rename(fzip, fpath)
        return fpath

    def finalize(self, fpath: Optional[str] = None) -> str:
        """finalize build and index and compress epub directory"""
        self.index()
        return self.compress(fpath)

    def cleanup(self):
        """cleanup leftover resources after finalization"""
        if self.dirs:
            shutil.rmtree(self.dirs.basedir, ignore_errors=True)
            self.dirs = None
