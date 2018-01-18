# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import os
import pymongo
import logging
#from scrapy.mail import MailSender
import sendgrid
from sendgrid.helpers.mail import *
import sally.google.spreadsheet as gs

logger = logging.getLogger('sally_lightfoot')


class LightfootPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.sheet_rows = []
        self.spreadsheetId = os.environ['SALLY_SHEET_ID'] or self.setings['SHEET_ID']
        self.collection = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


    @classmethod
    def from_crawler(cls, crawler):
        if os.environ['MONGO_USER'] and os.environ['MONGO_USER'] != '' and os.environ['MONGO_PASSWORD']:
            uri = "mongodb://" + os.environ['MONGO_USER'] + ":" + os.environ['MONGO_PASSWORD'] + "@" + os.environ['MONGO_HOST']
        else:
            uri = "mongodb://" + os.environ['MONGO_HOST']
        logger.debug(uri)
        return cls(
                mongo_uri = uri,
                mongo_db = os.environ['MONGO_DBNAME']
                )


    def to_str(self, item, value):
        if len(item[value]) > 0:
            return ','.join(item[value])
        else:
            return ''


    def export_spreadsheet(self, item):
        """Export items to Google Spreadsheets"""
        ecommerce = item['ecommerce']
        if item['cart'] and len(item['cart']) > 0:
            cart = True
        else:
            cart = False

        row = [
                item['score'],
                item['base_url'],
                self.to_str(item, 'offer'),
                self.to_str(item, 'keywords'),
                ','.join(item['telephone']),
                self.to_str(item, 'email'),
                ecommerce,
                cart,
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
        # Send email with info about the results
        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('MAIL_FROM'))
        to_email = Email(os.environ.get('MAIL_TO'))
        subject = ("[lightfoot] %s" % self.collection)
        content = Content("text/plain", "https://docs.google.com/spreadsheets/d/%s" % self.spreadsheetId)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        ## TODO Fails with builtins.TypeError: 'str' does not support the buffer interface
#        body = "https://docs.google.com/spreadsheets/d/%b" % bytes(self.spreadsheetId, 'utf-8')
#        mailer = MailSender.from_settings(spider.settings)
#        mailer.send(to=['sample@fake.com.mx'],
#                subject="[lighfoot] results %s" % self.collection,body=bytes(self.spreadsheetId, 'utf-8'),
#                attachs=(),mimetype="text/plain",charset='utf-8')


    def process_item(self, item, spider):
        self.db[self.collection].insert_one(dict(item.qualify()))
        # Send to spreadsheet
        self.export_spreadsheet(item)
        return item
