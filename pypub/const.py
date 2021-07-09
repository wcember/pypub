"""
useful constants and internal utilities
"""
import os
import imghdr
import jinja2
import logging
import lxml.html

#** Variables **#
__all__ = [
    'VERSION',
    'LOCAL_DIR',
    'SUPPORTED_TAGS',

    'validate',
    'copy_file',
    'copy_image',
    'read_template',
    'render_template',
    'xmlprettify',

    'log',
]

VERSION = '2.0.0'
LOCAL_DIR = os.path.realpath(os.path.dirname(__file__))

SUPPORTED_TAGS = {
    'a':          ['href', 'id'],
    'b':          ['id'],
    'big':        [],
    'blockquote': ['id'],
    'body':       [],
    'br':         ['id'],
    'center':     [],
    'cite':       [],
    'dd':         ['id', 'title'],
    'del':        [],
    'dfn':        [],
    'div':        ['align', 'id', 'bgcolor'],
    'em':         ['id', 'title'],
    'font':       ['color', 'face', 'id', 'size'],
    'head':       [],
    'h1':         [],
    'h2':         [],
    'h3':         [],
    'h4':         [],
    'h5':         [],
    'h6':         [],
    'html':       [],
    'i':          ['class', 'id'],
    'img':        ['align', 'border', 'height', 'id', 'src', 'width'],
    'li':         ['class', 'id', 'title'],
    'ol':         ['id'],
    'p':          ['align', 'id', 'title'],
    's':          ['id', 'style', 'title'],
    'small':      ['id'],
    'span':       ['bgcolor', 'title'],
    'strike':     ['class', 'id'],
    'strong':     ['class', 'id'],
    'sub':        ['id'],
    'sup':        ['class', 'id'],
    'u':          ['id'],
    'ul':         ['class', 'id'],
    'var':        []
}

#** Functions **#

def _make_logger() -> logging.Logger:
    """generate logger for library"""
    logger    = logging.getLogger('pypub')
    c_handler = logging.StreamHandler()
    c_format  = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    c_handler.setLevel(logging.DEBUG)
    c_handler.setFormatter(c_format)
    logger.setLevel(logging.WARNING)
    logger.addHandler(c_handler)
    return logger

def validate(name: str, var: object, type: object):
    """raise type-error or value-error if wrong type or empty"""
    if not isinstance(var, type):
        raise TypeError('%s must be type: %s' % (name, type.__name__))
    if not var:
        raise ValueError('%s must not be null/empty' % name)

def copy_file(fpath: str, dir: str):
    """copy file from static"""
    fout = os.path.join(dir, os.path.basename(fpath))
    with open(os.path.join(LOCAL_DIR, fpath), 'rb') as fr:
        with open(fout, 'wb') as fw:
            while True:
                chunk = fr.read(8192)
                if not chunk:
                    break
                fw.write(chunk)

def copy_image(fpath: str, dir: str, local: bool = True):
    """copy image from static after confirming is image"""
    fout = os.path.join(dir, os.path.basename(fpath))
    with open(os.path.join(LOCAL_DIR, fpath) if local else fpath, 'rb') as fr:
        head = fr.read(20)
        if not imghdr.what(None, h=head):
            raise ValueError('invalid image: %s' % file1)
        # write content
        with open(fout, 'wb') as fw:
            fw.write(head)
            while True:
                chunk = fr.read(8192)
                if not chunk:
                    break
                fw.write(chunk)

def read_template(fpath: str) -> jinja2.Template:
    """read template from static file and return"""
    with open(os.path.join(LOCAL_DIR, fpath), 'r') as f:
        return jinja2.Template(f.read())

def render_template(fpath: str, dir: str, *args, **kwargs):
    """read content from the given filename and return template"""
    fout     = fpath.rsplit('.xml.j2', 1)[0]
    fout     = os.path.join(dir, os.path.basename(fout))
    template = read_template(fpath)
    with open(fout, 'w') as f:
        f.write( template.render(*args, **kwargs) )

def xmlprettify(elem: lxml.html.HtmlElement, chars: str='  ', _level: int=1):
    """
    prettify the given element-tree w/ new indentations

    :param elem:   element being prettified
    :param chars:  characters used for single indent
    :param _level: internal variable used to track indent level
    """
    start = '\n' + _level * chars
    end = '\n' + (_level - 1) * chars
    children = elem.getchildren()
    if children:
        # make modifications
        if elem.text:
            elem.text = elem.text.strip() + start
        if elem.tail:
            elem.tail = elem.tail.strip() + end
        # iterate children
        for child in children:
            xmlprettify(child, chars, _level + 1)
        # ensure last child has tail indentation of parent
        child.tail = (child.tail or '').strip() + end
    else:
        elem.text = '' if not elem.text else elem.text.strip()
        if elem.tail:
            elem.tail = (elem.tail or '').strip() + end

#** Init **#
log = _make_logger()
