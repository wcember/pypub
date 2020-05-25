import cgi
import codecs
import imghdr
import os
import shutil
import tempfile
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import uuid

import bs4
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution
import requests

from . import clean


class NoUrlError(Exception):
    def __str__(self):
        return 'Chapter instance URL attribute is None'


class ImageErrorException(Exception):
    def __init__(self, image_url):
        self.image_url = image_url

    def __str__(self):
        return 'Error downloading image from ' + self.image_url


def get_image_type(url):
    for ending in ['jpg', 'jpeg', '.gif' '.png']:
        if url.endswith(ending):
            return ending
    else:
        try:
            f, temp_file_name = tempfile.mkstemp()
            urllib.request.urlretrieve(url, temp_file_name)
            image_type = imghdr.what(temp_file_name)
            return image_type
        except IOError:
            return None


def save_image(image_url, image_directory, image_name):
    """
    Saves an online image from image_url to image_directory with the name image_name.
    Returns the extension of the image saved, which is determined dynamically.

    Args:
        image_url (str): The url of the image.
        image_directory (str): The directory to save the image in.
        image_name (str): The file name to save the image as.

    Raises:
        ImageErrorException: Raised if unable to save the image at image_url
    """
    image_type = get_image_type(image_url)
    if image_type is None:
        raise ImageErrorException(image_url)
    full_image_file_name = os.path.join(image_directory, image_name + '.' + image_type)

    # If the image is present on the local filesystem just copy it
    if os.path.exists(image_url):
        shutil.copy(image_url, full_image_file_name)
        return image_type

    try:
        # urllib.urlretrieve(image_url, full_image_file_name)
        with open(full_image_file_name, 'wb') as f:
            user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
            request_headers = {'User-Agent': user_agent}
            requests_object = requests.get(image_url, headers=request_headers)
            try:
                content = requests_object.content
                # Check for empty response
                f.write(content)
            except AttributeError:
                raise ImageErrorException(image_url)
    except IOError:
        raise ImageErrorException(image_url)
    return image_type


def _replace_image(image_url, image_tag, ebook_folder,
                   image_name=None):
    """
    Replaces the src of an image to link to the local copy in the images folder of the ebook. Tightly coupled with bs4
        package.

    Args:
        image_url (str): The url of the image.
        image_tag (bs4.element.Tag): The bs4 tag containing the image.
        ebook_folder (str): The directory where the ebook files are being saved. This must contain a subdirectory
            called "images".
        image_name (Option[str]): The short name to save the image as. Should not contain a directory or an extension.
    """
    try:
        assert isinstance(image_tag, bs4.element.Tag)
    except AssertionError:
        raise TypeError("image_tag cannot be of type " + str(type(image_tag)))
    if image_name is None:
        image_name = str(uuid.uuid4())
    try:
        image_full_path = os.path.join(ebook_folder, 'images')
        assert os.path.exists(image_full_path)
        image_extension = save_image(image_url, image_full_path,
                                     image_name)
        image_tag['src'] = 'images' + '/' + image_name + '.' + image_extension
    except ImageErrorException:
        image_tag.decompose()
    except AssertionError:
        raise ValueError('%s doesn\'t exist or doesn\'t contain a subdirectory images' % ebook_folder)
    except TypeError:
        image_tag.decompose()


class Chapter(object):
    """
    Class representing an ebook chapter. By and large this shouldn't be
    called directly but rather one should use the class ChapterFactory to
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
    """
    def __init__(self, content, title, url=None):
        self._validate_input_types(content, title)
        self.title = title
        self.content = content
        self._content_tree = BeautifulSoup(self.content, 'html.parser')
        self.url = url
        self.html_title = cgi.escape(self.title, quote=True)

    def write(self, file_name):
        """
        Writes the chapter object to an xhtml file.

        Args:
            file_name (str): The full name of the xhtml file to save to.
        """
        try:
            assert file_name[-6:] == '.xhtml'
        except (AssertionError, IndexError):
            raise ValueError('filename must end with .xhtml')
        with open(file_name, 'wb') as f:
            f.write(self.content.encode('utf-8'))

    def _validate_input_types(self, content, title):
        try:
            assert isinstance(content, str)
        except AssertionError:
            raise TypeError('content must be a string')
        try:
            assert isinstance(title, str)
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

    def get_url(self):
        if self.url is not None:
            return self.url
        else:
            raise NoUrlError()

    def _get_image_urls(self):
        image_nodes = self._content_tree.find_all('img')
        raw_image_urls = [node['src'] for node in image_nodes if node.has_attr('src')]
        full_image_urls = [urllib.parse.urljoin(self.url, image_url) for image_url in raw_image_urls]
        image_nodes_filtered = [node for node in image_nodes if node.has_attr('src')]
        return list(zip(image_nodes_filtered, full_image_urls))

    def _replace_images_in_chapter(self, ebook_folder):
        image_url_list = self._get_image_urls()
        for image_tag, image_url in image_url_list:
            _replace_image(image_url, image_tag, ebook_folder)
        unformatted_html_unicode_string = str(self._content_tree.prettify(encoding='utf-8',
                                                                              formatter=EntitySubstitution.substitute_html),
                                                  encoding='utf-8')
        unformatted_html_unicode_string = unformatted_html_unicode_string.replace('<br>', '<br/>')
        self.content = unformatted_html_unicode_string


class ChapterFactory(object):
    """
    Used to create Chapter objects.Chapter objects can be created from urls,
    files, and strings.

    Args:
        clean_function (Option[function]): A function used to sanitize raw
            html to be used in an epub. By default, this is the pypub.clean
            function.
    """

    def __init__(self, clean_function=clean.clean):
        self.clean_function = clean_function
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
        self.request_headers = {'User-Agent': user_agent}

    def create_chapter_from_url(self, url, title=None):
        """
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

        Raises:
            ValueError: Raised if unable to connect to url supplied
        """
        try:
            request_object = requests.get(url, headers=self.request_headers, allow_redirects=False)
        except (requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError):
            raise ValueError("%s is an invalid url or no network connection" % url)
        except requests.exceptions.SSLError:
            raise ValueError("Url %s doesn't have valid SSL certificate" % url)
        unicode_string = request_object.text
        return self.create_chapter_from_string(unicode_string, url, title)

    def create_chapter_from_file(self, file_name, url=None, title=None):
        """
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
        """
        with codecs.open(file_name, 'r', encoding='utf-8') as f:
            content_string = f.read()
        return self.create_chapter_from_string(content_string, url, title)

    def create_chapter_from_string(self, html_string, url=None, title=None):
        """
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
        """
        clean_html_string = self.clean_function(html_string)
        clean_xhtml_string = clean.html_to_xhtml(clean_html_string)
        if title:
            pass
        else:
            try:
                root = BeautifulSoup(html_string, 'html.parser')
                title_node = root.title
                if title_node is not None:
                    title = str(title_node.string)
                else:
                    raise ValueError
            except (IndexError, ValueError):
                title = 'Ebook Chapter'
        return Chapter(clean_xhtml_string, title, url)

create_chapter_from_url = ChapterFactory().create_chapter_from_url
create_chapter_from_file = ChapterFactory().create_chapter_from_file
create_chapter_from_string = ChapterFactory().create_chapter_from_string
