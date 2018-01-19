from datetime import datetime
import re
from urllib.parse import urlparse
import tldextract
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from sally.items import WebsiteItem
import sally.google.spreadsheet as gs


class BasicCrab(CrawlSpider):

    ELEMENTS = ['div', 'p', 'span', 'a', 'li']

    name = "lightfoot"

    # TODO I still don't knpw what to do with the rules
    rules = (Rule(LinkExtractor(unique=True), callback='parse_link'))

    def __init__(self, csvfile='./tests/fixtures/very_small_list.txt',
            *args, **kwargs):

        # Fetch settings from Google spreadsheet
        self.config = gs.get_settings()
        self.score = gs.get_score()

        # Compile regexes
        # allowed_reg list of allowed TDLs to crawl
        allowed_reg = [re.compile(r"\.%s" % domain) for domain
                in self.config['allowed_domains']]
        # disallowed_reg list of disallowed TLDs not to crawl
        disallowed_reg = [re.compile(r"\.%s" % domain) for domain
                in self.config['disallowed_domains']]

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


    def extract_telephone(self, response, elements, myset=set({})):
        """Extract telephone from elements listed in ELEMENTS

        Returns a set() of telephones
        """
        if len(elements) > 0:
            mylist = response.xpath('//' + elements.pop()).re(
                r'\(+(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)\W*[^png|jpg|gif]')
            tels = []
            tels.append('-'.join(mylist[:3]))
            tels.append('-'.join(mylist[3:3]))
            tels.append('-'.join(mylist[6:3]))
            tels.append('-'.join(mylist[9:3]))
            tels.append('-'.join(mylist[12:3]))
            tels.append('-'.join(mylist[15:3]))
            self.logger.debug(myset)
            return self.extract_telephone(response, elements, myset)
        else:
            self.logger.debug(myset)
            return list(myset)


#    def extract_telephone(self, response, elements, tel_set=set({})):
#        """Extract telephone list from ELEMENTS
#
#        Return a set of formated telephones
#        """
#        if len(elements) > 0:
#        element = 'div' #elements.pop()
#        div_334 = set(self.to_tel(response.xpath('//' + element).re(
#            r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 10))
#        div_244 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\W(\d{2})\W*(\d{4})\W*(\d{4})\W*(\d*)'), 10))
#        div_12 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\+(\d{2})\W*(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 12))
#        element = 'li' #elements.pop()
#        li_334 = set(self.to_tel(response.xpath('//' + element).re(
#            r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 10))
#        li_244 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\W(\d{2})\W*(\d{4})\W*(\d{4})\W*(\d*)'), 10))
#        li_12 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\+(\d{2})\W*(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 12))
#        element = 'span' #elements.pop()
#        span_334 = set(self.to_tel(response.xpath('//' + element).re(
#            r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 10))
#        span_244 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\W(\d{2})\W*(\d{4})\W*(\d{4})\W*(\d*)'), 10))
#        span_12 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\+(\d{2})\W*(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 12))
#        element = 'a' #elements.pop()
#        a_334 = set(self.to_tel(response.xpath('//' + element).re(
#            r'(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 10))
#        a_244 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\W(\d{2})\W*(\d{4})\W*(\d{4})\W*(\d*)'), 10))
#        a_12 = set(self.to_tel(response.xpath('//' + element).re(
#            r'\+(\d{2})\W*(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)'), 12))



            #num = '-'.join(raw[:raw.index('')])
#            if len(num.replace('-','')) == 10:
#                tel_list.append(num)
#            return self.to_tel(raw[raw.index(''):][1:], code, tel_list)

            #return self.extract_telephone(response,
#                    elements, tel_set)
#        else:
#        return a_334.union(a_244.union(a_12.union(
#            li_334.union(li_244.union(li_12.union(
#            span_334.union(span_244.union(span_12.union(
#            div_334.union(div_244.union(div_12)))))))))))


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
        elif (len(response.xpath('//footer').re(r'magento', re.IGNORECASE)) > 0
              or len(response.xpath('//head').re(r'magento', re.IGNORECASE)) > 0)
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


    def extract_offer(self, website):
        # TODO make it better to store array of useful products in self['keywords']
        products = []
        if (type(website['keywords']) is list
            and len(website['keywords']) > 0 and website['keywords'][0] != ''):
            [products.append(p) for p
                    in website['keywords'][0].replace(' ','').split(',')
                    if p in self.config['allowed_keywords']]
        if (type(website['description']) is list
                and len(website['description']) > 0 and website['description'] != ''):
            [products.append(i) for i in website['description'][0].split(' ')
                    if i in self.config['allowed_keywords']]

        return products


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
        website_telephone = self.extract_telephone(response,
            list(BasicCrab.ELEMENTS))
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
        website['offer'] = self.extract_offer(website)
        website['last_crawl'] = datetime.now()

        return website


