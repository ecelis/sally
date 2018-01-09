# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import logging
import scrapy
from sally.qualifiers import QUALIFIER as q

logger = logging.getLogger(__name__)


class SallyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WebsiteItem(scrapy.Item):

    base_url = scrapy.Field()           # Base URL after any 30x redirection
    ecommerce = scrapy.Field()          # Any ecommerce references
    email = scrapy.Field()              # List of email regex
    last_crawl = scrapy.Field()         # Last time I crawled the site
    link = scrapy.Field()              # <a href> tags
    description = scrapy.Field()               # <meta content> tags
    keywords = scrapy.Field()
    onlinepay_rel = scrapy.Field()      # Any mention of on line payment
    score = scrapy.Field()              # Score based on qualifiers
    secure_url = scrapy.Field()         # +1 if HTTPS
    scripts = scrapy.Field()            # <script> tags
    telephone = scrapy.Field()          # List of regexd telephones
    title = scrapy.Field()              # <title> tag
    url = scrapy.Field()                # start_url given by source
    webstore_rel = scrapy.Field()       # Any metion of ecommerce software


    def qualify_product(self):
        products = []
        if type(self['keywords']) is list and len(self['keywords']) > 0 and self['keywords'][0] != '':
            [products.append(p) for p in self['keywords'][0].replace(' ','').split(',') if p in q['products']]
        if type(self['description']) is list and len(self['description']) > 0 and self['description'] != '':
            [products.append(i) for i in self['description'][0].split(' ') if i in q['products']]

            if len(products) < 1 or products[0] is '':
                self['score'] -= 0.2
            # return clean list of useful keywords
            return products


    def qualify(self):
        """Qualify item based on score"""
        self['score'] = 1           # Initialize with 1/5 == five *
        ## lessen score if missing keys
        logger.info(self.qualify_product())
        if not self['email'] or len(self['email']) < 1:         # No emails -1 *
            self['score'] -= 0.2
        if not self['telephone'] or len(self['telephone']) < 1:   # No tels -1 *
            self['score'] -= 0.2
        if not self['ecommerce'] or len(self['ecommerce']) < 1: # no eccomerce -1 *
            self['score'] -= 0.2
        ## increase in half * if secondary keys are found
        if self['secure_url']:
            self['score'] += 0.1

        return self
