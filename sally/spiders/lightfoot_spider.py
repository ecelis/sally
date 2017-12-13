from datetime import datetime
import scrapy
from sally.items import WebsiteItem
#import eat


class BasicCrab(scrapy.Spider):
    name = "lightfoot"

    def __init__(self):
        #with open('./tests/fixtures/sample_small_list.txt', 'r') as f:
        #    self.start_urls = ["http://%s"  % line.rstrip() for line in f]
        #f.close()
        self.start_urls = ['https://www.liverpool.com.mx/',
                'https://www.lolyinthesky.com.mx/',
                'http://tunacorazon.com',
                'http://tonaliartesanal.com',
                'http://ferrefama.com/']

    """
        response.xpath(//a/@href)  get links
    """

    def parse(self, response):
        """
        Save pages locally"
        page = response.url.split("/")[-2]
        filename = './garbage/lead-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        f.close()
        """
        #for sel in response.xpath('//a/@href'):
            #print(sel)
        website = WebsiteItem()
        website['url'] = response.url
        website['title'] = response.css('title::text').extract_first().strip()
        website['links'] = response.xpath('//a/@href').extract()
        website['last_crawl'] = datetime.now()

        yield website
