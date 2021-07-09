Tutorial - create an epub from reddit stories
*****************

Ready to get started? In this tutorial we will create an epub from the top stories currently on reddit.

Before you start, make sure the following is true

- Confirm that python 3 is installed on your machine and that you are using is.
- Make sure the most recent version of `pypub <http://pypub.readthedocs.io/en/latest/pypub.html#installation>`_ is installed
- In this tutorial, we are going to use the python package `praw <https://praw.readthedocs.io/en/stable/#installation>`_ to access reddit's api. Download that too. While praw is necessary for this tutorial, you do not need it to use pypub.
- (Optional) If you want to read your ebook on kindle, you'll need to convert it to a mobi file. Download `KindleGen <http://www.amazon.com/gp/feature.html?docId=1000765211>`_ to do this.

****************
Find the stories you're interested
****************
For this tutorial, we are going to grab the top stories from the subreddit `r/TrueReddit <http://reddit.com/r/TrueReddit/>`_. Pypub works with (most) websites, and the code contained here is easily generalizable to other content sources.

Let's begin by importing pypub as well as the other python libraries we're using for this tutorial

    >>> import pypub
    >>> import praw, os

Now let's get the current top ten stories from r/TrueReddit. The below code is necessary for this tutorial, but all we're returning here is a list of urls of stories we are interested in. Feel free to substitute here code to get whatever you are interested in (posts from your favorite blog, magazine articles, etc.)

    >>> praw_object = praw.Reddit(user_agent='pypub/1.0')
    >>> top_submission_list = praw_object.get_subreddit('TrueReddit').get_top(limit=10)
    >>> top_submission_url_list = [submission.url for submission in top_submission_list]

top_submission_url_list is a python list of strings, where each string represents a url for one of the top ten stories from r/TrueReddit [#f1]_.

****************
Create the epub
****************
Now that we have a list of url strings, we can use pypub to download the content and create an epub from the stories. First let's create an Epub object called epub. The only information we need to provide is the title of the ebook we'll be creating, which we will call 'TrueReddit - Top Stories'.

    >>> epub = pypub.Epub('TrueReddit - Top Stories')

With the Epub object we just created, let's add a chapter to it for every story we in our url list.

    >>> for url in top_submission_url_list:
    ...     try:
    ...         c = pypub.create_chapter_from_url(url)
    ...         epub.add_chapter(c)
    ...     except ValueError:
    ...         pass

Note in the above code that we try to create a chapter from every url, but don't if pypub raises a ValueError, which occurs if you try using pypub without an internet connection or if the url is invalid.

Finally, let's create our epub file. The below code saves it in the current working directory, but feel free to change that.

    >>> epub.create_epub(os.getcwd())

At this point, in the directory you're working in, you should have a file *TrueReddit - Top Stories.epub*. This is your ebook with the top stories from r/TrueReddit and you should be able to read on your favorite device (unless that device is a kindle...see the next section).

****************
(Optional) Convert to mobi
****************
If you're like me, then you like reading things on your kindle (which is why I created pypub in the first place). Unfortunately, kindle uses it's own format for ebooks.

Luckily, Amazon provided a tool, KindleGen to convert epubs (and other formats) to mobi so they can be viewed on kindle. Once it's downloaded, convert *TrueReddit - Top Stories.epub* by going to the command prompt and entering kindlegen's full file path (excluding .exe) followed by "TrueReddit - Top Stories.epub".

    > <full directory of kindlegen>kindlegen "TrueReddit - Top Stories.epub"

If the kindlegen executable is saved in the same directory as *TrueReddit - Top Stories.epub*, this can simply be entered as

    > kindlegen "TrueReddit - Top Stories.epub"

.. rubric:: Footnotes

.. [#f1] If you are using a version of python earlier than 2.7.9, you may get SNIMissingWarning exception, which has to do with verifying HTTPS certificates. You should consider upgrading your version of python or following the instructions `here <http://urllib3.readthedocs.io/en/latest/security.html#snimissingwarning>`
