# SSched.py
# Skeletorfw
# 16/05/17
# Version 0.0.1
#
# Python 3.4.1
#
# Bot to post regularly to a particular subreddit

import logging
import time
import praw
import csv

# Set up logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logfile handler
handler = logging.FileHandler('log/SSCHED.out')
handler.setLevel(logging.INFO)  # File logging level

# Create formatter and add to handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

# CONFIG
reddit = praw.Reddit('bot1')
default_sub = reddit.subreddit("getmetosleep")


class EmptyQueueError(Exception):
    pass


class RedditSubmission:
    # Class to hold active reddit submission
    def __init__(self, url, description, subreddit):
        self.url = url
        self.description = description
        self.subreddit = subreddit


def read_subqueue():
    """Read the current submission queue and return as a list"""
    logger.debug("Reading submission queue.")

    subqueue = []
    try:
        with open("data/subqueue.csv") as queuefile:
            queuereader = csv.reader(queuefile)
            for entry in queuereader:
                # Split entry into ['url', 'description', 'subreddit']
                subqueue.append([x for x in entry])
                logger.debug("Loaded {0}.".format(entry[0]))
    except FileNotFoundError:
        logger.warning("No submission queue present. Using empty queue.")

    logger.info("{0} entries in submission queue.".format(len(subqueue)))

    return subqueue


def pop_post(subqueue, fallback_sub):
    logger.debug("Popping submission from queue.")

    post_entry = subqueue.pop(0)
    if len(post_entry) == 2:
        post_entry.append(fallback_sub)     # Use default subreddit if not defined in entry
        logger.debug("No subreddit defined, using default of {0}".format(fallback_sub))
    post = RedditSubmission(post_entry[0], post_entry[1], post_entry[2])

    logger.info("Post successfully popped from queue.")
    logger.debug("{0:>14}: {1.description:}".format("Post title", post))
    logger.debug("{0:>14}: {1.url}".format("Post url", post))
    logger.debug("{0:>14}: {1.subreddit}".format("Post subreddit", post))

    return post, subqueue
