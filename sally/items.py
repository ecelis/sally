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
    url = scrapy.Field()
    title = scrapy.Field()
    links = scrapy.Field()              # <a href> tags
    email = scrapy.Field()
    telephone = scrapy.Field()
    meta = scrapy.Field()                # <meta content> tags
    scripts = scrapy.Field()             # <script> tags, useful to detect
                                        # ecommerce or online payments
    webstore_rel = scrapy.Field()        # Any metion of ecommerce software
    onlinepay_rel = scrapy.Field()       # Any mention
    last_crawl = scrapy.Field()
