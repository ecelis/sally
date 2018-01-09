from datetime import datetime
import re
from urllib.parse import urlparse
import tldextract
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from sally.items import WebsiteItem
from sally.qualifiers import QUALIFIER
#import eat


class BasicCrab(CrawlSpider):
    ELEMENTS = ['div', 'p', 'span', 'a', 'li']

    name = "lightfoot"

    allowed_domains = ['com', 'com.mx']

    rules = (Rule(LinkExtractor(unique=True), callback='parse_link'))


    def __init__(self, csvfile='', *args, **kwargs):
#        super(BasicCrab, self).__init__(*args, **kwargs)
        with open(csvfile, 'r') as f:
            allowed_urls = ["http://%s"  % line.rstrip() for line in f]
            self.start_urls = [
                    url for url in allowed_urls if tldextract.extract(url).suffix in BasicCrab.allowed_domains
                    ]
        f.close()


    def extract_email(self, response, elements, email_set=set({})):
        """Extract email from assorted DOM elements"""
        if len(elements) > 0:
            myset = set(response.xpath('//' + elements.pop()).re(
                        r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+'))
            return self.extract_email(response, elements, myset)
        else:
            return email_set


    def to_tel(self, raw, tel_list=[]):
        """Take a list of split telephones and returns a lisf of
       formated telephones"""
        if len(raw) > 0:
            try:
                number = '-'.join(raw[:raw.index('')])
                if len(number.replace('-','')) == 10:
                    tel_list.append(number)
                return self.to_tel(raw[raw.index(''):][1:], tel_list)
            except:
                # First param here must be empty list always
                return self.to_tel([], tel_list)
        else:
            if len(tel_list) > 0:
                return list(set(tel_list))
            else:
                return tel_list


    def extract_telephone(self, response, elements, tel_set=set({})):
        """Extract telephone list"""
        if len(elements) > 0:
            tel_raw = response.xpath('//' + elements.pop()).re(
                    r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)')
            return self.extract_telephone(response,
                    elements, set(self.to_tel(tel_raw)))
        else:
            return tel_set


    def is_ecommerce(self, response):
        """function for findEcommerce"""
        ecommerce = None
        full_text = response.xpath('//meta/@content').extract()
        # TODO we look only for woocommerce right now
        self.logger.info(QUALIFIER['ecommerce'])
        while len(QUALIFIER['ecommerce']) > 0:
            e = QUALIFIER['ecommerce'].pop()
            r = re.compile(e, re.IGNORECASE)
            ecommerce = filter(r.match, full_text)

            self.logger.info(ecommerce)
            if ecommerce:
                return list(ecommerce)
            else:
                return []


    def extract_description(self, response):
        return response.xpath('//meta[@name="description"]/@content').extract()


    def extract_keywords(self, response):
        l = response.xpath('//meta[@name="keywords"]/@content').extract()
        return l


    def start_requests(self):
        """Returns iterable of Requests"""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_item)


    def parse_item(self, response):
        website_link = [link for link in response.xpath('//a/@href').extract()]
        website_email = list(self.extract_email(response,
            list(BasicCrab.ELEMENTS)))
        website_telephone = list(self.extract_telephone(response,
            list(BasicCrab.ELEMENTS)))
        parsed_url = urlparse(response.url)

        website = WebsiteItem()
        website['base_url'] = parsed_url.netloc
        website['secure_url'] = True if parsed_url.scheme == 'https' else False
        website['url'] = response.url
        website['title'] = response.css('title::text').extract_first().strip()
        website['link'] = website_link
        website['email'] = website_email
        website['telephone'] = website_telephone
        website['ecommerce'] = self.is_ecommerce(response)
        website['description'] = self.extract_description(response)
        website['keywords'] = self.extract_keywords(response)
        #website['scripts'] = response.xpath('//script').extract()
        # TODO search for ecommerce and online payment
        website['last_crawl'] = datetime.now()

        return website


