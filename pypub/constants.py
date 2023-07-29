import os

SUPPORTED_TAGS = {
    'a': ['href', 'id', 'name'],
    'b': ['id'],
    'big': [],
    'blockquote': ['id'],
    'body': [],
    'br': ['id'],
    'center': [],
    'cite': [],
    'dd': ['id', 'title'],
    'del': [],
    'dfn': [],
    'div': ['align', 'id', 'bgcolor'],
    'em': ['id', 'title'],
    'font': ['color', 'face', 'id', 'size'],
    'head': ['title'],  # this does not do anything, the top level title is what protects title in head
    'h1': [],
    'h2': [],
    'h3': [],
    'h4': [],
    'h5': [],
    'h6': [],
    'hr /': ['color', 'id', 'width'],
    'html': [],
    'i': ['class', 'id'],
    'img': ['align', 'border', 'height', 'id', 'src', 'width'],
    'img /': ['align', 'border', 'height', 'id', 'src', 'width'],
    'li': ['class', 'id', 'title'],
    'ol': ['id'],
    'p': ['align', 'id', 'title'],
    's': ['id', 'style', 'title'],
    'small': ['id'],
    'span': ['bgcolor', 'title'],
    'strike': ['class', 'id'],
    'strong': ['class', 'id'],
    'sub': ['id'],
    'sup': ['class', 'id'],
    'title': [],  # for inside head tag
    'u': ['id'],
    'ul': ['class', 'id'],
    'var': []
    }
SINGLETON_TAG_LIST = [
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'param',
    'source',
    ]
xhtml_doctype_string = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'test_files')
EPUB_TEMPLATES_DIR = os.path.join(BASE_DIR, 'epub_templates')
