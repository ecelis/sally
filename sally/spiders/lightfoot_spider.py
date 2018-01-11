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

    # TODO make allowed_domains dynamic
    allowed_domains = ['com', 'com.mx', 'mx']

    # TODO make disallowed_domains dynamic
    disallowed_domains = []

    # TODO I still don't knpw what to do with the rules
    rules = (Rule(LinkExtractor(unique=True), callback='parse_link'))


    def __init__(self, csvfile='./tests/fixtures/very_small_list.txt',
            *args, **kwargs):

        ## TODO check for file existence or throw exception and exit
        with open(csvfile, 'r') as f:
            if '*' in self.allowed_domains:
                self.start_urls = ["http://%s"  % line.rstrip() for line in f]
            else:
                allowed_urls = ["http://%s"  % line.rstrip() for line in f]
                self.start_urls = [
                        url for url in allowed_urls if tldextract.extract(url).suffix in BasicCrab.allowed_domains
                        ]
        f.close()


    def extract_title(self, response):
        """extract_title from <title> tag

        Returns {str} title"""
        try:
            return response.css('title::text').extract_first().strip()
        except Exception:
            self.logger.error('Extract title %s' % Exception)
            return 'N/T'


    def extract_email(self, response, elements, email_set=set({})):
        """Extract email from elements listed in ELEMENTS

        Returns a set() of emails
        """
        if len(elements) > 0:
            myset = set(response.xpath('//' + elements.pop()).re(
                        r'\"?([-a-zA-Z0-9.`?{}]+@\w+\.[^png|jpg|gif]\w+\.\w*)"?'))
            return self.extract_email(response, elements, myset)
        else:
            return email_set


    def to_tel(self, raw, code, tel_list=[]):
        """Take a list of split telephones and returns a lisf of
       formated telephones

       Code 10 3 numbers for LADA
       Code 12 2 number is country code next 3 LADA

       Returns a list of telephones
       """
        if len(raw) > 0:
            try:
                num = '-'.join(raw[:raw.index('')])
                if len(num.replace('-','')) == code:
                    tel_list.append(num)
                return self.to_tel(raw[raw.index(''):][1:], code, tel_list)
            except:
                # First param here must be empty list always
                return self.to_tel([], code, tel_list)
        else:
            return tel_list


    def extract_telephone(self, response, elements, tel_set=set({})):
        """Extract telephone list from ELEMENTS

        Return a set of formated telephones
        """
        if len(elements) > 0:
            element = elements.pop()
            tel_set.update(set(self.to_tel(response.xpath('//' + element).re(
                    r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 10)))
            tel_set.update(set(self.to_tel(response.xpath('//' + element).re(
                    r'\W(\d{2})\W*(\d{4})\W*(\d{4})\W*(\d*)'), 10)))
            tel_set.update(set(self.to_tel(response.xpath('//' + element).re(
                    r'\+(\d{2})\W*(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 12)))
            return self.extract_telephone(response,
                    elements, tel_set)
        else:
            return tel_set


    def is_ecommerce(self, response):
        """Very simplistic e-commerce software detection

        Returns str of ecommerce software"""
        ecommerce = None
        full_text = response.xpath('//meta/@content').extract()
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


    def extract_description(self, response):
        """extract_description from <meta name="description"> tags

        Returns list of descriptio"""
        return response.xpath('//meta[@name="description"]/@content').extract()


    def extract_keywords(self, response):
        """extract_keywords from <meta name="keywords" tag.

        Returns list of keywords"""
        return response.xpath('//meta[@name="keywords"]/@content').extract()


    def extract_social_networks(self, response, base_url,
            found=set({}), networks=list(QUALIFIER['network'])):
        """extract_social_networks from <a href> tags, it matches agaist
        part of the base url.

        Returns set of social networks url found"""
        s = ''
        if type(base_url) is str:
            s = base_url
        else:
            if len(base_url) == 2:
                s = base_url[0]
            elif len(base_url) == 3:
                s = base_url[1]

        if len(networks) > 0:
            n = networks.pop()
            found.update(set(response.xpath('//a/@href').re(
                    r'(\w*\.' + n + '\/\w*' + s + '\w*)')))
            found.update(set(response.xpath('//a/@href').re(
                r'(\w*\.' + n + '\/\w*' + s[:3] + '\w*)')))
            return self.extract_social_networks(response, s, found,
                    networks)

        return found


    def start_requests(self):
        """Returns iterable of Requests"""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_item)


    def parse_link(self, link):
        self.logger.info(link)


    def parse_item(self, response):
        # Collect all links found in crawled pages
        website_link = [link for link in response.xpath('//a/@href').extract()]
        website_email = list(self.extract_email(response,
            list(BasicCrab.ELEMENTS)))
        website_telephone = list(self.extract_telephone(response,
            list(BasicCrab.ELEMENTS), set({})))
        parsed_url = urlparse(response.url)
        website_network = list(self.extract_social_networks(response,
            parsed_url.netloc.split('.'), set({}), list( QUALIFIER['network'])))

        website = WebsiteItem()
        website['base_url'] = parsed_url.netloc
        website['secure_url'] = True if parsed_url.scheme == 'https' else False
        website['url'] = response.url
        website['title'] = self.extract_title(response)
        website['link'] = website_link
        website['network'] = website_network
        website['email'] = website_email
        website['telephone'] = website_telephone
        website['ecommerce'] = self.is_ecommerce(response)
        website['description'] = self.extract_description(response)
        website['keywords'] = self.extract_keywords(response)
        # TODO search for ecommerce and online payment
        website['last_crawl'] = datetime.now()

        return website


