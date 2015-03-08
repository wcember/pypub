import re

import bs4
import lxml.html

import constants

def clean(html_string, tags=constants.SUPORTED_TAGS ,pretty_print=False):
    try:
        assert isinstance(html_string, basestring)
    except AssertionError:
        raise TypeError
    html = lxml.html.fromstring(html_string)
    stack = html.getchildren()
    while stack:
        current_node = stack.pop()
        child_node_list = current_node.getchildren()
        if not current_node.tag in tags.keys():
            parent_node = current_node.getparent()
            parent_node.remove(current_node)
            for node in child_node_list:
                parent_node.insert(-1, node)
        else:
            attribute_dict = current_node.attrib
            for attribute in current_node.attrib.keys():
                if attribute not in tags[current_node.tag]:
                    attribute_dict.pop(attribute)
        stack.extend(child_node_list)
    unformatted_html_string = lxml.html.tostring(html,
            pretty_print=True,
            doctype='<!DOCTYPE html>',
            encoding='unicode')
    if pretty_print:
        return bs4.BeautifulSoup(unformatted_html_string).prettify()
    else:
        return unformatted_html_string


def condense(html_string):
    return re.sub('>\s+<','><',html_string).strip()