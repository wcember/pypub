import cgi
import codecs

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
        try:
            assert file_name[-6:] == '.xhtml'
        except (AssertionError, IndexError):
            raise ValueError('filename must end with .xhtml')
        with open(file_name, 'wb') as f:
            f.write(self.content.encode('utf-8'))

    def _validate_input_types(self, content, title):
        try:
            assert isinstance(content, basestring)
        except AssertionError:
            raise TypeError('content must be a string')
        try:
            assert isinstance(title, basestring)
        except AssertionError:
            raise TypeError('title must be a string')
        try:
            assert title != ''
        except AssertionError:
            raise ValueError('title cannot be empty string')
        try:
            assert content != ''
        except AssertionError:
            raise ValueError('content cannot be empty string')


class ChapterFactory(object):

    def __init__(self, clean_function=clean.clean):
        self.clean_function = clean_function
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
        self.request_headers = {'User-Agent': user_agent}

    def create_chapter_from_url(self, url, title=None):
        request_object = requests.get(url, headers=self.request_headers)
        unicode_string = unicode(request_object.text, 'utf-8')
        return self.create_chapter_from_string(unicode_string, url, title)

    def create_chapter_from_file(self, file_name, url=None, title=None):
        with codecs.open(file_name, 'r', encoding='utf-8') as f:
            content_string = f.read()
        return self.create_chapter_from_string(content_string, url, title)

    def create_chapter_from_string(self, html_string, url=None, title=None):
        clean_html_string = self.clean_function(html_string)
        clean_xhtml_string = clean.html_to_xhtml(clean_html_string)
        if title:
            pass
        else:
            try:
                node = lxml.html.fromstring(html_string)
                title = node.xpath('//title')[0].text
            except IndexError:
                title = 'Ebook Chapter'
        return Chapter(clean_xhtml_string, title, url)