# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import os
import pymongo
import logging
import sally.spreadsheets as gs

logger = logging.getLogger('sally_lightfoot')

class SallyPipeline(object):
    def process_item(self, item, spider):
        return item


class LightfootPipeline(object):

    collection = 'lightfoot'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.sheet_rows = []


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                mongo_uri=crawler.settings.get('MONGO_HOST'), #'mongodb://127.0.0.1:27017/items',
                mongo_db=crawler.settings.get('MONGO_DBNAME', 'sally') #'items'
                )


    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.spreadsheetId = os.environ['SALLY_SHEET_ID'] or self.setings['SHEET_ID']
        self.sheet = os.environ['SALLY_SHEET_NAME'] or self.settings['SHEET_NAME']
        self.sheet_rows = []


    def close_spider(self, spider):
        self.client.close()
        gs.insert_to(self.spreadsheetId, self.sheet, self.sheet_rows)


    def process_item(self, item, spider):
        self.db[self.collection].insert_one(dict(item.qualify()))
        # Send to spreadsheet
        # TODO put extract of first item in a function
        if(len(item['email']) > 0):
            email = item['email'][0]
        else:
            email = ''
        if(len(item['telephone']) > 0):
            telephone = item['telephone'][0]
        else:
            telephone = ''
        ecommerce = item['ecommerce']
        if len(item['keywords']) > 0:
            keywords = item['keywords'][0]
        else:
            keywords = ''
        row = [
                item['score'],
                item['base_url'],
                keywords,          # item['oferta']
                telephone,          # item['telephone']
                email,          # item['email']
                ecommerce,          # item['ecommerce']
                'N/L',          # item['place']
                datetime.datetime.now().strftime('%m/%d/%Y')
                ]
        self.sheet_rows.append(row)
        logger.info(self.sheet_rows)
        return item
