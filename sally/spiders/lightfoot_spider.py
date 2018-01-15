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
import sally.google.spreadsheet as gs
#import eat


class BasicCrab(CrawlSpider):
    ELEMENTS = ['div', 'p', 'span', 'a', 'li']

    name = "lightfoot"

    # TODO I still don't knpw what to do with the rules
    rules = (Rule(LinkExtractor(unique=True), callback='parse_link'))


    def __init__(self, csvfile='./tests/fixtures/very_small_list.txt',
            *args, **kwargs):

        self.settings = gs.get_settings()
        self.score = gs.get_score()

        # Compile regex
        allowed_reg = [re.compile(r"\.%s" % domain) for domain in self.settings['allowed_domains']]
        disallowed_reg = [re.compile(r"\.%s" % domain) for domain in self.settings['disallowed_domains']]

        ## TODO check for file existence or throw exception and exit
        lines = []
        with open(csvfile, 'r') as f:
            lines = ["http://%s" % l.rstrip() for l in f]
            f.close()

        allowed_url = []
        for r in allowed_reg:
            allowed_url += list(filter(r.search, lines))

        disallowed_url = []
        for r in disallowed_reg:
            disallowed_url += list(filter(r.search, list(set(allowed_url))))

        self.start_urls = list(set(allowed_url).difference(set(disallowed_url)))


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


    def shoppingcart_detection(self, divs):
        result = []
        p = re.compile(r'cart')
        result += list(filter(p.search, divs))

        self.logger.debug(result)
        return list(set(result))


    def online_payment(self, links):
        elements = list(BasicCrab.ELEMENTS)
        result = []
        r = re.compile(r'paypal.me/\w*')
        result += list(filter(r.match, links))
        self.logger.debug(result)
        return result


    def extract_description(self, response):
        """extract_description from <meta name="description"> tags

        Returns list of descriptions"""
        return response.xpath('//meta[@name="description"]/@content').extract()


    def extract_keywords(self, response):
        """extract_keywords from <meta name="keywords" tag.

        Returns list of keywords"""
        return response.xpath('//meta[@name="keywords"]/@content').extract()


    def extract_social_networks(self, response, base_url,
            found=set({}), networks=[]):
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


    def clearset(self):
        s = set({})
        s.clear()
        return s

    def parse_item(self, response):
        # Collect all links found in crawled pages
#        website_link = [link for link in response.xpath('//a/@href').extract()]
        website_email = list(self.extract_email(response,
            list(BasicCrab.ELEMENTS)))
        website_telephone = list(self.extract_telephone(response,
            list(BasicCrab.ELEMENTS),
            self.clearset()))
        parsed_url = urlparse(response.url)
        website_network = list(self.extract_social_networks(response,
            parsed_url.netloc.split('.'), set({}),
            ['facebook\.com','instagram\.com','twitter\.com']))

        website = WebsiteItem()
        website.set_score(self.score)
        website['base_url'] = parsed_url.netloc
        website['secure_url'] = True if parsed_url.scheme == 'https' else False
        website['url'] = response.url
        website['title'] = self.extract_title(response)
        website['link'] = [link for link in response.xpath('//a/@href').extract()]
        website['cart'] = self.shoppingcart_detection(
            response.xpath('//div/@class').extract() + response.xpath('//a/@class').extract() + response.xpath('//i/@class').extract())
        #self.online_payment(response.xpath('//div/@class').extract())
        website['network'] = website_network
        website['email'] = website_email
        website['telephone'] = website_telephone
        website['ecommerce'] = self.is_ecommerce(response)
        website['description'] = self.extract_description(response)
        website['keywords'] = self.extract_keywords(response)
        # TODO search for ecommerce and online payment
        website['last_crawl'] = datetime.now()

        return website


