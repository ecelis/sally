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
    links = scrapy.Field()
    last_crawl = scrapy.Field()
