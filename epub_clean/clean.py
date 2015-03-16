import re

import lxml.etree
import lxml.html

import constants

def clean(input_unicode_string, tags=constants.SUPORTED_TAGS):
    try:
        assert type(input_unicode_string) == unicode
    except AssertionError:
        raise TypeError
    node = lxml.html.fromstring(input_unicode_string)
    stack = node.getchildren()
    while stack:
        current_node = stack.pop()
        child_node_list = current_node.getchildren()
        if not current_node.tag in tags.keys():
            parent_node = current_node.getparent()
            parent_node.remove(current_node)
            for n in child_node_list:
                parent_node.insert(-1, n)
        else:
            attribute_dict = current_node.attrib
            for attribute in current_node.attrib.keys():
                if attribute not in tags[current_node.tag]:
                    attribute_dict.pop(attribute)
        stack.extend(child_node_list)
    unformatted_html_unicode_string = lxml.html.tostring(node,
            pretty_print=True,
            doctype='<!DOCTYPE html>',
            encoding='unicode')
    return unformatted_html_unicode_string


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
    #close singleton tags
    xhtml_unicode_string = string_with_open_singletons.replace('<br/>', '<br />')
    return xhtml_unicode_string
