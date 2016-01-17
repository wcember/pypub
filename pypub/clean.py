import cgi
import re

from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution
import lxml.etree
import lxml.html

import constants

def unicode_to_html_entities(text):
    '''Converts unicode to HTML entities.  For example '&' becomes '&amp;'''
##    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    text = EntitySubstitution.substitute_html(text)
    return text

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
    while stack:
        current_node = stack.pop()
        child_node_list = current_node.findAll(True, recursive=False)
        if not current_node.name in tag_dictionary.keys():
            parent_node = current_node.parent
            current_node.extract()
            for n in child_node_list:
                parent_node.append(n)
        else:
            attribute_dict = current_node.attrs
            for attribute in attribute_dict.keys():
                if attribute not in tag_dictionary[current_node.name]:
                    attribute_dict.pop(attribute)
        stack.extend(child_node_list)
    unformatted_html_unicode_string = unicode(root.prettify(encoding='utf-8', formatter=EntitySubstitution.substitute_html), encoding = 'utf-8')
    #fix <br> tags since not handled well by default by bs4
    unformatted_html_unicode_string = unformatted_html_unicode_string.replace('<br>', '<br/>')
    return unformatted_html_unicode_string


##def get_content(input_unicode_string):
##    try:
##        assert type(input_unicode_string) == unicode
##    except AssertionError:
##        raise TypeError
##    node = lxml.html.fromstring(input_unicode_string)
##    content_list = []
##    for element in root.iter():
##        if root.tail:
##            content_list.append(root.tail)
##        if root.text:
##            content_list.append(root.text)
##    return content_list


def condense(input_unicode_string):
    try:
        assert type(input_unicode_string) == unicode
    except AssertionError:
        raise TypeError
    return re.sub('>\s+<','><',input_unicode_string).strip()

def html_to_xhtml(html_unicode_string):
    try:
        assert isinstance(html_unicode_string, basestring)
    except AssertionError:
        raise TypeError
    root = BeautifulSoup(html_unicode_string, 'html.parser')
    #Confirm root node is html
    try:
        assert root.html is not None
    except AssertionError:
        raise ValueError(''.join(['html_unicode_string cannot be a fragment.',
                'string is the following: %s', unicode(root)]))
    #Add xmlns attribute to html node
    root.html['xmlns'] = 'http://www.w3.org/1999/xhtml'
    unicode_string = unicode(root.prettify(encoding='utf-8', formatter='html'), encoding = 'utf-8')
    #close singleton tag_dictionary
    for tag in constants.SINGLETON_TAG_LIST:
        unicode_string = unicode_string.replace(
                '<' + tag + '/>',
                '<' + tag + ' />')
    return unicode_string

##def validate(xhtml_unicode_string):
##    parser = lxml.etree.XMLParser(dtd_validation=True)
##    return lxml.etree.fromstring(xhtml_unicode_string, parser)
