import os
from mongoengine import *


class HermitMongo:

    def __init__(self):
        connect('sally', host=os.environ.get('MONGO_HOST',
            username=os.environ.get('MONGO_USER'),
            password=os.environ.get('MONGO_PASSWORD')))

class User(Document):

    email = StringField(required=True)
    fb_userId = StringField(required=True)
    fb_accessToken = StringField(requied=True)

    def __init__(self):
        connect('sally', host=os.environ.get('MONGO_HOST',
            username=os.environ.get('MONGO_USER'),
            password=os.environ.get('MONGO_PASSWORD')))


