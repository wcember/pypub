# Pypub #

Create epub's using python. Pypub is a python library to create epub files quickly without having to worry about the intricacies of the epub specification.

This package was orignally forked and re-writen based on WCember's [python2 version](https://github.com/wcember/pypub)
but due to lack of any response has been re-released as a new package to support python3

# Installation #
The current release of pypub is available through pip:

    $ pip install pypub3

Pypub is only compatible with Python <= 3.6.

# Quickstart #

```python3
import pypub
my_first_epub = pypub.Epub('My First Epub')
my_first_chapter = pypub.create_chapter_from_url('https://en.wikipedia.org/wiki/EPUB')
my_first_epub.add_chapter(my_first_chapter)
my_first_epub.create_epub('OUTPUT_DIRECTORY')
```

# Features #
* Pypub is **easy to install** and has minimal dependencies.
* Pypub **abstracts the epub specification**. Create epubs without worrying about what an NCX is.
* Pypub can **create epubs from websites, html files, strings**, or a combination of all three.
* Pypub can **clean up poorly formatted and complicated html** so it will cleanly as a chapter in your book.
* Pypub **creates epubs specifically so they can be converted into Amazon Kindle mobi or azw3 files**. Don't know which tags Amazon supports? Don't worry about it because pypub does. 
* Pypub is **customizable**. Don't like the way pypub sanitizes html files for you ebook? Pypub can be configured with your own sanitation function.
* Pypub is **licensed under the MIT license**. Do what you want with it.

# Documentation #

Documentation is available at [http://pypub.readthedocs.org/en/latest/developer_interface.html](http://pypub.readthedocs.org/en/latest/developer_interface.html)

# Copyright and License #

Copyright (c) 2022 Andrew Scott

[**Licensed**](https://github.com/imgurbot12/pypub/blob/master/LICENSE) under the MIT License

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
