import os
import lxml
import unittest

from .. import *

#** Variables **#
static = os.path.realpath(os.path.join(os.path.dirname(__file__),'static'))

image_html_sample1 = """
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <img src=""></img>
 </body>
</html>
"""
image_html_sample2 = """
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <img src=""></img>
  <img></img>
  <img/>
 </body>
</html>
"""
article_html_sample1 = """
<html>
    <head></head>
    <body>
        <article>Hello! I am a test</article>
    </body>
</html>
"""
article_html_sample2 = """
<html>
    <head></head>
    <body>
        <div>dsfasfadfasdfasdf</div>
        <article>Hello! I am a test</article>
    </body>
</html>
"""
article_html_sample3 = """
<html>
    <head></head>
    <body>
        <article><video></video>Hello! I am a test</article>
    </body>
</html>
"""
complete_html_sample1 = """
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <div>Hello </div>
 </body>
</html>
"""
complete_html_sample2 = """
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <div>Hello </div>
  <script>Uh oh...it's an evil script!</script>
 </body>
</html>
"""
complete_html_sample3 = """
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <div>Hello </div>
 </body>
 <video>Play me!</video>
</html>
"""
complete_html_sample4 = """
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <video>
   <div>Hello </div>
  </video>
 </body>
 <video>Play me!</video>
</html>
"""
complete_html_sample5 = """
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <video>
   <div>Hello&nbsp;</div>
  </video>
 </body>
 <video>Play me!</video>
</html>
"""

#** Tests **#

class ChapterTests(unittest.TestCase):

    def _clean(self, content: str) -> str:
        """return clean content-str using chapter etree-generation"""
        # generate etree
        etree = Chapter('title', content)._new_etree()
        # condense etree
        for elem in etree.iter():
            elem.tail = None
            elem.text = elem.text.strip() if elem.text else ''
        # return stringifed xml
        return lxml.etree.tostring(etree, method='xml')

    def test_create_chapter_from_file(self):
        """complete test for create_chapter_from_file"""
        example = os.path.join(static, 'example.html')
        c       = create_chapter_from_file(example)
        self.assertEqual(c.title, 'Business & Co')
        self.assertEqual(c.url, None)
        self.assertEqual(c.html_title, 'Business &amp; Co')

    def test_chapter_clean_images(self):
        """ensure etree cleaning works as intended to filter bad images"""
        clean1 = self._clean(image_html_sample1)
        clean2 = self._clean(image_html_sample2)
        self.assertEqual(clean1, clean2)

    def test_chapter_clean_article(self):
        """test that non-whitelisted tags get removed from html snippet"""
        s1 = self._clean(article_html_sample1)
        s2 = self._clean(article_html_sample2)
        s3 = self._clean(article_html_sample3)
        self.assertEqual(s1, s2)
        self.assertEqual(s1, s3)

    def test_chapter_clean_html(self):
        """test that entire html grouping can be cleaned properly"""
        s1 = self._clean(complete_html_sample1)
        s2 = self._clean(complete_html_sample2)
        s3 = self._clean(complete_html_sample3)
        s4 = self._clean(complete_html_sample4)
        s5 = self._clean(complete_html_sample5)
        self.assertEqual(s1, s2)
        self.assertEqual(s1, s3)
        self.assertEqual(s1, s4)
        self.assertEqual(s1, s5)

    def test_chapter_errors(self):
        """complete test that checks chapter generation for errors"""
        self.assertRaises(TypeError, Chapter, None, 'content')
        self.assertRaises(TypeError, Chapter, 'content', None)
        self.assertRaises(ValueError, Chapter, '', 'content')
        self.assertRaises(ValueError, Chapter, 'content', '')

#** Main **#

if __name__ == '__main__':
    unittest.main()
