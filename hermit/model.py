import os
from mongoengine import *


#class HermitMongo:
#
#    def __init__(self):
#        connect('sally', host=os.environ.get('MONGO_HOST',
#            username=os.environ.get('MONGO_USER'),
#            password=os.environ.get('MONGO_PASSWORD')))

def mongo_connect():
    """Ëstablish a MongoDB connetion"""
    try:
        connect(os.environ.get('MONGO_DBNAME'),
                host="mongodb://" + os.environ.get('MONGO_HOST'),
                port=int(os.environ.get('MONGO_PORT')),
                replicaset=os.environ.get('MONGO_REPLICA_SET'),
                username=os.environ.get('MONGO_USER'),
                password=os.environ.get('MONGO_PASSWORD'))
    except Exception:
        return {'status': 500, 'statusText': 'Can\'t connect to MongoDB'}



class User(Document):

    name = StringField()
    email = EmailField(required=True)
    fb_userId = StringField(required=True, unique=True)
    fb_accessToken = StringField(requied=True)


class FbPage(DynamicDocument):
    title = StringField()
    about = StringField()
    category = StringField()
    engagement = DictField()
    emails = ListField(EmailField())
    location = DictField()
    phone = StringField()
    website = StringField()
    category_list = ListField(DictField())
    whatsapp_number = StringField()
    link = URLField()
    score_values = DictField()
    score = FloatField()
    last_crawl = DateTimeField()
