"""
Chapter Rendering Factory Implementation
"""
import os
import uuid
import urllib.error
import urllib.parse
import urllib.request
from logging import Logger
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Protocol

import imghdr
import pyxml.html
from pyxml.html import HtmlElement
from jinja2 import Template

from .chapter import Chapter, urlrequest, htmltostring

#** Variables **#
__all__ = [
    'SUPPORTED_TAGS',

    'urlrequest',
    'render_images',
    'xmlprettify',

    'RenderCtx', 
    'ChapterFactory', 
    'SimpleChapterFactory'
]

#: unicode characters to replace if found in content
REPLACE = dict([(ord(x), ord(y)) for x,y in zip(u"‘’´“”–-", u"'''\"\"--")])

#: supported tags and attributes allowed in an epub
SUPPORTED_TAGS = {
    'a':          ('href', 'id'),
    'b':          ('id', ),
    'big':        (),
    'blockquote': ('id', ),
    'body':       (),
    'br':         ('id', ),
    'center':     (),
    'cite':       (),
    'dd':         ('id', 'title'),
    'del':        (),
    'dfn':        (),
    'div':        ('align', 'id', 'bgcolor'),
    'em':         ('id', 'title'),
    'font':       ('color', 'face', 'id', 'size'),
    'head':       (),
    'h1':         (),
    'h2':         (),
    'h3':         (),
    'h4':         (),
    'h5':         (),
    'h6':         (),
    'html':       (),
    'i':          ('class', 'id'),
    'img':        ('align', 'border', 'height', 'id', 'src', 'width'),
    'li':         ('class', 'id', 'title'),
    'ol':         ('id', ),
    'p':          ('align', 'id', 'title'),
    's':          ('id', 'style', 'title'),
    'small':      ('id', ),
    'span':       ('bgcolor', 'title'),
    'strike':     ('class', 'id'),
    'strong':     ('class', 'id'),
    'sub':        ('id', ),
    'sup':        ('class', 'id'),
    'u':          ('id', ),
    'ul':         ('class', 'id'),
    'var':        (),
}

#** Functions **#

def render_images(ctx: 'RenderCtx', chunk_size: int = 8192):
    """
    replace global image references w/ local downloaded ones
    """
    downloads = {}
    for image in ctx.etree.xpath('.//img[@src]'):
        # cleanup link and resolve relative paths
        url = image.attrib['src'].rsplit('?', 1)[0]
        fmt = (ctx.chapter.title, url)
        if '://' not in url:
            if not ctx.chapter.url:
                ctx.logger.warning(
                    'chapter[%s] cannot render image %r w/o chapter-url' % fmt)
                continue
            url = urllib.parse.urljoin(ctx.chapter.url, url)
            fmt = (ctx.chapter.title, url)
        # skip if url has already been downloaded
        if url in downloads:
            image.attrib['src'] = downloads[url]
            continue
        # download url into local image folder for epub
        ctx.logger.debug(f'chapter[%s] downloading image: %r' % fmt)
        try:
            res = urlrequest(url, timeout=ctx.timeout)
            # ensure status of response is valid
            if res.status and res.status != 200:
                raise urllib.error.URLError(f'status: {res.status}')
            # read first chunk to determine content-type
            chunk = res.read(chunk_size)
            mime  = imghdr.what(None, h=chunk)
            if not mime:
                ctx.logger.warning('chapter[%s] cannot identify %r mime' % fmt)
                continue
            fname = f'{uuid.uuid4()}.{mime}'
            fpath = os.path.join(ctx.imagedir, fname)
            # read rest of the content into associated file
            with open(fpath, 'wb') as f:
                while chunk:
                    f.write(chunk)
                    chunk = res.read(chunk_size)
            # save epub-path in downloads cache and update image attribs
            epub_path = os.path.join('images/', fname)
            downloads[url] = epub_path
            image.attrib['src'] = epub_path
        except urllib.error.URLError:
            ctx.logger.error('chapter[%s] failed to download %r' % fmt)

