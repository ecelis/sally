from datetime import datetime
import re
from urllib.parse import urlparse
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from sally.items import WebsiteItem
#import eat


class BasicCrab(Crawler):
    name = "lightfoot"

    allowed_domains = ['com.mx']

    rules = (Rule(LinkExtractor(unique=True), callback='parse_link'))


    def __init__(self):
        with open('./tests/fixtures/very_small_list.txt', 'r') as f:
            self.start_urls = ["http://%s"  % line.rstrip() for line in f]
        f.close()


    def start_requests(self):
        """Returns iterable of Requests"""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_item)


    def parse_item(self, response):
        website_link = [link for link in response.xpath('//a/@href').extract()]
        website_email = [email for email in
                response.xpath('//div').re(r'[A-Za-z0-9].*@.*')]
        website_telephone = response.xpath('//div').re(r'[Tt][Ee][Ll].*[0-9]') # TODO use libtelephone
        parsed_url = urlparse(response.url)

        website = WebsiteItem()
        website['base_url'] = parsed_url.netloc
        website['secure_url'] = True if parsed_url.scheme == 'https' else False
        website['url'] = response.url
        website['title'] = response.css('title::text').extract_first().strip()
        website['link'] = website_link
        website['email'] = website_email
        website['telephone'] = website_telephone
        website['ecommerce'] = self.find_ecommerce(response.xpath('//meta/@content').extract())
        #website['meta'] = response.xpath('//meta/@content').extract()
        #website['scripts'] = response.xpath('//script').extract()
        # TODO search for ecommerce and online payment
        website['last_crawl'] = datetime.now()

        return website


    def find_ecommerce(self, full_text):
        """function for findEcommerce"""
        # TODO we look only for woocommerce right now
        r = re.compile('[Ww]oo[Cc]ommerce')
        ecommerce = filter(r.match, full_text)
        return list(ecommerce)
