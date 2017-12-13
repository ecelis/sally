import scrapy
import eat


class BasicCrab(scrapy.Spider):
    name = "lightfoot"

    start_urls = ['http://www.liverpool.com.mx', 'http://www.sat.gob.mx'] #eat.feed_csv()
