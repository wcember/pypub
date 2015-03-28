import re
import urlparse

import lxml.etree
import lxml.html

import constants

def clean(input_unicode_string,
        tag_dictionary=constants.SUPPORTED_TAGS):
    '''Sanitizes HTML.

    Sanitizes HTML. Tags not contained as keys in the tag_dictionary input are
    removed, and child nodes are recursively moved to parent of removed node.
    Attributes not contained as arguments in tag_dictionary are removed.

    Args:
        input_unicode_string: A unicode string representing HTML.
        tag_dictionary: A dictionary with tags as keys and attributes as
            values.

    Returns:
        A unicode string representing HTML. Doctype is set to <!DOCTYPE html>.

    Raises:
        TypeError: Raised if input_unicode_string isn't of type unicode.
    '''
    try:
        assert type(input_unicode_string) == unicode
    except AssertionError:
        raise TypeError
    node = lxml.html.fromstring(input_unicode_string)
    stack = node.getchildren()
    while stack:
        current_node = stack.pop()
        child_node_list = current_node.getchildren()
        if not current_node.tag in tag_dictionary.keys():
            parent_node = current_node.getparent()
            parent_node.remove(current_node)
            for n in child_node_list:
                parent_node.insert(-1, n)
        else:
            attribute_dict = current_node.attrib
            for attribute in current_node.attrib.keys():
                if attribute not in tag_dictionary[current_node.tag]:
                    attribute_dict.pop(attribute)
        stack.extend(child_node_list)
    unformatted_html_unicode_string = lxml.html.tostring(node,
            pretty_print=True,
            doctype='<!DOCTYPE html>',
            encoding='unicode')
    return unformatted_html_unicode_string


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


def condense(input_unicode_string):
    try:
        assert type(input_unicode_string) == unicode
    except AssertionError:
        raise TypeError
    return re.sub('>\s+<','><',input_unicode_string).strip()

def html_to_xhtml(html_unicode_string):
    try:
        assert type(html_unicode_string) == unicode
    except AssertionError:
        raise TypeError
    node = lxml.html.fromstring(html_unicode_string)
    #Confirm root node is html
    try:
        assert node.tag.lower() == 'html'
    except AssertionError:
        raise ValueError(''.join('html_unicode_string cannot be a fragment.',
                'Root node tag is %s', node.tag))
    #Add xmlns attribute to html node
    node.set('xmlns', 'http://www.w3.org/1999/xhtml')
    #Set DOCTYPE
    DOCTYPE_string = constants.xhtml_doctype_string
    string_with_open_singletons = lxml.etree.tostring(node, pretty_print=True,
            encoding='unicode', doctype=DOCTYPE_string)
    xhtml_unicode_string = string_with_open_singletons
    #close singleton tag_dictionary
    for tag in constants.SINGLETON_TAG_LIST:
        xhtml_unicode_string = xhtml_unicode_string.replace(
                '<' + tag + '/>',
                '<' + tag + ' />')
    return xhtml_unicode_string

def validate(xhtml_unicode_string):
    parser = lxml.etree.XMLParser(dtd_validation=True)
    return lxml.etree.fromstring(xhtml_unicode_string, parser)
