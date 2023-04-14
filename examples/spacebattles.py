"""
Download a Book on Space Battles

NOTE: most of the code-complexity in this script
comes from how incomplete the lxml xpath engine is
"""
import sys
sys.path.insert(0, '../')

import pypub
print(pypub.__file__)

import time
import random
import logging
from urllib.parse import urljoin

import pyxml.html
from pypub import Epub, create_chapter_from_html
from pypub.chapter import urlrequest

#** Variables **#

#: title for book
TITLE = "A Geek's Guide: Corporation of Occult Research and Extermination"

#: author for book
AUTHOR = 'Sage of Eyes'

#: space battles base url (make sure to use reader version)
BASE_URL = 'https://forums.spacebattles.com/threads/a-geeks-guide-corporation-of-occult-research-and-extermination-complete.330378/reader/'

#: output file
OUTPUT = 'geeks-guide-1.epub'

#** Functions **#

def request(url: str) -> pyxml.html.HtmlElement:
    """complete http request and retrieve parsed html"""
    res  = urlrequest(url)
    body = res.read()
    if res.status and res.status != 200:
        raise RuntimeError('invalid response', res.status)
    return pyxml.html.fromstring(body)

def get_pages(url: str) -> int:
    """
    retrieve number of pages from main reader page
    """
    last    = 0
    etree   = request(url)
    ul      = etree.find('//ul[@class="pageNav-main"]')
    for anchor in ul.findall('/li/a[@href]'):
        pagenum = anchor.text
        if not pagenum.isdigit():
            raise ValueError('invalid page number', pagenum)
        last = max(last, int(pagenum))
    return last

def parse_chapters(url: str, book: Epub):
    """
    parse chapters from the given url and append them to the ebook
    """
    etree = request(url)
    for article in etree.findall('//article[starts-with(@class, "message ")]'):
        # assign title based on threadmark or number and find body
        try:
            title = article.find('//span[contains(@class, "threadmarkLabel")]')
            body  = article.find('//div[contains(@class, "message-main")]')
            title = f'Chapter_{book.last_chapter}' if title is None else title.text
            if body is None:
                raise RuntimeError('unable to find article body')
            content = pyxml.html.tostring(body)
            chapter = create_chapter_from_html(content, title=title, url=url)
            assign  = book.assign_chapter()
            book.builder.render_chapter(assign, chapter)
        except RuntimeError as e:
            print(pyxml.html.tostring(article))
            raise e

#** Init **#
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    book = Epub(TITLE, creator=AUTHOR)
    # retrieve and parse the max-page available for iterating
    last_page = get_pages(BASE_URL) 
    urls      = [BASE_URL]
    for n in range(2, last_page+1):
        url = urljoin(BASE_URL, f'page-{n}')
        urls.append(url)
    # iterate page urls and retrieve chapters
    with book.builder as builder:
        dirs = builder.begin()
        print('building ebook at', dirs.basedir)
        for n, url in enumerate(urls, 1):
            print(f'loading chapters {n}/{len(urls)}')
            parse_chapters(url, book)
            #NOTE: this random sleep time is to avoid bot
            # detection from spacebattles. if pages are queried
            # too quickly, the requests start getting denied.
            sleep = random.randint(2, 15)
            print('sleeping', sleep, 'seconds')
            time.sleep(sleep)
        builder.finalize(OUTPUT)
