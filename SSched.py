# SSched.py
# Skeletorfw
# 17/05/17
#
# Python 3.4.1
#
# Bot to post regularly to a particular subreddit

import csv
import logging
import textwrap
import time

import praw
from prawcore import RequestException

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
default_sub = "test"    # Insert your default sub here


class MalformedPostError(Exception):
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
            queuereader = csv.reader(queuefile, delimiter='|')
            for entry in queuereader:
                # Split entry into ['url', 'description', 'subreddit']
                subqueue.append([x for x in entry])
                logger.debug("Loaded {0}.".format(entry[0]))
    except FileNotFoundError:
        logger.warning("No submission queue present. Returning empty queue.")

    logger.info("Entries in submission queue: {0}.".format(len(subqueue)))

    return subqueue


def validate_post(post_entry, fallback_sub):
    logger.debug("Validating popped submission from queue.")

    try:
        using_default = False
        post_entry_working = post_entry

        # Process entry properly, removing whitespace and checking values.
        if len(post_entry_working) == 2:
            post_entry_working.append(fallback_sub)     # Use default subreddit if not defined in entry.
            using_default = True
            logger.debug("No subreddit defined, using default of {0}.".format(fallback_sub))
        if len(post_entry_working) > 3:     # Should catch many malformed entries.
            raise MalformedPostError
        post_entry_working = [x.strip() for x in post_entry_working]  # Cut whitespace from each string.
        # Should possibly try to validate URLs here.
        # Elegantly shorten descriptions over 300 chars.
        post_entry_working[1] = textwrap.shorten(post_entry_working[1], width=300, placeholder="...")

        # Create RedditSubmission obj
        post = RedditSubmission(post_entry_working[0], post_entry_working[1], post_entry_working[2])

        logger.info("Post successfully validated.")
        logger.debug("--------------- METADATA ----------------")
        logger.debug("{0:>9}: {1.description:}".format("Title", post))
        logger.debug("{0:>9}: {1.url}".format("Url", post))
        if using_default:
            logger.debug("{0:>9}: {1.subreddit}(default)".format("Subreddit", post))
        else:
            logger.debug("{0:>9}: {1.subreddit}".format("Subreddit", post))
        logger.debug("-----------------------------------------")

    except MalformedPostError:
        err_string = "".join(["{0}|".format(x) for x in post_entry]).rstrip("|")
        logger.error("Malformed post entry: {0}".format(err_string))
        with open("data/subqueue_errored.csv", "a", newline='') as errorfile:   # Write errored line to errorfile.
            errorwriter = csv.writer(errorfile, delimiter='|')
            errorwriter.writerow(post_entry)
        raise MalformedPostError

    return post


def submit_post(post):
    subreddit = reddit.subreddit(post.subreddit)
    subreddit.submit(title=post.description, url=post.url)
    logger.info("Post submitted successfully.")


def write_subqueue(subqueue):
    """Write subqueue out to csv for next time"""
    logger.debug("Writing subqueue to disk.")

    with open("data/subqueue.csv", "w", newline='') as queuefile:
        queuewriter = csv.writer(queuefile, delimiter='|')
        queuewriter.writerows(subqueue)
    logger.info("Currently queued submissions:{0}".format(len(subqueue)))


def main():
    starttime = time.perf_counter()
    logger.info("-----------------------------------------")
    logger.info("Started execution at {0}".format(time.strftime("%H:%M:%S, %d/%m/%Y", time.localtime())))
    logger.info("-----------------------------------------")
    queue = read_subqueue()
    if queue:
        loopagain = True
        while loopagain:
            loopagain = False   # Only do 1 run.
            popped = queue.pop(0)
            logger.debug("Popped post string from queue.")
            try:
                validated = validate_post(popped, default_sub)
                submit_post(validated)
            except MalformedPostError:
                logger.critical("Did not post due to malformed post string!")
                loopagain = True    # Force another run.
            except RequestException as err:
                logger.critical("Could not post:{0}".format(err.original_exception))
                queue.insert(0, popped)     # Insert string back into queue for later.
            write_subqueue(queue)
    else:
        logger.info("No entries in queue.")
    endtime = time.perf_counter()
    runtime = time.strftime("%H:%M:%S", time.gmtime(endtime - starttime))
    logger.info("-----------------------------------------")
    logger.info("Ended execution at {0}".format(time.strftime("%H:%M:%S, %d/%m/%Y", time.localtime())))
    logger.info("Executed in {0}.".format(runtime))
    logger.info("-----------------------------------------")

main()
