#!/usr/bin/python

import feedparser
import logging
import gevent
from gevent import monkey
from time import mktime
from datetime import datetime
from feeds import connection


class FeedHandler(object):
    """This class response for adding and updating feeds"""

    def __init__(self, url):
        parsed_feed = feedparser.parse(url)
        self.url = unicode(url)
        self.title = unicode(parsed_feed.feed.title)
        self.items = self.__extract_items(parsed_feed)
        logging.info("Processed %s(%s)", self.title, url)

    @staticmethod
    def __extract_items(parsed_feed):
        """Extract items from parsed feed object"""
        return [{'summary': article.summary,
                 'title': article.title,
                 'link': article.link,
                 'published': datetime.fromtimestamp(mktime(article.published_parsed)),
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

    logging.basicConfig(filename="fetcher.log", level=logging.INFO)
    logging.info("\n" + "*" * 5 + " New run " + "*" * 5)

    URLS = ['http://feeds.feedburner.com/d0od',
            'http://habrahabr.ru/rss/hubs/',
            'http://dribbble.com/shots/popular.rss',
            'http://www.alexconrad.org//feeds/posts/default',
            'http://www.ixbt.com/export/articles.rss',
            'http://feeds.feedburner.com/eaxme',
            'http://feeds.feedburner.com/futurecolors'
            ]

    def create_job(url):
        f = FeedHandler(url)
        f.process()

    gevent.joinall([gevent.spawn(create_job, url) for url in URLS])