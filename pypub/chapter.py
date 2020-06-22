"""
contains chapter object and chapter generating utilities
"""
import os
import html
import uuid
import imghdr
import requests
import lxml.html
import urllib.parse
from jinja2 import Template
from typing import Optional

from .const import log, validate, xmlprettify, SUPPORTED_TAGS

#** Variables **#
__all__ = [
    'Chapter',

    'create_chapter_from_url',
    'create_chapter_from_file',
    'create_chapter_from_string',
]

_session = requests.Session()
_session.headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'
}

#** Functions **#

def create_chapter_from_string(
    html:          str,
    title:         Optional[str] = None,
    url:           Optional[str] = None,
    title_xpath:   Optional[str] = None,
    content_xpath: Optional[str] = None,
) -> 'Chapter':
    """
    generate a chapter object from the given html string

    :param html:          html string making up chapter content
    :param title:         title used for the given chpater
    :param url:           url assigned to this particular chapter
    :param title_xpath:   xpath used to find title in html
    :param content_xpath: xpath used to find content in html
    """
    html  = '<div>%s</div>' % html
    etree = None
    # attempt to parse title if not given
    if not title:
        etree  = etree if etree is not None else lxml.html.fromstring(html)
        xpath  = (title_xpath or './/title').rsplit('text()', 1)[0] + '/text()'
        elem   = etree.xpath(xpath)
        # raise error if title-xpath failed
        if not elem and title_xpath:
            raise ValueError('no such title xpath: %r' % title_xpath)
        # assign title to new collection
        title  = elem[0] if elem else 'Epub Chapter'
    # attempt to parse content if given xml-path
    if content_xpath:
        etree = etree if etree is not None else lxml.html.fromstring(html)
        elem  = etree.xpath(content_xpath)
        # if no elements are found, raise error
        if len(elem) == 0:
            raise ValueError('no content w/ xpath: %s' % content_xpath)
        # if one element is found, set as root
        if len(elem) == 1:
            html = lxml.html.tostring(elem[0]).decode()
        # if multiple elements were found, append all to new root
        else:
            etree = lxml.html.fromstring('<div></div>')
            for child in elem:
                etree.append(child)
            html = lxml.html.tostring(etree).decode()
    # generate chapter object
    return Chapter(title, html, url)

def create_chapter_from_file(
    fpath:         str,
    title:         Optional[str] = None,
    url:           Optional[str] = None,
    title_xpath:   Optional[str] = None,
    content_xpath: Optional[str] = None,
) -> 'Chapter':
    """
    generate a chapter object from the given file

    :param fpath:         html file location making up chapter content
    :param title:         title used for the given chpater
    :param url:           url assigned to this particular chapter
    :param title_xpath:   xpath used to find title in html
    :param content_xpath: xpath used to find content in html
    """
    with open(fpath, 'r') as f:
        return create_chapter_from_string(f.read(),
            title, url, title_xpath, content_xpath)

def create_chapter_from_url(
    url:           str,
    title:         Optional[str] = None,
    title_xpath:   Optional[str] = None,
    content_xpath: Optional[str] = None,
) -> 'Chapter':
    """
    generate a chapter object from the given file

    :param url:           url being downloaded for html content
    :param title:         title used for the given chpater
    :param title_xpath:   xpath used to find title in html
    :param content_xpath: xpath used to find content in html
    """
    r = _session.get(url, timeout=10)
    return create_chapter_from_string(r.text,
        title, url, title_xpath, content_xpath)

#** Classes **#

class Chapter:
    """chapter object to be attached to epub"""

    def __init__(self, title: str, content: str, url: Optional[str] = None):
        """
        :param title:   title of the chapter
        :param content: content contained within the chapter
        :param url:     url from where the chapter content came from
        """
        validate('title', title, str)
        validate('content', content, str)
        self.title      = title
        self.content    = content
        self.url        = url
        self.html_title = html.escape(title)
        # additional attributes filled out by epub
        self.id         = None
        self.link       = None
        self.play_order = None
        self.etree      = None

    def _assign(self, id: int, link: str):
        """assign addtional epub specific attributes"""
        self.id         = 'page_%d' % id
        self.link       = link
        self.play_order = id
        self.etree      = self._new_etree()

    def _new_etree(self) -> Optional[lxml.html.HtmlElement]:
        """generate new filtered element-tree"""
        etree = lxml.html.fromstring(self.content)
        # check if we can minimalize the scope
        body    = etree.xpath('.//body')
        etree   = body[0] if body else etree
        article = etree.xpath('.//article')
        etree   = article[0] if article else etree
        # iterate elements in tree and delete/modify them
        for elem in [elem for elem in etree.iter()][1:]:
            # if element tag is supported
            if elem.tag in SUPPORTED_TAGS:
                # remove attributes not approved for specific tag
                for attr in elem.attrib:
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

    def _replace_images(self, image_dir: str):
        """replace image references w/ local downloaded ones"""
        _downloads = set()
        for img in self.etree.xpath('.//img[@src]'):
            # get full link for relative paths
            link = img.attrib['src'].rsplit('?', 1)[0]
            url  = urllib.parse.urljoin(self.url, link)
            # skip already completed downloads
            if url in _downloads:
                continue
            # attempt to download from url
            (head, fname, file) = (True, None, None)
            try:
                log.debug('chapter[%s] download img: %s' % (self.title, url))
                with _session.get(url, timeout=10, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=8192):
                        # check image-type in first chunk
                        if head:
                            head = False
                            mime = imghdr.what(None, h=chunk)
                            if not mime:
                                break
                            fname = '%s.%s' % (uuid.uuid4(), mime)
                            fpath = os.path.join(image_dir, fname)
                            file  = open(fpath, 'wb')
                        # write chunks to file if head was accepted
                        file.write(chunk)
            finally:
                if fname:
                    _downloads.add(url)
                    img.attrib['src'] = os.path.join('images/', fname)
                if file:
                    file.close()

    def _render(self, template: Template, image_dir: str, **kw: str) -> bytes:
        """render chapter content and attach it to the template"""
        # replace images in etree
        self._replace_images(image_dir)
        # render template and xml tree to attach elements to
        content = template.render(**kw, chapter=vars(self))
        etree   = lxml.html.fromstring(content.encode())
        # attach elements from chapter tree to complete template
        body = etree.xpath('.//body')[0]
        for elem in self.etree.getchildren():
            body.append(elem)
        # return html as string to be written
        xmlprettify(etree)
        return lxml.html.tostring(etree, method='xml')
