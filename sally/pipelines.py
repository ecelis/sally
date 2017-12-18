# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class SallyPipeline(object):
    def process_item(self, item, spider):
        return item


class LightfootPipeline(object):

    collection = 'lightfoot'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                mongo_uri=crawler.settings.get('MONGO_URI'), #'mongodb://127.0.0.1:27017/items',
                mongo_db=crawler.settings.get('MONGO_DATABASE', 'sally') #'items'
                )


    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_spider(self, spider):
        self.client.close()


    def process_item(self, item, spider):
        self.db[self.collection].insert_one(dict(item))
        return item
