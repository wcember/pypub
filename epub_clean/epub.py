import collections
import copy
import json
import os
import random
import string
import shutil
import tempfile
import time

import jinja2
import lxml.html
import lxml.html.builder
import requests

from constants import *
import chapter


class _Minetype():

    def __init__(self, parent_directory):
        minetype_template = os.path.join(EPUB_TEMPLATES_DIR, 'minetype.txt')
        shutil.copy(minetype_template,
                os.path.join(parent_directory, 'minetype.txt'))


class _ContainerFile():

    def __init__(self, parent_directory):
        container_template = os.path.join(EPUB_TEMPLATES_DIR, 'container.xml')
        shutil.copy(container_template,
                os.path.join(parent_directory, 'container.xml'))


class _EpubFile(object):

    def __init__(self, template_file, **non_chapter_parameters):
        self.content = u''
        self.file_name = ''
        self.template_file = template_file
        self.non_chapter_parameters = non_chapter_parameters

    def write(self, file_name):
        self.file_name = file_name
        with open(file_name, 'wb') as f:
            f.write(self.content.encode('utf-8'))

    def _renderTemplate(self, **variable_value_pairs):
        def readTemplate():
            with open(self.template_file, 'r') as f:
                template = f.read().decode('utf-8')
            return jinja2.Template(template)
        template = readTemplate()
        rendered_template = template.render(variable_value_pairs)
        self.content = rendered_template

    def add_chapters(self, **parameter_lists):
        def checkListLengths(lists):
            list_length = None
            for value in lists.values():
                assert isinstance(value, list)
                if list_length is None:
                    list_length = len(value)
                else:
                    assert len(value) == list_length
        checkListLengths(parameter_lists)
        template_chapter = collections.namedtuple('template_chapter',
                parameter_lists.keys())
        chapters = [template_chapter(*items) for items in zip(*parameter_lists.values())]
        self._renderTemplate(chapters=chapters, **self.non_chapter_parameters)

    def get_content(self):
        return self.content


class _TOC_HTML(_EpubFile):

    def __init__(self,
            template_file=os.path.join(EPUB_TEMPLATES_DIR, 'toc.html'),
            **non_chapter_parameters):
        super(_TOC_HTML, self).__init__(template_file,
                **non_chapter_parameters)

    def add_chapters(self, chapter_list):
        chapter_numbers = range(len(chapter_list))
        link_list = [str(n) + '.xhtml' for n in chapter_numbers]
        try:
            for c in chapter_list:
                t = type(c)
                assert type(c) == chapter.Chapter
        except AssertionError:
            raise TypeError('chapter_list items must be Chapter not %s',
                    str(t))
        chapter_titles = [c.title for c in chapter_list]
        super(_TOC_HTML, self).add_chapters(title=chapter_titles,
                link=link_list)

    def get_content_as_element(self):
        root = lxml.html.fromstring(self.content.encode('utf-8'))
        return root


class _TOC_NCX(_EpubFile):

    def __init__(self,
            template_file=os.path.join(EPUB_TEMPLATES_DIR, 'toc_ncx.xml'),
            **non_chapter_parameters):
        super(_TOC_NCX, self).__init__(template_file, **non_chapter_parameters)

    def add_chapters(self, chapter_list):
        id_list = range(len(chapter_list))
        play_order_list = [n + 1 for n in id_list]
        title_list = [c.title for c in chapter_list]
        link_list = [str(n) + '.xhtml' for n in id_list]
        super(_TOC_NCX, self).add_chapters(**{'id': id_list,
                'play_order': play_order_list,
                'title': title_list,
                'link': link_list})

    def get_content_as_element(self):
        root = lxml.etree.fromstring(self.content.encode('utf-8'))
        return root


class _Content_OPF(_EpubFile):

    def __init__(self, title, creator='', language='', rights='',
            publisher='', uid='', date = time.strftime("%m-%d-%Y")):
        super(_Content_OPF, self).__init__(os.path.join(EPUB_TEMPLATES_DIR,
                'opf.xml'),
                title=title,
                creator=creator,
                language=language,
                rights=rights,
                publisher=publisher,
                uid=uid,
                date=date)

    def add_chapters(self, chapter_list):
        id_list = range(len(chapter_list))
        link_list = [str(n) + '.xhtml' for n in id_list]
        super(_Content_OPF, self).add_chapters(**{'id': id_list,
                'link': link_list})

    def get_content_as_element(self):
        root = lxml.etree.fromstring(self.content.encode('utf-8'))
        return root


