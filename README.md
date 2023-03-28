pypub
------

Create epub's using Python. 
Pypub is a Python library to create epub files quickly, 
without having to worry about the intricacies of the epub specification.

This package was originally forked and re-written based on WCember's Python 2 
version, but due to a lack of response has been re-released as a new package 
to support Python 3.

The codebase has since gone through a few substantial rewrites and operates 
as its own library moving forward.

### Installation

```
pip install pypub3
```

### Quickstart

```python
import pypub

my_first_epub = pypub.Epub('My First Epub')
my_first_chapter = pypub.create_chapter_from_url('https://en.wikipedia.org/wiki/EPUB')
my_first_epub.add_chapter(my_first_chapter)
my_first_epub.create('./my-first-epub.epub')
```

# Features #
* Pypub is **easy to install** and has minimal dependencies.
* Pypub **abstracts the epub specification**. 
  Create epubs without worrying about what an NCX is.
* Pypub can **create epubs from websites, html files, strings**, 
  or a combination of all three.
* Pypub can **clean up poorly formatted and complicated html**, 
  so it will show cleanly as a chapter in your book.
* Pypub **creates epubs specifically so they can be converted into 
  Amazon Kindle mobi or azw3 files**. Don't know which tags Amazon 
  supports? Don't worry about it because pypub does. 
* Pypub is **customizable**. Don't like the way pypub sanitizes html 
  files for you ebook? Pypub can be configured with your own sanitation 
  function.
* Pypub is **licensed under the MIT license**. Do what you want with it.
