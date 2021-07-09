"""
epub object defintion and script
"""
import os
import uuid
import shutil
import zipfile
import tempfile
from typing import Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from .const import *
from .chapter import Chapter

#** Variables **#
__all__ = ['Epub']

#** Classes **#

class Epub:
    """epub object used to genrate ebooks"""

    def __init__(self,
        title:     str,
        creator:   str = 'pypub',
        language:  str = 'en',
        rights:    str = '',
        publisher: str = 'pypub',
        date:      Optional[str] = None,
        cover:     Optional[str] = None,
        epub_dir:  Optional[str] = None,
    ):
        """
        :param title:     title of the book
        :param creator:   creator/author of the book
        :param language:  primary language of the book
        :param rights:    rights tied to publishing of this book
        :param publisher: name of publisher releasing book
        :param cover:     cover-image to be put on cover or release
        :param epub_dir:  directory used to generate epub in
        """
        validate('title', title, str)
        # primary attributes
        dt   = datetime.today()
        self.title       = title
        self.creator     = creator
        self.language    = language
        self.rights      = rights
        self.publisher   = publisher
        self.date        = date or datetime(dt.year, dt.month, dt.day).isoformat()
        self.uid         = uuid.uuid4()
        self.cover_image = cover
        # trackers
        self.chapter_id = 0
        self.chapters   = []
        # run startup functions
        self._increment_chapter()
        self._create_directories(epub_dir)

    def _increment_chapter(self):
        """increment chapter trackers"""
        self.chapter_id  += 1
        self.chapter_path = str(self.chapter_id) + '.xhtml'

    def _create_directories(self, epub_dir: str):
        """create directory varibles for epub components"""
        self.EPUB_DIR     = epub_dir or tempfile.mkdtemp()
        self.OEBPS_DIR    = os.path.join(self.EPUB_DIR, 'OEBPS')
        self.META_INF_DIR = os.path.join(self.EPUB_DIR, 'META-INF')
        self.IMAGE_DIR    = os.path.join(self.OEBPS_DIR, 'images')
        self.STYLE_DIR    = os.path.join(self.OEBPS_DIR, 'styles')

    @staticmethod
    def _generate_font(
        font:        str,
        text:        str,
        target_size: float,
        max_size:    int,
        max_width:   int
    ) -> ImageFont:
        """generate font with dynamic size based on the given criteria"""
        size = 5
        fnt = ImageFont.truetype(font, size)
        # iterate until the text size is just larger than the criteria
        while fnt.getsize(text)[0] <= target_size*max_width and size < max_size:
            size += 1
            fnt = ImageFont.truetype(font, size)
        return fnt

    def _generate_cover_image(self, opacity: int = 255):
        """generate dynamic cover-image w/ text"""
        assert opacity >= 0 and opacity < 256
        # get variables and generate new temporary cover image
        font_fill = fill=(255,255,255,opacity)
        cover_img = os.path.join(LOCAL_DIR, 'static/img/cover.png')
        cover_fnt = os.path.join(LOCAL_DIR, 'static/fonts/free_mono.ttf')
        with Image.open(cover_img).convert("RGBA") as base:
            # get dimensions of base-image in order to center text
            width, height = base.size
            # make a blank image for text, initialized to transparent text color
            txt = Image.new("RGBA", base.size, (255,255,255,0))
            # get a drawing context
            d = ImageDraw.Draw(txt)
            # write title text at top of cover
            text = self.title.title()
            fnt  = self._generate_font(cover_fnt, text, 0.9, 60, width)
            w, h = d.textsize(text, font=fnt)
            d.text(((width-w)/2, 10), text, font=fnt, fill=font_fill)
            # write author text at bottom of cover
            text = self.creator.title()
            fnt  = self._generate_font(cover_fnt, text, 0.5, 40, width)
            w, h = d.textsize(text, font=fnt)
            d.text(((width-w)/2, height-int(h*1.5)), text, font=fnt, fill=font_fill)
            # write output cover directly into epub directory
            self.cover_image = os.path.join(self.IMAGE_DIR, 'cover.png')
            out = Image.alpha_composite(base, txt)
            out.save(self.cover_image)

    def add_chapter(self, chapter: Chapter):
        """add a new chapter to the epub book"""
        chapter._assign(self.chapter_id, self.chapter_path)
        self.chapters.append(chapter)
        self._increment_chapter()

    def _generate(self):
        """generate the epub directory before compiling epub"""
        # make directories
        log.info('generating: %r (by: %s)' % (self.title, self.creator))
        os.makedirs(self.META_INF_DIR)
        os.makedirs(self.IMAGE_DIR)
        os.makedirs(self.STYLE_DIR)
        # write static-files
        log.info('epub=%r, generating static content' % self.title)
        copy_file('static/mimetype',          self.EPUB_DIR)
        copy_file('static/container.xml',     self.META_INF_DIR)
        copy_file('static/coverpage.xhtml',   self.OEBPS_DIR)
        copy_file('static/css/coverpage.css', self.STYLE_DIR)
        copy_file('static/css/styles.css',    self.STYLE_DIR)
        # get vars and start writing chapters
        log.info('epub=%r, writing chapter content' % self.title)
        epub_vars = vars(self)
        page_html = read_template('templates/page.xhtml.xml.j2')
        for n, chapter in enumerate(self.chapters, 1):
            log.info('rendering chapter #%d: %r' % (n, chapter.title))
            content = chapter._render(page_html, self.IMAGE_DIR, epub=epub_vars)
            with open(os.path.join(self.OEBPS_DIR, chapter.link), 'wb') as f:
                f.write(content)
        # handle cover-page generation/copying
        if self.cover_image is None:
            self._generate_cover_image()
        else:
            copy_image(self.cover_image, self.IMAGE_DIR, local=False)
        # handle cover-page vars
        cover_image = os.path.basename(self.cover_image)
        epub_vars['cover_img'] = cover_image
        epub_vars['cover_ext'] = self.cover_image.rsplit('.', 1)[-1]
        # update epub-vars with trackers for style files and image files
        epub_vars['styles'] = enumerate(os.listdir(self.STYLE_DIR), 0)
        epub_vars['images'] = [
            (i.rsplit('.', 1)[-1], i)
            for i in os.listdir(self.IMAGE_DIR)
            if i != cover_image
        ]
        log.info('epub=%r, writing final templates' % self.title)
        # render and write the rest of the templates
        render_template('templates/book.ncx.xml.j2', self.OEBPS_DIR, epub_vars)
        render_template('templates/book.opf.xml.j2', self.OEBPS_DIR, epub_vars)
        render_template('templates/toc.xhtml.xml.j2', self.OEBPS_DIR, epub_vars)

    def create_epub(self, output_dir: str = '.', fname: Optional[str] = None):
        """
        generate an epub book at the given directory w/ the given filename

        :param output_dir: directory epub will be written in
        :param fname:      name of book completed epub file
        """
        fname = (fname or self.title).rsplit('.epub', 1)[0] + '.epub'
        fpath = os.path.join(output_dir, fname)
        fzip  = fpath.rsplit('.epub', 1)[0] + '.zip'
        try:
            # generate epub directory
            self._generate()
            # start zipping contents
            log.info('epub=%r, zipping content' % self.title)
            zipf = zipfile.ZipFile(fzip, 'w', zipfile.ZIP_DEFLATED)
            path = self.EPUB_DIR.rstrip('/') + '/'
            for root, dirs, files in os.walk(path):
                fp = root.split(path, 1)[1]
                for file in files:
                    rootf  = os.path.join(root, file)
                    locf   = os.path.join(fp, file)
                    method = zipfile.ZIP_STORED if file == 'mimetype' else None
                    zipf.write(rootf, locf, method)
            # rename zip to epub
            zipf.close()
            os.rename(fzip, fpath)
        finally:
            shutil.rmtree(self.EPUB_DIR, ignore_errors=True)
