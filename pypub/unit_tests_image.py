import os
import unittest

import chapter


test_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'test_files')


class ChapterTests(unittest.TestCase):

    def setUp(self):
        self.factory = chapter.ChapterFactory()

    def test_save_image(self):
        image_url_list = ['http://www.fangraphs.com/images/247_90_fangraphs.png',
                          'http://bothsides.wpengine.netdna-cdn.com/wp-content/uploads/2015/11/bothsides1.jpg']
        image_type_list = ['png',
                           'jpeg']
        for index, image in enumerate(image_url_list):
            self.assertEqual(chapter.save_image(image_url_list[index], test_directory,
                                                'test image ' + str(index)),
                             image_type_list[index])

    def test_save_image_error(self):
        self.assertRaises(chapter.ImageErrorException,
                          chapter.save_image,
                          'http://example.com',
                          test_directory,
                          'error image')

    def test_get_image_urls(self):
        test_url_1 = 'http://example.com'
        test_chapter_1 = chapter.create_chapter_from_url(test_url_1)
        self.assertEqual(test_chapter_1._get_image_urls(), [])
        test_url_2 = 'http://williamcember.com'
        test_chapter_2 = chapter.create_chapter_from_url(test_url_2)
        test_image_list_2 = ['http://williamcember.com/media/bithex-logo-black.png',
                             'http://williamcember.com/media/icon_linkedin.png',
                             'http://williamcember.com/media/GitHub-Mark-Light-120px-plus.png',
                             'http://williamcember.com/media/icon_twitter.png']
        self.assertEqual(test_chapter_2._get_image_urls(), test_image_list_2)


if __name__ == '__main__':
    unittest.main()
