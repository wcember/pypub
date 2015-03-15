import re

import unittest

from clean import clean, condense, html_to_xhtml

class CleanTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
    def test_condense(self):
        pass
    def test_clean_tags_full_html(self):
        s = u'''
                <!DOCTYPE html>
                <html>
                 <head>
                 </head>
                 <body>
                  <div>Hello</div>
                 </body>
                </html>
                '''
        s1 = u'''
                <!DOCTYPE html>
                <html>
                 <head>
                 </head>
                 <body>
                  <div>Hello</div>
                  <script>Uh oh...it's an evil script!</script>
                 </body>
                </html>
                '''
        s2 = u'''
                <!DOCTYPE html>
                <html>
                 <head>
                 </head>
                 <body>
                  <div>Hello</div>
                 </body>
                 <script>Uh oh...it's an evil script again!</script>
                </html>
                '''
        s3 = u'''
                <!DOCTYPE html>
                <html>
                 <head>
                 </head>
                 <body>
                  <div>Hello</div>
                 </body>
                 <video>Play me!</video>
                </html>
                '''
        s4 = u'''
                <!DOCTYPE html>
                <html>
                 <head>
                 </head>
                 <body>
                  <video>
                   <div>Hello</div>
                  </video>
                 </body>
                 <video>Play me!</video>
                </html>
                '''
        self.assertEqual(condense(clean(s)), condense(s))
        self.assertEqual(condense(clean(s1)), condense(s))
        self.assertEqual(condense(clean(s2)), condense(s))
        self.assertEqual(condense(clean(s3)), condense(s))
        self.assertEqual(condense(clean(s4)), condense(s))

    def test_html_to_xhtml(self):
        s = u'''
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml">
                 <head>
                 </head>
                 <body>
                  <div id="Test">Hello</div>
                  <br />
                  <br />
                 </body>
                </html>
                '''
        s1 = u'''
                <!DOCTYPE html>
                <html>
                 <head>
                 </head>
                 <body>
                  <DIV ID="Test">Hello</div>
                  <br>
                  <br>
                 </body>
                </html>
                '''
        self.assertEqual(condense(html_to_xhtml(clean((s1)))), condense(s))


if __name__ == '__main__':
    unittest.main()