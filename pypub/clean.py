import cgi
import re

from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution

import constants

def clean(input_string,
        tag_dictionary=constants.SUPPORTED_TAGS):
    '''Compile a hex string into Script.

    Args:
        hex_string: A string or unicode string that is the hex representation
            of a bitcoin script.

    Returns:
        str: A bitcoin script formatted as a string.

    Raises:
        InvalidHexError: Raised if the input hex_string doesn't compile to
            valid Script.
        TypeError: Raised if the input hex_string isn't a string.

    Examples:
        >>> compile_hex('aa106fe28c0ab6f1b372c1a6a246ae63f74f87')
        'OP_HASH256 6fe28c0ab6f1b372c1a6a246ae63f74f OP_EQUAL'
        >>> compile_hex('76a90a134408afa258a50ed7a188ac')
        'OP_DUP OP_HASH160 134408afa258a50ed7a1 OP_EQUALVERIFY OP_CHECKSIG'
        >>> compile_hex('0504b0bd6342ac')
        '04b0bd6342 OP_CHECKSIG'
        >>> compile_hex('aa206fe28c0ab6f1b372c1a6a246ae63f74f931')
        InvalidHexError
    '''
    try:
        assert isinstance(input_string, basestring)
    except AssertionError:
        raise TypeError
    root = BeautifulSoup(input_string, 'html.parser')
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

def condense(input_string):
    '''Trims leadings and trailing whitespace between tags in an html document

    Args:
        input_string: A (possible unicode) string representing HTML.

    Returns:
        A (possibly unicode) string representing HTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    '''
    try:
        assert isinstance(input_string, basestring)
    except AssertionError:
        raise TypeError
    removed_leading_whitespace = re.sub('>\s+','>', input_string).strip()
    removed_trailing_whitespace = re.sub('\s+<','<', removed_leading_whitespace).strip()  #Need to fix this so replaces whitespace with words between tags
    return removed_trailing_whitespace

def html_to_xhtml(html_unicode_string):
    '''Converts html to xhtml

    Args:
        input_string: A (possible unicode) string representing HTML.

    Returns:
        A (possibly unicode) string representing XHTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    '''
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