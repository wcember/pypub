import cgi
import codecs

from bs4 import BeautifulSoup
import requests

import clean
import constants


class Chapter(object):
    '''
    Class representing an ebook chapter. By and large this shouldn't be
    called directly but rather one should use the class ChapterFactor to
    instantiate a chapter.

    Args:
        content (str): The content of the chapter. Should be formatted as
            xhtml.
        title (str): The title of the chapter.
        url (Option[str]): The url of the webpage where the chapter is from if
            applicable. By default this is None.

    Attributes:
        content (str): The content of the ebook chapter.
        title (str): The title of the chapter.
        url (str): The url of the webpage where the chapter is from if
            applicable.
        html_title (str): Title string with special characters replaced with
            html-safe sequences
    '''
    def __init__(self, content, title, url=None):
        self._validate_input_types(content, title)
        self.title = title
        self.content = content
        self.url = url
        self.html_title = cgi.escape(self.title, quote=True)

    def write(self, file_name):
        '''Writes the chapter object to an xhtml file'''
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
    '''
    Used to create Chapter objects.Chapter objects can be created from urls,
    files, and strings.

    Args:
        clean_function (Option[function]): A function used to sanitize raw
            html to be used in an epub. By default, this is the pypub.clean
            function.
    '''

    def __init__(self, clean_function=clean.clean):
        self.clean_function = clean_function
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
        self.request_headers = {'User-Agent': user_agent}

    def create_chapter_from_url(self, url, title=None):
        '''
        Creates a Chapter object from a url. Pulls the webpage from the
        given url, sanitizes it using the clean_function method, and saves
        it as the content of the created chapter. Basic webpage loaded
        before any javascript executed.

        Args:
            url (string): The url to pull the content of the created Chapter
                from
            title (Option[string]): The title of the created Chapter. By
                default, this is None, in which case the title will try to be
                inferred from the webpage at the url.

        Returns:
            Chapter: A chapter object whose content is the webpage at the given
                url and whose title is that provided or inferred from the url
        '''
        request_object = requests.get(url, headers=self.request_headers)
        unicode_string = unicode(request_object.text, 'utf-8')
        return self.create_chapter_from_string(unicode_string, url, title)

    def create_chapter_from_file(self, file_name, url=None, title=None):
        '''
        Creates a Chapter object from an html or xhtml file. Sanitizes the
        file's content using the clean_function method, and saves
        it as the content of the created chapter.

        Args:
            file_name (string): The file_name containing the html or xhtml
                content of the created Chapter
            url (Option[string]): A url to infer the title of the chapter from
            title (Option[string]): The title of the created Chapter. By
                default, this is None, in which case the title will try to be
                inferred from the webpage at the url.

        Returns:
            Chapter: A chapter object whose content is the given file
                and whose title is that provided or inferred from the url
        '''
        with codecs.open(file_name, 'r', encoding='utf-8') as f:
            content_string = f.read()
        return self.create_chapter_from_string(content_string, url, title)

    def create_chapter_from_string(self, html_string, url=None, title=None):
        '''
        Creates a Chapter object from a string. Sanitizes the
        string using the clean_function method, and saves
        it as the content of the created chapter.

        Args:
            html_string (string): The html or xhtml content of the created
                Chapter
            url (Option[string]): A url to infer the title of the chapter from
            title (Option[string]): The title of the created Chapter. By
                default, this is None, in which case the title will try to be
                inferred from the webpage at the url.

        Returns:
            Chapter: A chapter object whose content is the given string
                and whose title is that provided or inferred from the url
        '''
        clean_html_string = self.clean_function(html_string)
        clean_xhtml_string = clean.html_to_xhtml(clean_html_string)
        if title:
            pass
        else:
            try:
                root = BeautifulSoup(html_string, 'html.parser')
                title_node = root.title
                title = unicode(title_node.string)
            except IndexError:
                title = 'Ebook Chapter'
        return Chapter(clean_xhtml_string, title, url)

create_chapter_from_url = ChapterFactory().create_chapter_from_url
create_chapter_from_file = ChapterFactory().create_chapter_from_file
create_chapter_from_string = ChapterFactory().create_chapter_from_string