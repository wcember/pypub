"""
Chapter Factory Unit Tests
"""
import logging
import unittest

from ..chapter import htmltostring
from ..factory import SimpleChapterFactory

#** Variables **#
__all__ = ['FactoryTests']

#: basic testing logging instance
logger = logging.getLogger('pypub.test')

#: chapter factory instance used to generate chapters
factory = SimpleChapterFactory()

image_html_sample1 = b"""
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <img src=""></img>
 </body>
</html>
"""

image_html_sample2 = b"""
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

article_html_sample1 = b"""
<html>
    <head></head>
    <body>
        <article>Hello! I am a test</article>
    </body>
</html>
"""

article_html_sample2 = b"""
<html>
    <head></head>
    <body>
        <div>dsfasfadfasdfasdf</div>
        <article>Hello! I am a test</article>
    </body>
</html>
"""

article_html_sample3 = b"""
<html>
    <head></head>
    <body>
        <article><video></video>Hello! I am a test</article>
    </body>
</html>
"""

complete_html_sample1 = b"""
<!DOCTYPE html>
<html>
 <head>
 </head>
 <body>
  <div>Hello </div>
 </body>
</html>
"""

complete_html_sample2 = b"""
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

complete_html_sample3 = b"""
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

complete_html_sample4 = b"""
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

complete_html_sample5 = b"""
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

#** Functions **#

def cleanup(content: bytes) -> bytes:
    """
    clean and produce finalized pypub chapter content
    """
    etree = factory.cleanup_html(content)
    for elem in etree.iter():
        elem.tail = None
        elem.text = elem.text.strip() if elem.text else ''
    return htmltostring(etree)

#** Tests **#

class FactoryTests(unittest.TestCase):
    
    def test_clean_images(self):
        """ensure etree cleaning works as intended to filter bad images"""
        clean1 = cleanup(image_html_sample1)
        clean2 = cleanup(image_html_sample2)
        self.assertEqual(clean1, clean2)

    def test_clean_article(self):
        """test that non-whitelisted tags get removed from html snippet"""
        s1 = cleanup(article_html_sample1)
        s2 = cleanup(article_html_sample2)
        s3 = cleanup(article_html_sample3)
        self.assertEqual(s1, s2)
        self.assertEqual(s1, s3)

    def test_clean_html(self):
        """test entire html grouping can be cleaned properly"""
        s1 = cleanup(complete_html_sample1)
        s2 = cleanup(complete_html_sample2)
        s3 = cleanup(complete_html_sample3)
        s4 = cleanup(complete_html_sample4)
        s5 = cleanup(complete_html_sample5)
        self.assertEqual(s1, s2)
        self.assertEqual(s1, s3)
        self.assertEqual(s1, s4)
        self.assertEqual(s1, s5)

#** Main **#

if __name__ == '__main__':
    unittest.main()
