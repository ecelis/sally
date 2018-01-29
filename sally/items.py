# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import logging
import scrapy
from sally.qualifiers import QUALIFIER as q

logger = logging.getLogger(__name__)


class WebsiteItem(scrapy.Item):


    base_url = scrapy.Field()           # Base URL after any 30x redirection
    ecommerce = scrapy.Field()          # Any ecommerce references
    email = scrapy.Field()              # List of email regex
    last_crawl = scrapy.Field()         # Last time I crawled the site
    link = scrapy.Field()              # <a href> tags
    network = scrapy.Field()              # <a href> tags
    description = scrapy.Field()               # <meta content> tags
    keywords = scrapy.Field()
    offer = scrapy.Field()
    onlinepay_rel = scrapy.Field()      # Any mention of on line payment
    cart = scrapy.Field()
    score = scrapy.Field()              # Score based on qualifiers
    secure_url = scrapy.Field()         # +1 if HTTPS
    scripts = scrapy.Field()            # <script> tags
    telephone = scrapy.Field()          # List of regexd telephones
    country_code = scrapy.Field()
    title = scrapy.Field()              # <title> tag
    url = scrapy.Field()                # start_url given by source
    webstore_rel = scrapy.Field()       # Any metion of ecommerce software
    score_values = scrapy.Field()
    spreadsheetId = scrapy.Field()


    def set_score(self, scores):
        self['score_values'] = dict(scores)


    def qualify_product(self):
        """qualify_product eval <meta> tags from item mathing description and
        keywords parameters of such tags. a href tags are also searched

        If products aren't found in QUALIFIE['product'] -0.2 is substracted
        from self['score']

        Return products list"""
        if len(self['offer']) < 1 or self['offer'][0] is '':
            self['score'] += self['score_values']['offer']
        # return clean list of useful keywords
        return self['offer']


    def qualify_social_network(self):
        """qualify_social_network substracts -0.2 from self['score'] if
        self['network'] is empty

        Returns list of social networks"""
        if type(self['network']) != list or len(self['network']) < 1 or self['network'][0] is '':
            self['score'] += self['score_values']['network']

        return self['network']


    def qualify(self):
        """Qualify item based on qualify_product, qualify_social_network,
        if self['email'] is empty, self['telephones'] is empty, self['ecommerce']
        -0.2 is substracted for each missing value. Score starts at 1.0.

        Extra qualifires: https +0.1"""
        self['score'] = 1           # Initialize with 1/5 == five *
        ## lessen score if missing keys
        self.qualify_product()
        self.qualify_social_network()
        if not self['email'] or len(self['email']) < 1:         # No emails -1 *
            self['score'] += self['score_values']['email']
        if not self['telephone'] or len(self['telephone']) < 1:   # No tels -1 *
            self['score'] += self['score_values']['telephone']
        if not self['ecommerce'] or len(self['ecommerce']) < 1: # no eccomerce -1 *
            self['score'] += self['score_values']['ecommerce']
        ## increase in half * if secondary keys are found
        if self['secure_url']:
            self['score'] += self['score_values']['secure_url']
        if not self['cart'] or len(self['cart']) < 1:
            self['score'] += self['score_values']['cart']

        return self
