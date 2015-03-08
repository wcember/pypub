import unittest

import chapter


class ChapterTests(unittest.TestCase):
    def setUp(self):
        self.factory = chapter.ChapterFactory()
    def test_create_chapter_from_url(self):
        c = self.factory.create_chapter_from_url('http://example.com')
        self.assertEqual(c.title, 'Example Domain')
        self.assertEqual(c.url, 'http://example.com')
        self.assertEqual(c.html_title, 'Example Domain')


if __name__ == '__main__':
    unittest.main()