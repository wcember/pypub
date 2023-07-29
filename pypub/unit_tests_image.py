import os
import unittest

import chapter


test_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'test_files')


class ChapterTests(unittest.TestCase):

    def setUp(self):
        self.factory = chapter.ChapterFactory()
        self.test_image_list = []

    def test_save_image(self):  # TODO do not hit external websites that may/will disappear. If want to test http(s) spin up a server as part of test
        image_url_list = ['http://www.fangraphs.com/images/247_90_fangraphs.png',  # available as of 2023-07-28
                          'https://web.archive.org/web/20190110010653if_/http://bothsides.wpengine.netdna-cdn.com/wp-content/uploads/2015/11/bothsides1.jpg']  # http://bothsides.wpengine.netdna-cdn.com/wp-content/uploads/2015/11/bothsides1.jpg']  # domain no longer available as of 2023-07-28
        image_type_list = ['.png',
                           '.jpg']
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
        test_image_list_2 = self.test_image_list
        image_url_list_2_calced = [t[1] for t in test_chapter_2._get_image_urls()]
        self.assertEqual(image_url_list_2_calced, test_image_list_2)

    def test_replace_image(self):
        test_url = 'http://williamcember.com'
        test_ebook_dir = os.path.join(test_directory, 'epub_output')
        c = chapter.create_chapter_from_url(test_url)
        c._replace_images_in_chapter(test_ebook_dir)
        c.write(os.path.join(test_directory, 'test_cember.xhtml'))



if __name__ == '__main__':
    unittest.main()