class Epub():

    def __init__(self, output_directory, title, creator='',
            language='en', rights='', publisher='Cember Corporation'):
        def create_directories():
            self.EPUB_DIR = tempfile.mkdtemp()
            self.OEBPS_DIR = os.path.join(self.EPUB_DIR, 'OEBPS')
            self.META_INF_DIR = os.path.join(self.EPUB_DIR, 'META-INF')
            self.LOCAL_IMAGE_DIR = 'images'
            self.IMAGE_DIR = os.path.join(self.OEBPS_DIR, self.LOCAL_IMAGE_DIR)
            self.output_directory = output_directory
            os.makedirs(self.OEBPS_DIR)
            os.makedirs(self.META_INF_DIR)
            os.makedirs(self.IMAGE_DIR)
        create_directories()
        self.chapters = []
        self.title = title
        try:
            assert title
        except AssertionError:
            raise ValueError('title cannot be empty string')
        self.creator= creator
        self.language= language
        self.rights= rights
        self.publisher = publisher
        self.uid= ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        self.current_chapter_number = None
        self._increase_current_chapter_number()
        self.toc_html = _TOC_HTML()
        self.toc_ncx = _TOC_NCX()
        self.opf = _Content_OPF(self.title, self.creator, self.language,
                self.rights, self.publisher, self.uid)
        self.minetype = _Minetype(self.EPUB_DIR)
        self.container = _ContainerFile(self.META_INF_DIR)

    def _increase_current_chapter_number(self):
        if self.current_chapter_number is None:
            self.current_chapter_number = 0
        else:
            self.current_chapter_number += 1
        self.current_chapter_id = str(self.current_chapter_number)
        self.current_chapter_path = ''.join([self.current_chapter_id,
                '.xhtml'])

    def add_chapter(self, c):
        try:
            assert type(c) == chapter.Chapter
        except AssertionError:
            raise TypeError('chapter must be of type Chapter')
        chapter_file_output = os.path.join(self.OEBPS_DIR,
                self.current_chapter_path)
        c.write_to_xhtml(chapter_file_output)
        self._increase_current_chapter_number()
        self.chapters.append(c)

    def create_epub(self, epub_name = None):
        def createTOCs_and_ContentOPF():
            for epub_file, name in ((self.toc_html, 'toc.html'),
                    (self.toc_ncx, 'toc.ncx'),
                    (self.opf, 'content.opf'),):
                epub_file.add_chapters(self.chapters)
                epub_file.write(os.path.join(self.OEBPS_DIR, name))
        def create_zip_archive(epub_name):
            try:
                assert isinstance(epub_name, basestring) or epub_name is None
            except AssertionError:
                raise TypeError('epub_name must be string or None')
            if epub_name is None:
                epub_name = str(time.time())
            epub_name_with_path = os.path.join(self.output_directory,
                    epub_name)
            try:
                os.remove(os.path.join(epub_name_with_path, '.zip'))
            except OSError:
                pass
            shutil.make_archive(epub_name_with_path, 'zip', self.EPUB_DIR)
            return epub_name_with_path + '.zip'
        def turn_zip_into_epub(zip_archive):
            epub_full_name = zip_archive.strip('.zip') + '.epub'
            try:
                os.remove(epub_full_name)
            except OSError:
                pass
            os.rename(zip_archive, epub_full_name)
            return epub_full_name
        createTOCs_and_ContentOPF()
        epub_path = turn_zip_into_epub(create_zip_archive(epub_name))
        shutil.rmtree(self.EPUB_DIR)
        return epub_path


##def create_epub_from_folder_file(epub_title, epub_file_title,
##        output_directory, input_directory, information_file):
##    if information_file is not None:
##        with open(information_file, 'rb') as f:
##            information_list = json.load(f)
##    else:
##        information_list = None
##    e = Epub(output_directory, epub_title)
##    chapter_list = []
##    for information_dictionary in information_list:
##        chapter_path = information_dictionary['path']
##        chapter_url = information_dictionary['url']
##        chapter_title = information_dictionary['title']
##        chapter_list.append(chapter.Chapter(chapter_path, chapter_url, chapter_title))
##    for c in chapter_list:
##        c.clean_and_replace_images(e)
##        e.add_chapter(c)
##    e.create_epub(epub_file_title)
##    return e
