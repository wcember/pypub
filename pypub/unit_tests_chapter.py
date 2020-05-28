import os
import unittest

from . import chapter


test_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        'test_files')

class ChapterTests(unittest.TestCase):

    def setUp(self):
        self.factory = chapter.ChapterFactory()

##    def test_create_chapter_from_url(self):
##        c = self.factory.create_chapter_from_url('http://example.com')
##        self.assertEqual(c.title, 'Example Domain')
##        self.assertEqual(c.url, 'http://example.com')
##        self.assertEqual(c.html_title, 'Example Domain')
##        c = self.factory.create_chapter_from_url(
##                'http://www.bothsidesofthetable.com/')
##        self.assertEqual(c.title,
##                'Bothsides of the Table | 2x entrepreneur turned VC')
##        self.assertEqual(c.url, 'http://www.bothsidesofthetable.com/')
##        self.assertEqual(c.html_title,
##                'Bothsides of the Table | 2x entrepreneur turned VC')

    def test_create_chapter_from_file(self):
        test_file = os.path.join(test_directory, 'example.html')
        c = self.factory.create_chapter_from_file(
                test_file)
        self.assertEqual(c.title, 'Example Domain')
        self.assertEqual(c.url, None)
        self.assertEqual(c.html_title, 'Example Domain')

    def test_html_title(self):
        test_file = os.path.join(test_directory, 'strategy&.html')
        c = self.factory.create_chapter_from_file(
                test_file, 'http://www.strategyand.pwc.com/')
        self.assertEqual(c.title,
                'Strategy& (Formerly Booz & Company) - A global management and strategy consulting firm')
        self.assertEqual(c.url, 'http://www.strategyand.pwc.com/')
        self.assertEqual(c.html_title,
                'Strategy&amp; (Formerly Booz &amp; Company) - A global management and strategy consulting firm')

    def test_chapter_type_errors(self):
        self.assertRaises(TypeError, chapter.Chapter, 1, 'Dummy Content')
        self.assertRaises(TypeError, chapter.Chapter, 'Dummy Title', 1)
        self.assertRaises(ValueError, chapter.Chapter, '', 'Dummy Content')
        self.assertRaises(ValueError, chapter.Chapter, 'Dummy Title', '')

    def test_chapter_write_error(self):
        test_file = os.path.join(test_directory, 'example.html')
        c = self.factory.create_chapter_from_file(
                test_file)
        self.assertRaises(ValueError, c.write, '')


if __name__ == '__main__':
    unittest.main()