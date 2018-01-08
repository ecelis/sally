from datetime import datetime
import re
from urllib.parse import urlparse
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from sally.items import WebsiteItem
#import eat


class BasicCrab(CrawlSpider):
    name = "lightfoot"

    allowed_domains = ['com', 'com.mx']

    rules = (Rule(LinkExtractor(unique=True), callback='parse_link'))

    

    def __init__(self):


        with open('./tests/fixtures/very_small_list.txt', 'r') as f:
            self.start_urls = ["http://%s"  % line.rstrip() for line in f]
        f.close()


    def start_requests(self):
        """Returns iterable of Requests"""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_item)


    def extract_email(self, response, elements, email_set):
        """Extract email from assorted DOM elements"""
        if len(elements) > 0:
            myset = set(response.xpath('//' + elements.pop()).re(
                        r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+'))
            return self.extract_email(response=response,
                    elements=elements,
                    email_set=myset
                    )
        else:
            return email_set


    def to_tel(self, raw, tel_list):
        """Take a list of split telephones and returns a lisf of
       formated telephones"""

        if len(raw) > 0:
            try:
                tel_list.append('-'.join(raw[:raw.index('')]))
                return self.to_tel(raw[raw.index(''):][1:], tel_list)
            except:
                return tel_list
        else:
            return tel_list


    def extract_telephone(self, response, elements, tel_list, tel_set):
        if len(elements) > 0:
            element = elements.pop()
            tel_raw = response.xpath('//' + element).re(
                    r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)')

            if len(tel_list) > 0:
                self.logger.info(tel_list)
                l = self.to_tel(tel_raw, [])
                if len(l) > 0:
                    tel_list.append(l)
                    self.logger.info(set(tel_list))

            return self.extract_telephone(response, elements, tel_list,
                    tel_set)
        else:
            return tel_set


    def parse_item(self, response):
        website_link = [link for link in response.xpath('//a/@href').extract()]
        website_email = list(self.extract_email(response,
            ['div','p','span','a'], set({})))
        self.logger.info(website_email)
        website_telephone = list(self.extract_telephone(response, ['div','p','span','a'],
            [], set({})))
        self.logger.info(website_telephone)
        #website_telephone = response.xpath('//div').re(r'[Tt][Ee][Ll].*[0-9]') # TODO use libtelephone
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
        website['meta'] = response.xpath('//meta/@content').extract()
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
