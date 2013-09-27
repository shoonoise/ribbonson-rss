#!/usr/bin/python

import feedparser
import logging
import gevent
import opml
from gevent import monkey
from time import mktime
from datetime import datetime
from feeds import connection


class FeedHandler(object):
    """This class response for adding and updating feeds"""

    def __init__(self, url):

        parsed_feed = feedparser.parse(url)

        if 'bozo_exception' in parsed_feed:
            logging.info("Failed to parse %s. %s" % (url, parsed_feed['bozo_exception']))
            raise gevent.GreenletExit

        try:
            self.items = self.__extract_items(parsed_feed)
        except AttributeError as e:
            logging.info("Failed to parse %s. %s" % (url, e))
            raise gevent.GreenletExit

        self.url = unicode(url)
        self.title = unicode(parsed_feed.feed.title)
        logging.info("Processed %s(%s)", self.title, url)

    @staticmethod
    def __extract_items(parsed_feed):
        """Extract items from parsed feed object"""
        return [{'summary': article.summary,
                 'title': article.title,
                 'link': article.link,
                 'published': datetime.fromtimestamp(mktime(article.updated_parsed)),
                 'viewed': False}
                for article in parsed_feed.entries]

    @property
    def in_db(self):
        """Return True if Feed already in DB"""
        return connection.test.feed.find_one({'url': self.url})

    def __add_feed_in_db(self):
        """Use if feed not stored in db"""
        logging.info("Create new feed (%s(%s)) in db", self.title, self.url)
        collection = connection.test.feed.Feed()
        if not self.title and self.url:
            logging.warning("Issue with feed parsing: %s", self.url)
            raise ValueError("Invalid %s feed format" % self.url)

        collection['title'] = self.title
        collection['url'] = self.url
        collection['items'] = self.items
        collection.save()

    def __update_feed_in_db(self):
        """Use if feed already in db"""
        logging.info("Update %s(%s)", self.title, self.url)
        connection.test.feed.find_and_modify({'url': self.url}, {'$push': {'items': {'$each': self.items}}})

    def process(self):
        """Common method for create od update feed in db"""
        if self.in_db:
            self.__update_feed_in_db()
        else:
            self.__add_feed_in_db()


if __name__ == "__main__":

    monkey.patch_all()

    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s', filename="fetcher.log", level=logging.INFO)
    logging.info("\n" + "*" * 5 + " New run " + "*" * 5)

    URLS = set()

    def create_job(url):
        f = FeedHandler(url)
        f.process()

    opml_file = open("feedly.opml")
    outline = opml.from_string(opml_file.read())
    for line in outline:
        for item in line:
            URLS.add(item.xmlUrl)

    gevent.joinall([gevent.spawn(create_job, url) for url in URLS])
