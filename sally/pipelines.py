# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import os
import pymongo
import logging
import sally.spreadsheet as gs

logger = logging.getLogger('sally_lightfoot')

class SallyPipeline(object):
    def process_item(self, item, spider):
        return item


class LightfootPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.sheet_rows = []
        self.spreadsheetId = os.environ['SALLY_SHEET_ID'] or self.setings['SHEET_ID']
        self.collection = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') #os.environ['SALLY_SHEET_NAME'] or self.settings['SHEET_NAME']


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                mongo_uri = crawler.settings.get('MONGO_HOST'),
                mongo_db = crawler.settings.get('MONGO_DBNAME', 'sally')
                )


    def to_str(self, item, value):
        if len(item[value]) > 0:
            return ','.join(item[value])
        else:
            return ''


    def export_spreadsheet(self, item):
        """Export items to Google Spreadsheets"""
        ecommerce = item['ecommerce']
        row = [
                item['score'],
                item['base_url'],
                self.to_str(item, 'offer'),
                self.to_str(item, 'keywords'),
                self.to_str(item, 'telephone'),
                self.to_str(item, 'email'),
                ecommerce,
                self.to_str(item, 'network'),
                'N/L',
                datetime.datetime.now().strftime('%m/%d/%Y')
                ]
        self.sheet_rows.append(row)


    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_spider(self, spider):
        self.client.close()
        # Create sheet in google
        gs.create_sheet(self.spreadsheetId, self.collection)
        gs.insert_to(self.spreadsheetId, self.collection, self.sheet_rows)


    def process_item(self, item, spider):
        self.db[self.collection].insert_one(dict(item.qualify()))
        # Send to spreadsheet
        self.export_spreadsheet(item)
        return item
