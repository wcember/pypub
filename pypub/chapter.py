"""
Chapter Assignment and Processing Factories
"""
import html
import os.path
import urllib.request
from io import BytesIO
from dataclasses import dataclass
from typing import Optional

import pyxml.html

try:
    import mammoth
except ModuleNotFoundError:
    mammoth = None

#** Variables **#
__all__ = [
    'Chapter',

    'create_chapter_from_html',
    'create_chapter_from_text',
    'create_chapter_from_file',
    'create_chapter_from_url',
]

#: user agent to use when making url requests
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'

#** Classes **#

@dataclass(repr=False)
class Chapter:
    title:   str
    content: bytes
    url:     Optional[str] = None

    def __repr__(self) -> str:
        return 'Chapter(title=%r, url=%r, content=%d)' % (
            self.title, self.url, len(self.content))

#** Functions **#

def urlrequest(url: str, timeout: int = 10):
    """
    complete a url-request to the specified url
    """
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=timeout)

def htmltostring(root: pyxml.html.HtmlElement) -> bytes:
    """
    convert html to bytes
    """
    html = pyxml.html.tostring(root, method='xml')
    return html.encode() if isinstance(html, str) else html

def convert_text(text: str) -> bytes:
    """
    convert basic text into paragraphed html

    :param text: raw bytes text
    :return:     html version of text
    """
    root = pyxml.html.Element('body')
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        elem = pyxml.html.Element('p')
        elem.text = html.escape(line)
        root.append(elem)
    return htmltostring(root)

def convert_docx(data: bytes) -> bytes:
    """
    convert docx content into valid html

    :param data: docx archive bytes
    :return:     valid page html
    """
    if mammoth is None:
        raise ImportError(
            'cannot process `docx` without `mammoth`. Please pip install it')
    buffer = BytesIO(data)
    result = mammoth.convert_to_html(buffer)
    return result.value.encode()

def convert_content(path: str, data: bytes) -> bytes:
    """
    convert content according to the path extension

    :param path: path associated w/ data to denote data type
    :param data: raw bytes to process into html
    :return:     data processed into valid html
    """
    if path.endswith('.txt') or path.endswith('.text'):
        text = data.decode()
        return convert_text(text)
    elif path.endswith('.docx'):
        return convert_docx(data)
    return data

def create_chapter_from_html(
    html:          bytes,
    title:         Optional[str] = None,
    url:           Optional[str] = None,
    title_xpath:   Optional[str] = None,
    content_xpath: Optional[str] = None,
) -> Chapter:
    """
    generate a chapter object from the given html string

    :param html:          html string making up chapter content
    :param title:         title used for the given chpater
    :param url:           url assigned to this particular chapter
    :param title_xpath:   xpath used to find title in html
    :param content_xpath: xpath used to find content in html
    :return:              generated chapter object
    """
    html  = b'<html>' + html + b'</html>'
    etree = None
    # assign title according to title-xpath if specified
    if not title:
        etree = etree or pyxml.html.fromstring(html)
        xpath = (title_xpath or './/title').rsplit('/text()', 1)[0] + '/text()'
        elem  = etree.xpath(xpath)
        if not elem and title_xpath:
            raise ValueError(f'no such title: {title_xpath!r}')
        title = elem[0] if elem else 'Epub Chapter'
    # assign content according to content-xpath if specified
    if content_xpath:
        etree = etree or pyxml.html.fromstring(html)
        elem  = etree.xpath(content_xpath)
        root  = None
        if not len(elem):
            raise ValueError(f'no content at xpath: {content_xpath!r}')
        if len(elem) > 1:
            root = pyxml.html.Element('div')
            for child in elem:
                root.append(child)
        else:
            root = elem[0]
        html = htmltostring(root)
    # generate chapter object
    return Chapter(title, html, url)

def create_chapter_from_text(
    text:    str,
    title:   Optional[str] = None,
    url:     Optional[str] = None,
) -> Chapter:
    """
    generate a chapter object from the given text

    :param text:    text content to parse into chapter
    :param title:   assigned title of the chapter
    :param url:     url associated w/ the chapter
    """
    html = convert_text(text)
    return create_chapter_from_html(html, title, url)

def create_chapter_from_file(
    fpath:         str,
    title:         Optional[str] = None,
    url:           Optional[str] = None,
    title_xpath:   Optional[str] = None,
    content_xpath: Optional[str] = None,
) -> Chapter:
    """
    generate a chapter object from the given file

    :param fpath:         html file location making up chapter content
    :param title:         title used for the given chpater
    :param url:           url assigned to this particular chapter
    :param title_xpath:   xpath used to find title in html
    :param content_xpath: xpath used to find content in html
    """
    with open(fpath, 'rb') as f:
        url  = url or f'file://{os.path.abspath(fpath)}'
        html = convert_content(fpath, f.read())
        return create_chapter_from_html(html,
            title, url, title_xpath, content_xpath)

def create_chapter_from_url(
    url:           str,
    title:         Optional[str] = None,
    title_xpath:   Optional[str] = None,
    content_xpath: Optional[str] = None,
) -> Chapter:
    """
    generate a chapter object from the given file

    :param url:           url being downloaded for html content
    :param title:         title used for the given chpater
    :param title_xpath:   xpath used to find title in html
    :param content_xpath: xpath used to find content in html
    :param factory:       chapter factory override (for customization)
    """
    res  = urlrequest(url, timeout=10)
    html = convert_content(url, res.read())
    return create_chapter_from_html(html,
        title, url, title_xpath, content_xpath)
