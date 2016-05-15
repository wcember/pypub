Tutorial - create an epub from reddit stories
**********

Ready to get started? In this tutorial we will create an epub from the top stories currently on reddit.

Before you start, make sure the following is true

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

    >>> top_submission_list = praw.Reddit(user_agent='pypub').get_subreddit('TrueReddit').get_top(limit=number_of_stories)
    >>> top_submission_url_list = [submission.url for submission in top_submission_list]

top_submission_url_list is a python list of strings, where each string represents a url for one of the top ten stories from r/TrueReddit.
