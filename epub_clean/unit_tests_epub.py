import copy
import unittest
import os
import os.path
import shutil
import tempfile
import time

import lxml.html

import chapter
from constants import *
import epub


class TestEpub(unittest.TestCase):

    def setUp(self):
        chapter_dir = os.path.join(TEST_DIR, 'test_chapters')
        chapter_factory = chapter.ChapterFactory()
        self.output_directory = os.path.join(TEST_DIR, 'epub_output')
        self.chapter_list = []
        file_list = [f for f in os.listdir(chapter_dir) if os.path.isfile(os.path.join(chapter_dir,f))]
        for index, f in enumerate(file_list):
            full_name = os.path.join(chapter_dir, f)
            c = chapter_factory.create_chapter_from_file(full_name)
            self.chapter_list.append(c)
        self.chapter_titles = [
                u'Quick Practical, Tactical Tips for Presentations',
                u'Venture capital - Wikipedia, the free encyclopedia',
                u"Ben's Blog",
                u"The capture of Mosul: Terror\u2019s new headquarters | The Economist",
                ]

    def test_TOCHTML(self):
        def create_TOC():
            self.test_toc = epub._TOC_HTML()
            self.test_toc.add_chapters(self.chapter_list)
            self.toc_element = self.test_toc.get_content_as_element()
        def check_titles():
            chapter_nodes = self.toc_element.get_element_by_id('chapters').getchildren()
            self.assertEqual(len(chapter_nodes), len(self.chapter_list))
            self.assertEqual(chapter_nodes[0][0].text,self.chapter_titles[0])
            self.assertEqual(chapter_nodes[1][0].text,self.chapter_titles[1])
            self.assertEqual(chapter_nodes[2][0].text,self.chapter_titles[2])
            self.assertEqual(chapter_nodes[3][0].text,self.chapter_titles[3])
        create_TOC()
        check_titles()
        self.test_toc.write(os.path.join(TEST_DIR, 'epub_output', 'toc.html'))

    def test_TOCNCX(self):
        def createTOC():
            self.test_toc = epub._TOC_NCX()
            self.test_toc.add_chapters(self.chapter_list)
            self.toc_element = self.test_toc.get_content_as_element()
        def checkTitles():
            chapter_nodes = self.toc_element[2]
            self.assertEqual(len(chapter_nodes),len(self.chapter_list))
            for index, node in enumerate(chapter_nodes):
                self.assertEqual(node[0][0].text,self.chapter_titles[index])
        createTOC()
        checkTitles()
        self.test_toc.write(os.path.join(TEST_DIR, 'epub_output', 'toc_ncx.xml'))

    def test_ContentOPF(self):
        def createContentOPF():
            self.test_opf = epub._Content_OPF('Sample Title')
            self.test_opf.add_chapters(self.chapter_list)
            opf_file = os.path.join(TEST_DIR, 'epub_output', 'opf.xml')
            self.test_opf.write(opf_file)
            self.opf_element = self.test_opf.get_content_as_element()
            self.assertEqual(len(self.opf_element.getchildren()), 4)
        def check_encoding():
            pass
        def checkSpine():
            spine_nodes = self.opf_element[2].getchildren()
            self.assertEqual(len(spine_nodes),len(self.chapter_list) + 1)
        def checkManifest():
            manifest_nodes = self.opf_element[1].getchildren()
            self.assertEqual(len(manifest_nodes),len(self.chapter_list) + 2)
        createContentOPF()
        check_encoding()
        checkSpine()
        checkManifest()

    def test_createEpub(self):
        e = epub.Epub(TEST_DIR, 'Test Epub')
        for index, c in enumerate(self.chapter_list):
            c.write(os.path.join(TEST_DIR, 'epub_output', str(index) + '.html'))
            e.add_chapter(c)
        e.createEpub(epub_name = 'test_epub')

##class Test_Create_Epub_From_Folder(unittest.TestCase):
##    def test_create_epub_from_folder_file(self):
##        test_folder = os.path.join(TEST_DIR, 'test_create_epub_from_folder')
##        information_file = os.path.join(test_folder, 'link_information.json')
##        e = epub.create_epub_from_folder_file('Sample Title', 'Test',
##                test_folder, test_folder, information_file)
##        self.assertEqual(len(e.chapters),3)
##        chapter_1 = e.chapters[0]
##        self.assertEqual(chapter_1.title,'Example Domain')
##        chapter_2 = e.chapters[1]
##        self.assertEqual(chapter_2.title,'AVC')
##        chapter_2 = e.chapters[2]
##        self.assertEqual(chapter_2.title,'Wikipedia')

if __name__ == '__main__':
    unittest.main()
