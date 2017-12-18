from datetime import datetime
from urllib.parse import urlparse
import scrapy
from scrapy.loader import ItemLoader
#from scrapy import ItemLoader
from sally.items import WebsiteItem
#import eat


class BasicCrab(scrapy.Spider):
    name = "lightfoot"


    def __init__(self):
        with open('./tests/fixtures/very_small_list.txt', 'r') as f:
            self.start_urls = ["http://%s"  % line.rstrip() for line in f]
        f.close()


    def start_requests(self):
        """Returns iterable of Requests"""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_item)


    def parse_item(self, response):
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
        #print(response.xpath('//td/text()').re(r'Tel\..*'))
        parsed_url = urlparse(response.url)
        website = WebsiteItem()
        website['base_url'] = parsed_url.netloc
        website['secure_url'] = True if parsed_url.scheme == 'https' else False
        website['url'] = response.url
        website['title'] = response.css('title::text').extract_first().strip()
        #website['links'] = response.xpath('//a/@href').extract()
        #website['email'] = response.xpath('//div').re(r'[A-Za-z0-9].*@.*\.com\.*')
        #website['telephone'] = response.xpath('//div').re(r'[Tt][Ee][Ll].*[0-9]') # TODO use libtelephone
        #website['meta'] = response.xpath('//meta/@content').extract()
        #website['scripts'] = response.xpath('//script').extract()
        # TODO search for ecommerce and online payment
        website['last_crawl'] = datetime.now()

        yield website
