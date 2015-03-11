import re

import lxml.etree
import lxml.html

import constants

def clean(input_string, output_type='HTML', tags=constants.SUPORTED_TAGS):
    try:
        assert isinstance(input_string, basestring)
    except AssertionError:
        raise TypeError
    try:
        assert output_type == 'HTML' or output_type == 'XHTML'
    except AssertionError:
        raise ValueError('output_type must be HTML or XHTML')
    if output_type == 'HTML':
        node = lxml.html.fromstring(input_string)
    else:
        parser = lxml.etree.XMLParser(encoding='utf-8', recover=True)
        node = lxml.etree.fromstring(input_string, parser=parser)
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
    if output_type == 'HTML':
        unformatted_html_string = lxml.html.tostring(node,
                pretty_print=True,
                doctype='<!DOCTYPE html>',
                encoding='utf-8')
        return unformatted_html_string
    else:
        unformatted_xhtml_string = lxml.etree.tostring(node,
                pretty_print=True,
                encoding='utf-8')


def condense(html_string):
    return unicode(re.sub('>\s+<','><',html_string).strip())

def html_to_xml(html_string):
    pass
