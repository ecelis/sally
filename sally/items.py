# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SallyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class WebsiteItem(scrapy.Item):

    base_url = scrapy.Field()           # Base URL after any 30x redirection
    email = scrapy.Field()              # List of email regex
    last_crawl = scrapy.Field()         # Last time I crawled the site
    link = scrapy.Field()              # <a href> tags
    meta = scrapy.Field()               # <meta content> tags
    onlinepay_rel = scrapy.Field()      # Any mention of on line payment
    score = scrapy.Field()              # Score based on qualifiers
    secure_url = scrapy.Field()         # +1 if HTTPS
    scripts = scrapy.Field()            # <script> tags
    telephone = scrapy.Field()          # List of regexd telephones
    title = scrapy.Field()              # <title> tag
    url = scrapy.Field()                # start_url given by source
    webstore_rel = scrapy.Field()       # Any metion of ecommerce software

    def qualify(self):
        self['score'] = 5           # Initialize with five stars
        if not self['email'] or len(self['email']) < 1:         # No emails -1
            self['score'] -= 1
        if not self['telephone'] or len(self['telephone']) < 1:   # No tels -1
            self['score'] -= 1

        return self