def xmlprettify(elem: HtmlElement, chars: str='  ', level: int=1):
    """
    prettify the given element-tree w/ new indentations
    
    :param elem:  element being prettified
    :param chars: characters used for single indent
    :param level: internal variable used to track indent level
    """
    start    = '\n' + level * chars
    end      = '\n' + (level - 1) * chars
    children = elem.getchildren()
    if children:
        # make modifications
        if elem.text:
            elem.text = elem.text.rstrip() + start
        if elem.tail:
            elem.tail = elem.tail.rstrip() + end
        # iterate children
        for child in children:
            xmlprettify(child, chars, level + 1)
        # ensure last child has tail indentation of parent
        if children:
            child = children[-1]
            child.tail = (child.tail or '').rstrip() + end
    else:
        elem.text = '' if not elem.text else elem.text
        if elem.tail:
            elem.tail = (elem.tail or '').rstrip() + end

#** Classes **#

@dataclass
class RenderCtx:
    """variables and data associated w/ rendering a chapter"""
    logger:        Logger
    chapter:       Chapter
    etree:         HtmlElement
    imagedir:      str
    template:      Template
    render_kwargs: dict = field(default_factory=dict)
    timeout:       int  = 10

class ChapterFactory(Protocol):
    
    @abstractmethod
    def cleanup_html(self, content: bytes) -> HtmlElement:
        """
        cleanup raw html content and render as an lxml element tree
        """
        raise NotImplementedError

    @abstractmethod
    def hydrate(self, ctx: RenderCtx):
        """
        modify contents of chapter and etree before final rendering
        """
        raise NotImplementedError

    @abstractmethod
    def finalize(self, ctx: RenderCtx) -> bytes:
        """
        complete final rendering of chapter object and render as html bytes
        """
        raise NotImplementedError
   
    @abstractmethod
    def prettify(self, root: HtmlElement):
        """
        factory implementation to prettify etree at the end of finalization
        """
        raise NotImplementedError

    def render(self, log: Logger, chapter: Chapter, *args, **kwargs) -> bytes:
        """
        render chapter to bytes w/ the given settings
        """
        etree = self.cleanup_html(chapter.content)
        ctx   = RenderCtx(log, chapter, etree, *args, **kwargs)
        self.hydrate(ctx)
        return self.finalize(ctx)

class SimpleChapterFactory(ChapterFactory):
    """Simple Chapter Factory Implementation"""

    def cleanup_html(self, content: bytes) -> HtmlElement:
        """
        cleanup html content to only include supported tags
        """
        content = content.decode('utf-8', 'replace').translate(REPLACE).encode()
        # check if we can minimalize the scope
        etree   = pyxml.html.fromstring(content)
        body    = etree.xpath('.//body')
        etree   = body[0] if body else etree
        article = etree.xpath('.//article')
        etree   = article[0] if article else etree
        # iterate elements in tree and delete/modify them
        for elem in [elem for elem in etree.iter()][1:]:
            # if element tag is supported
            if elem.tag in SUPPORTED_TAGS:
                # remove attributes not approved for specific tag
                for attr in list(elem.attrib.keys()):
                    if attr not in SUPPORTED_TAGS[elem.tag]:
                        elem.attrib.pop(attr)
            # if element is not supported, append children to parent
            else:
                parent = elem.getparent()
                for child in elem.getchildren():
                    parent.append(child)
                parent.remove(elem)
                #NOTE: this is a bug with lxml, some children have
                # text in the parent included in the tail rather
                # than text attribute, so we also append tail to text
                if elem.tail and elem.tail.strip():
                    parent.text = (parent.text or '') + elem.tail.strip()
        # ensure all images with no src are removed
        for img in etree.xpath('.//img'):
            if 'src' not in img.attrib:
                img.getparent().remove(img)
        # return new element-tree
        return etree

    def hydrate(self, ctx: RenderCtx):
        """
        modify chapter element-tree to render images
        """
        render_images(ctx)
    
    def prettify(self, root: HtmlElement):
        """
        simple xml prettify function
        """
        xmlprettify(root)

    def finalize(self, ctx: RenderCtx) -> bytes:
        """
        render chapter content w/ specified template
        """
        content = ctx.template.render(**ctx.render_kwargs)
        # attach elements from chapter etree to content etree
        etree = pyxml.html.fromstring(content.encode())
        body  = etree.xpath('.//body')[0]
        for elem in ctx.etree.getchildren():
            body.append(elem)
        # return html as string to be written
        self.prettify(etree)
        return htmltostring(etree)
