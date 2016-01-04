import re

from bs4 import BeautifulSoup
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
    root = BeautifulSoup(input_unicode_string, 'html.parser')
    stack = root.findAll(True, recursive=False)
##    node = lxml.html.fromstring(input_unicode_string)
##    stack = node.getchildren()
    while stack:
        current_node = stack.pop()
##        child_node_list = current_node.getchildren()
        child_node_list = current_node.findAll(True, recursive=False)
##        if not current_node.tag in tag_dictionary.keys():
        if not current_node.name in tag_dictionary.keys():
##            parent_node = current_node.getparent()
            parent_node = current_node.parent
##            parent_node.remove(current_node)
            current_node.extract()
            for n in child_node_list:
##                parent_node.insert(-1, n)
                parent_node.append(n)
        else:
##            attribute_dict = current_node.attrib
            attribute_dict = current_node.attrs
            for attribute in attribute_dict.keys():
##                if attribute not in tag_dictionary[current_node.tag]:
                if attribute not in tag_dictionary[current_node.name]:
                    attribute_dict.pop(attribute)
        stack.extend(child_node_list)
##    unformatted_html_unicode_string = lxml.html.tostring(node,
##            pretty_print=True,
##            doctype='<!DOCTYPE html>',
##            encoding='unicode')
    unformatted_html_unicode_string = unicode(root)
    return unformatted_html_unicode_string


def get_content(input_unicode_string):
    try:
        assert type(input_unicode_string) == unicode
    except AssertionError:
        raise TypeError
    node = lxml.html.fromstring(input_unicode_string)
    content_list = []
    for element in root.iter():
        if root.tail:
            content_list.append(root.tail)
        if root.text:
            content_list.append(root.text)
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
