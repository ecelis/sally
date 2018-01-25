import os
from mongoengine import *


#class HermitMongo:
#
#    def __init__(self):
#        connect('sally', host=os.environ.get('MONGO_HOST',
#            username=os.environ.get('MONGO_USER'),
#            password=os.environ.get('MONGO_PASSWORD')))

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
    website = URLField()
    category_list = ListField(DictField())
    whatsapp_number = StringField()
    link = URLField()
    score_values = DictField()
    score = FloatField()
    last_crawl = DateTimeField()
