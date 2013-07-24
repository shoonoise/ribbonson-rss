from feeds import connection
from mongokit import Document
import datetime

@connection.register
class Feed(Document):
    __database__ = 'test'
    __collection__ = 'feeds'

    structure = {
        'title': unicode,
        'url': unicode,
        'items': [
            {
            'title': unicode,
            'link': unicode,
            'published': datetime.datetime,
            'summary': unicode,
            'viewed': bool
        }
        ]
    }

    indexes = [
        {'fields': ['url'], 'unique': True}
    ]
