import feedparser
from time import mktime
from datetime import datetime
from feeds import models, connection

URLS = ['http://feeds.feedburner.com/d0od',
        'http://habrahabr.ru/rss/hubs/',
        'http://dribbble.com/shots/popular.rss',
        'http://www.alexconrad.org//feeds/posts/default',
        'http://www.ixbt.com/export/articles.rss',
        'http://feeds.feedburner.com/eaxme',
        'http://feeds.feedburner.com/futurecolors'
        ]

def add_new_feed(url):
    new_feed = feedparser.parse(url)
    items = []
    for article in new_feed.entries:
        items.append({'summary': article.summary,
                      'title': article.title,
                      'link': article.link,
                      'published': datetime.fromtimestamp(mktime(article.published_parsed)),
                      'viewed': False})

    feed = connection.test.feed.Feed()
    if  not (new_feed.get('feed').get('title') and new_feed.get('url')):
        print new_feed.get('feed')
        raise ValueError, "Invalide feed format"

    feed['title'] = unicode(new_feed.feed.title)
    feed['url'] = unicode(url)
    feed['items'] = items
    feed.save()

def find_feed(url):
    return connection.test.feed.find_one({'url': url})

def update_feed(url):
    updated_feed = feedparser.parse(url)
    items = []
    for article in updated_feed.entries:
        items.append(article.summary)
    connection.test.feed.find_and_modify({'url': url}, {'$push': {'items': {'$each': items}}})

if __name__ == "__main__":

    for url in URLS:
        if find_feed(url):
            update_feed(url)
        else:
            add_new_feed(url)
