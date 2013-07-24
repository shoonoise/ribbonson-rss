from base64 import urlsafe_b64encode, urlsafe_b64decode
from flask import abort, render_template, jsonify
from feeds import app, connection
from models import Feed

@app.route("/<feed_id>/<int:item_no>")
def get_article(feed_id, item_no):
    collection = connection.test.feed.Feed
    app.logger.debug(collection)
    feed = collection.find_one({'url': urlsafe_b64decode(str(feed_id))})
    if item_no >= len(feed['items']):
        abort(404)
    article = feed['items'][item_no]
    return jsonify(article)

@app.route("/")
def index():
    feeds = []
    all_feeds = connection.test.feed.Feed.fetch()
    for f in all_feeds:
        title = f['title']
        count_items = len(f['items'])
        feed_id = urlsafe_b64encode(f['url'])
        feeds.append({'title': title, 'count': count_items, 'id': feed_id})
    app.logger.debug(feeds)
    return render_template('index.html', feeds=feeds)


