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


    def __init__(self, csvfile='./tests/fixtures/very_small_list.txt', *args, **kwargs):
#        super(BasicCrab, self).__init__(*args, **kwargs)
        with open(csvfile, 'r') as f:
            if '*' in BasicCrab.allowed_domains:
                self.start_urls = ["http://%s"  % line.rstrip() for line in f]
            else:
                allowed_urls = ["http://%s"  % line.rstrip() for line in f]
                self.start_urls = [
                        url for url in allowed_urls if tldextract.extract(url).suffix in BasicCrab.allowed_domains
                        ]
        f.close()


    def extract_title(self, response):
        try:
            return response.css('title::text').extract_first().strip()
        except err:
            self.logger.error('Extract title %s' % err)
            return 'N/T'


    def extract_email(self, response, elements, email_set=set({})):
        """Extract email from assorted DOM elements"""
        if len(elements) > 0:
            myset = set(response.xpath('//' + elements.pop()).re(
                        r'\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?'))
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
            element = elements.pop()
            tel_334 = response.xpath('//' + element).re(
                    r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)')
            tel_244 = response.xpath('//' + element).re(
                    r'\W(\d{2})\W*(\d{4})\W*(\d{4})\W*(\d*)')
            return self.extract_telephone(response,
                    elements, set(self.to_tel(tel_334)))
        else:
            return tel_set


    def is_ecommerce(self, response):
        """function for findEcommerce"""
        ecommerce = None
        full_text = response.xpath('//meta/@content').extract()
        # TODO we look only for woocommerce right now
        if len(response.xpath('//script/@src').re(r'cdn\.shopify\.com')) > 0:
            # Look for cdn.shopify.com
            return 'shopify'
        if len(response.xpath('//meta[@name="generator"]/@content')
                .re(r'WooCommerce')) > 0:
            return 'woocommerce'
        elif len(response.xpath('//img/@src').re(r'cdn-shoperti\.global')) > 0:
            return 'shoperti'
        elif len(response.xpath('//footer').re(r'magento', re.IGNORECASE)) > 0:
            return 'magento'
        else:
            return 'N/E'
#        elif len(response.xpath(''))

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
        website['title'] = self.extract_title(response)
        website['link'] = website_link
        website['email'] = website_email
        website['telephone'] = website_telephone
        website['ecommerce'] = self.is_ecommerce(response)
        website['description'] = self.extract_description(response)
        website['keywords'] = self.extract_keywords(response)
        # TODO search for ecommerce and online payment
        website['last_crawl'] = datetime.now()

        return website


