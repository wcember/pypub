import re

import unittest

import clean

class CleanTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_content(self):
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
        self.assertEqual(clean.get_content(s, u''), [
                (u'div', u'Hello'),
        ])


if __name__ == '__main__':
    unittest.main()