import os
import unittest

import chapter


test_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        'test_files')

class ChapterTests(unittest.TestCase):

    def setUp(self):
        self.factory = chapter.ChapterFactory()

    def test_save_image(self):
        image_url_list = ['http://www.fangraphs.com/images/247_90_fangraphs.png'
                ,'http://bothsides.wpengine.netdna-cdn.com/wp-content/uploads/2015/11/bothsides1.jpg'
                ]
        image_type_list = ['png'
                ,'jpeg']
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



if __name__ == '__main__':
    unittest.main()