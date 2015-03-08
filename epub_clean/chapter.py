import cgi
import lxml.html
import requests

import clean
import constants


class Chapter(object):

    def __init__(self, content, title, url=None):
        self._validate_input_types(content, title)
        self.title = title
        self.content = content
        self.url = url
        self.html_title = cgi.escape(self.title, quote=True)

    def write(self, file_name):
        with open(file_name, 'wb') as f:
            f.write(self.content.encode('unicode'))

    def _validate_input_types(self, content, title):
        try:
            assert isinstance(content, basestring)
        except AssertionError:
            raise TypeError('content must be a string')
        try:
            assert isinstance(title, basestring)
        except AssertionError:
            raise TypeError('title must be a string')


class ChapterFactory(object):

    def __init__(self, clean_function=clean.clean):
        self.clean_function = clean_function

    def create_chapter_from_url(self, url, title=None):
        request_object = requests.get(url)
        return self.create_chapter_from_string(request_object.text, title, url)

    def create_chapter_from_file(self, file_name, title):
        with open(file_name, 'r') as f:
            content_string = f.read()
        return Chapter(content_string, title)

    def create_chapter_from_string(self, html_string, title=None, url=None):
        clean_html_string = self.clean_function(html_string)
        if title:
            pass
        else:
            try:
                node = lxml.html.fromstring(html_string)
                title = node.xpath('//title')[0].text
            except IndexError:
                title = 'Ebook Chapter'
        return Chapter(clean_html_string, title, url)