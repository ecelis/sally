"""Sally lightfoot web crawler"""
import os
import logging
from datetime import datetime
import re
from urllib.parse import urlparse
import sendgrid
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail
import scrapy
from scrapy.spiders import CrawlSpider
from sally.items import WebsiteItem
import crabs.google.spreadsheet as gs
import crabs.google.drive as gd

logger = logging.getLogger()
handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON)
logger.addHandler(handler)

class BasicCrab(CrawlSpider):
    """Generic web crawler"""

    ELEMENTS = ['div', 'p', 'span', 'a', 'li']

    name = "lightfoot"

    def __init__(
            self,
            csvfile,
            spreadsheet):

        self.source_urls = csvfile
        self.spreadsheetId = spreadsheet
        # Fetch settings from Google spreadsheet
        self.config = gs.get_settings()
        self.score = gs.get_score()

        # Compile regexes
        # allowed_reg list of allowed TDLs to crawl
        allowed_reg = [
            re.compile(
                r"\.%s" % domain,
                re.IGNORECASE) for domain in self.config['allowed_domains']]
        # disallowed_reg list of disallowed TLDs not to crawl
        disallowed_reg = [
            re.compile(r"\.%s" % domain, re.IGNORECASE) for domain
            in self.config['disallowed_domains']]
        # Get lines from csv file and append http schema
        lines = ["http://%s" % str(l).rstrip() for l in gs.get_urls(csvfile)]
        gd.mv(csvfile, os.environ.get('DRIVE_PROC'))
        # Filter allowed TLDs from lines
        allowed_url = []
        for alreg in allowed_reg:
            allowed_url += list(filter(alreg.search, lines))
        # Filter disallowed TLDs from lines
        disallowed_url = []
        for dsalreg in disallowed_reg:
            disallowed_url += list(
                filter(dsalreg.search, list(set(allowed_url))))
        # set start_urls from a set of only useful URLs
        self.start_urls = list(set(allowed_url).difference(
            set(disallowed_url)))

    def extract_title(self, response):
        """Return title from <title> tag"""
        try:
            return response.css('title::text').extract_first().strip()
        except Exception:
            self.logger.error('Extract title %s' % Exception)
            return 'N/T'

    def extract_email(self, response, elements, email_set=None):
        """Return set of emails from given HTML DOM elemnts list"""
        # Important!
        # https://docs.python.org/3/tutorial/controlflow.html#default-argument-values
        if email_set is None:
            email_set = set({})
        if elements:
            myset = set(response.xpath('//' + elements.pop()).re(
                r'\"?([-a-zA-Z0-9.`?{}]+@\w+\.[^png|jpg|gif]\w+\.\w*)"?'))
            return self.extract_email(response, elements, myset)
        return email_set

    def extract_telephone(self, response, elements, tels=None):
        """Extract telephone from elements listed in ELEMENTS

        Returns a set() of telephones
        """
        if tels is None:
            tels = []
        if elements:
            element = elements.pop()
            t334 = []
            t334 = response.xpath('//' + element).re(
                r'\(+(\d{3})\W*(\d{3})\W*(\d{4})\W*(\d*)\W*[^png|jpg|gif]')
            t244 = response.xpath('//' + element).re(
                r'\(+(\d{2})\W*(\d{4})\W*(\d{4})\W*(\d*)\W*[^png|jpg|gif]')
            t_2_8 = response.xpath('//' + element).re(
                r'\(+(\d{2})\W*(\d{8})\W*[^png|jpg|gif]')
            tels.append('-'.join(t334[:3]))
            tels.append('-'.join(t334[3:3]))
            tels.append('-'.join(t334[6:3]))
            tels.append('-'.join(t244[:3]))
            tels.append('-'.join(t244[3:3]))
            tels.append('-'.join(t244[6:3]))
            tels.append('-'.join(t_2_8[:2]))
            tels.append('-'.join(t_2_8[2:2]))
            tels.append('-'.join(t_2_8[4:2]))
            return self.extract_telephone(response, elements, list(
                filter(None, tels)))
        else:
            tset = set(tels)
            self.logger.debug(tset)
            if tset:
                return list(tset)
            return []

    def is_ecommerce(self, response):
        """Very simplistic e-commerce software detection."""
        ecommerce = ''
        if response.xpath('//script/@src').re(r'cdn\.shopify\.com'):
            eccomerce = 'shopify'
        if response.xpath(
                '//meta[@name="generator"]/@content').re(r'WooCommerce'):
            ecommerce = 'woocommerce'
        elif response.xpath('//img/@src').re(r'cdn-shoperti\.global'):
            ecommerce = 'shoperti'
        elif (
                response.xpath('//footer').re(r'[Mm]agento', re.IGNORECASE)
                or response.xpath('//head').re(
                    r'[Mm]agento',
                    re.IGNORECASE)):
            ecommerce = 'magento'
        return ecommerce

    def shoppingcart_detection(self, divs):
        """Simplistic shopping cart detection."""
        result = []
        cart = re.compile(r'cart')
        result += list(filter(cart.search, divs))
        self.logger.debug(result)
        return list(set(result))

    def online_payment(self, links):
        """Return payment methods if any."""
        result = []
        paypal = re.compile(r'paypal.me/\w*')
        result += list(filter(paypal.match, links))
        self.logger.debug(result)
        return result

    def extract_description(self, response):
        """Return descriptoin from <meta name="description"> tags."""
        return response.xpath('//meta[@name="description"]/@content').extract()

    def extract_keywords(self, response):
        """Return keywords from <meta name="keywords" tag."""
        return response.xpath('//meta[@name="keywords"]/@content').extract()

    def extract_social_networks(
            self, response, base_url, found=None, networks=None):
        """
        Return social newtork s from <a href> tags, it matches agaist
        part of the base url.
        """
        if found is None:
            found = set({})
        if networks is None:
            networks = []
        guess_string = ''
        if type(base_url) is str:
            guess_string = base_url
        else:
            if len(base_url) == 2:
                guess_string = base_url[0]
            elif len(base_url) == 3:
                guess_string = base_url[1]

        if networks:
            network = networks.pop()
            found.update(set(response.xpath('//a/@href').re(
                r'(\w*\.' + network + '\/\w*' + guess_string + '\w*)')))
            found.update(set(response.xpath('//a/@href').re(
                r'(\w*\.' + network + '\/\w*' + guess_string[:3] + '\w*)')))
            return self.extract_social_networks(
                response, guess_string, found, networks)

        return found

    def extract_offer(self, website):
        """Return list of matched allowed keywords in website"""
        products = []
        if (website['keywords']
                and isinstance([], type(website['keywords']))
                and website['keywords'][0] != ''):
            [products.append(p) for p
             in website['keywords'][0].replace(' ', '').split(',')
             if p in self.config['allowed_keywords']]
        if (website['description']
                and isinstance([], type(website['description']))
                and website['description'] != ''):
            [products.append(i) for i in website['description'][0].split(' ')
             if i in self.config['allowed_keywords']]

        return products

    def start_requests(self):
        """Returns iterable of Requests"""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

    def parse_item(self, response):
        """Return parsed websites"""
        parsed_url = urlparse(response.url)
        website = WebsiteItem()
        website.set_score(self.score)
        website['spreadsheetId'] = self.spreadsheetId
        website['base_url'] = parsed_url.netloc
        website['secure_url'] = True if parsed_url.scheme == 'https' else False
        website['url'] = response.url
        website['title'] = self.extract_title(response)
        website['link'] = [
            link for link in response.xpath('//a/@href').extract()]
        website['cart'] = self.shoppingcart_detection(
            response.xpath('//div/@class').extract()
            + response.xpath('//a/@class').extract()
            + response.xpath('//i/@class').extract())
        website['network'] = list(
            self.extract_social_networks(
            response, parsed_url.netloc.split('.'), set({}),
            ['facebook\.com', 'instagram\.com', 'twitter\.com']))
        website['email'] = list(
            self.extract_email(response, list(BasicCrab.ELEMENTS)))
        website['telephone'] = self.extract_telephone(
            response, list(BasicCrab.ELEMENTS))
        website['ecommerce'] = self.is_ecommerce(response)
        website['description'] = self.extract_description(response)
        website['keywords'] = self.extract_keywords(response)
        website['offer'] = self.extract_offer(website)
        website['last_crawl'] = datetime.now()
        return website

    def closed(self, reason):
        """Trigerr actions ond crawl end"""
        response = gd.mv(self.source_urls, os.environ.get('DRIVE_DONE'))
        # Send email with info about the results
        mailer = sendgrid.SendGridAPIClient(
            apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('MAIL_FROM'))
        to_email = Email(os.environ.get('MAIL_TO'))
        subject = ("[lightfoot] terminó")
        content = Content(
            "text/plain", "https://docs.google.com/spreadsheets/d/%s"
            % self.spreadsheetId)
        mail = Mail(from_email, subject, to_email, content)
        response = mailer.client.mail.send.post(request_body=mail.get())
        return response
