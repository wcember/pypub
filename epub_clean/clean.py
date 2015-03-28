import re
import urlparse

import lxml.etree
import lxml.html

import constants

def get_content(input_unicode_string, base_url):
    '''Extracts text and image links from HTML unicode string.

    Extracts text and image links from HTML unicode string. Returns a list of
    tuples containing a tag followed by text content or an image location. Tags
    correspond to the tag of the node the text/image is from. If text between
    nodes, sets tag as u"p". Text is stripped of leading and trailing
    whitespace.

    input_unicode_string is not required to be a complete html document.

    Image locations are set to full urls

    Args:
        input_unicode_string: A unicode string representing HTML.
            Can be a fragment
        url: URL for which to base image links off. Must be a unicode string

    Returns:
        A list of tuples containing unicode. The first element of the tuple is
            an html tag. The second element of the tuple is unicode text or
            an image location.

    Raises:
        TypeError: Raised if input_unicode_string isn't of type unicode.
    '''
    try:
        assert type(input_unicode_string) == unicode
    except AssertionError:
        raise TypeError
    try:
        assert type(base_url) == unicode
    except AssertionError:
        raise TypeError
    node = lxml.html.fromstring(input_unicode_string)
    content_list = []
    for element in node.iter():
        if element.tail is not None:
            stripped_tail = element.tail.strip()
            if stripped_tail:
                content_list.append((u'p', stripped_tail))
        if element.text is not None:
            stripped_text = element.text.strip()
            if stripped_text:
                content_list.append((element.tag, stripped_text))
        elif element.tag == 'img':
            element_url = element['src']
            if urlparse.urlparse(element_url)['netloc'] == '':
                image_url = urlparse.urljoin(base_url, element_url)
            else:
                image_url = element_url
            content_list.append(('img', image_url))
    return content_list


def validate(xhtml_unicode_string):
    parser = lxml.etree.XMLParser(dtd_validation=True)
    return lxml.etree.fromstring(xhtml_unicode_string, parser)
