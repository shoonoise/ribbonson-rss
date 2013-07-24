from flask import Flask
from mongokit import Connection

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
connection = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])

import feeds.views

if __name__ == '__main__':
    app.run()


