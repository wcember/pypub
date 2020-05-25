import re

import bs4

from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution

from . import constants


def create_html_from_fragment(tag):
    """
    Creates full html tree from a fragment. Assumes that tag should be wrapped in a body and is currently not

    Args:
        tag: a bs4.element.Tag

    Returns:"
        bs4.element.Tag: A bs4 tag representing a full html document
    """

    try:
        assert isinstance(tag, bs4.element.Tag)
    except AssertionError:
        raise TypeError
    try:
        assert tag.find_all('body') == []
    except AssertionError:
        raise ValueError

    soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
    soup.body.append(tag)
    return soup


def clean(input_string,
          tag_dictionary=constants.SUPPORTED_TAGS):
    """
    Sanitizes HTML. Tags not contained as keys in the tag_dictionary input are
    removed, and child nodes are recursively moved to parent of removed node.
    Attributes not contained as arguments in tag_dictionary are removed.
    Doctype is set to <!DOCTYPE html>.

    Args:
        input_string (basestring): A (possibly unicode) string representing HTML.
        tag_dictionary (Option[dict]): A dictionary with tags as keys and
            attributes as values. This operates as a whitelist--i.e. if a tag
            isn't contained, it will be removed. By default, this is set to
            use the supported tags and attributes for the Amazon Kindle,
            as found at https://kdp.amazon.com/help?topicId=A1JPUWCSD6F59O

    Returns:
        str: A (possibly unicode) string representing HTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    """
    try:
        assert isinstance(input_string, str)
    except AssertionError:
        raise TypeError
    root = BeautifulSoup(input_string, 'html.parser')
    article_tag = root.find_all('article')
    if article_tag:
        root = article_tag[0]
    stack = root.findAll(True, recursive=False)
    while stack:
        current_node = stack.pop()
        child_node_list = current_node.findAll(True, recursive=False)
        if current_node.name not in list(tag_dictionary.keys()):
            parent_node = current_node.parent
            current_node.extract()
            for n in child_node_list:
                parent_node.append(n)
        else:
            attribute_dict = current_node.attrs
            for attribute in list(attribute_dict.keys()):
                if attribute not in tag_dictionary[current_node.name]:
                    attribute_dict.pop(attribute)
        stack.extend(child_node_list)
    #wrap partial tree if necessary
    if root.find_all('html') == []:
        root = create_html_from_fragment(root)
    # Remove img tags without src attribute
    image_node_list = root.find_all('img')
    for node in image_node_list:
        if not node.has_attr('src'):
            node.extract()
    unformatted_html_unicode_string = str(root.prettify(encoding='utf-8',
                                                            formatter=EntitySubstitution.substitute_html),
                                              encoding='utf-8')
    # fix <br> tags since not handled well by default by bs4
    unformatted_html_unicode_string = unformatted_html_unicode_string.replace('<br>', '<br/>')
    # remove &nbsp; and replace with space since not handled well by certain e-readers
    unformatted_html_unicode_string = unformatted_html_unicode_string.replace('&nbsp;', ' ')
    return unformatted_html_unicode_string


def condense(input_string):
    """
    Trims leadings and trailing whitespace between tags in an html document

    Args:
        input_string: A (possible unicode) string representing HTML.

    Returns:
        A (possibly unicode) string representing HTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    """
    try:
        assert isinstance(input_string, str)
    except AssertionError:
        raise TypeError
    removed_leading_whitespace = re.sub('>\s+', '>', input_string).strip()
    removed_trailing_whitespace = re.sub('\s+<', '<', removed_leading_whitespace).strip()
    return removed_trailing_whitespace


def html_to_xhtml(html_unicode_string):
    """
    Converts html to xhtml

    Args:
        html_unicode_string: A (possible unicode) string representing HTML.

    Returns:
        A (possibly unicode) string representing XHTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    """
    try:
        assert isinstance(html_unicode_string, str)
    except AssertionError:
        raise TypeError
    root = BeautifulSoup(html_unicode_string, 'html.parser')
    # Confirm root node is html
    try:
        assert root.html is not None
    except AssertionError:
        raise ValueError(''.join(['html_unicode_string cannot be a fragment.',
                         'string is the following: %s', str(root)]))
    # Add xmlns attribute to html node
    root.html['xmlns'] = 'http://www.w3.org/1999/xhtml'
    unicode_string = str(root.prettify(encoding='utf-8', formatter='html'), encoding='utf-8')
    # Close singleton tag_dictionary
    for tag in constants.SINGLETON_TAG_LIST:
        unicode_string = unicode_string.replace(
                '<' + tag + '/>',
                '<' + tag + ' />')
    return unicode_string
