import os
import sys
import re
import datetime
import time
import logging
import logging.handlers
import requests
from mongoengine import connect
from mongoengine import errors
import hermit.model as model
import sally.google.spreadsheet as gs
import sally.google.drive as gd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON)
logger.addHandler(handler)


class HermitCrab(object):
    """Facebook pages crawler"""

    def __init__(self, source_file, spreadsheet, fb_user_id, *args, **kwargs):
        self.spreadsheetId = spreadsheet
        self.config = gs.get_settings()
        logger.debug(self.config)
        self.score = gs.get_score()
        self.collection = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.fb_user_id = fb_user_id
        self.access_token = self.get_token()
        self.graph = 'https://graph.facebook.com'
        self.sheet_rows = [
                ['SCORE', 'WEB SITE', 'ABOUT', 'CATEGORY', 'LIKES', 'TELPHONE',
                    'EMAIL', 'ADDRESS', 'CITY', 'COUNTRY', 'CRAWL DATE']
                ]
        self.categories = []

        lines = ["%s" % str(l).rstrip() for l in gs.get_urls(source_file)]
        gd.mv(source_file, os.environ.get('DRIVE_PROC'))
        fb = re.compile(r'facebook', re.IGNORECASE)
        self.start_urls = list(filter(
            fb.search,
            list(filter(None, ','.join(lines).split(',')))))
        logger.debug(self.start_urls)

        for url in self.start_urls:
            response = self.parse_item(url.split('/')[1])
            if 'error' in response:
                logger.info(response['error']['message'])
            else:
                logger.debug(response)
                self.persist(response)
                if ('location' in response
                        and 'country' in response['location']
                        and response['location']['country']
                        in self.config['allowed_countries']):
                    item = self.process_response(response)
                    row = self.build_row(item)
                    self.sheet_rows.append(row)
            #time.sleep(2)

        # Send to google spreadsheet
        self.insert_sheet(self.sheet_rows)
        gd.mv(source_file, os.environ.get('DRIVE_DONE'))

        # Go get pages alike
        if len(self.categories) > 1:
            for cat in list(set(self.categories)):
                rows = [
                    ['SCORE', 'WEB SITE', 'ABOUT', 'CATEGORY', 'LIKES', 'TELPHONE',
                    'EMAIL', 'ADDRESS', 'CITY', 'COUNTRY', 'CRAWL DATE']
                        ]
                pages = self.search_alike(cat)
                for i in pages['data']:
                    pg_count = 0
                    pg_page = len(pages['data'])
                    logger.debug(i)
                    self.persist(i)
                    if ('location' in i
                            and 'country' in i['location']
                            and i['location']['country']
                            in self.config['allowed_countries']):
                        rows.append(self.build_row(self.process_response(i)))
                    #time.sleep(2)
                logger.debug(rows)
                self.insert_sheet(rows)

        sys.exit(0)

    def insert_sheet(self, rows):
        """Create a Google spreadhseet and insert given rows to it."""
        if len(rows) > 1:
            spreadsheet = gs.create_spreadsheet("fb%s" % self.collection)
            logger.debug(spreadsheet)
            sheet = gs.create_sheet(
                    spreadsheet['spreadsheetId'],
                    self.collection)
            logger.debug(sheet)
            results = gs.insert_to(
                    spreadsheet['spreadsheetId'],
                    self.collection,
                    rows)
            gd.mv(
                    spreadsheet['spreadsheetId'],
                    os.environ.get('DRIVE_RESULTS'))
            logger.debug(results)

    def qualify(self, item):
        """Return score for given item."""
        score = 1
        if ('emails' not in item or not item['emails']):
            score += self.score['email']
        if ('phone' not in item or not item['phone']):
            score += self.score['telephone']
        if ('engagement' not in item or item['engagement']['count'] < 2000):
            score += self.score['likes']

        return score

    def get_token(self):
        """Return Facebook user token from data base."""
        model.mongo_connect()
        try:
            user = model.User.objects(fb_userId=self.fb_user_id).get()
            return user.fb_accessToken
        except Exception as ex:
            logger.error(ex, exc_info=True)
            return None

    def persist(self, item):
        """Persist item to database."""
        try:
            page = model.FbPage(
                page_id=item['id'],
                title=item['name'] if 'name' in item else None,
                about=item['about'] if 'about' in item else None,
                category=item['category'] if 'category' in item else None,
                engagement=item['engagement'] if 'engagement' in item else None,
                emails=item['emails'] if 'emails' in item else None,
                location=item['location'] if 'location' in item else None,
                phone=item['phone'] if 'phone' in item else None,
                website=item['website'] if 'website' in item else None,
                category_list=item['category_list'] if 'category_list' in item else None,
                whatsapp_number=item['whatsapp_number'] if 'whatsapp_number' in item else None,
                link=item['link'] if 'link' in item else None,
                score_values=item['score_values'] if 'score_values' in item else None,
                score=item['score'] if 'score' in item else None,
                )
            return page.save()
        except errors.NotUniqueError as ex:
            logger.error(ex, exc_info=True)
            return None

    def search_alike(self, category):
        """Return related pages by category."""
        query = "search?q=%s&metadata=1" % category
        fields = str(
                '&fields=about,category,contact_address,engagement,emails,'
                'location,phone,website,category_list,description,'
                'has_whatsapp_number,whatsapp_number,hometown,name,products,'
                'rating_count,overall_star_rating,link,'
                'connected_instagram_account&access_token=')
        request = requests.get("%s/%s&type=page%s%s" % (
            self.graph, query, fields,
            self.access_token))
        return request.json()

    def process_response(self, response):
        """Return valid values for response items."""
        item = {}
        item['id'] = response['id']
        if 'website' in response:
            item['website'] = response['website']
        if 'about' in response:
            item['about'] = response['about']
        else:
            item['about'] = None
        if 'category' in response:
            item['category'] = response['category']
            self.categories.append(item['category'])
        else:
            item['category'] = None
        if 'engagement' in response:
            item['likes'] = response['engagement']['count']
        else:
            item['likes'] = None
        if 'phone' in response:
            item['phone'] = response['phone']
        else:
            item['phone'] = None
        if 'emails' in response:
            item['emails'] = ','.join(response['emails'])
        else:
            item['emails'] = None
        if 'location' in response:
            item['city'] = response['location']['city'] if 'city' in response['location'] else None
            item['street'] = response['location']['street'] if 'street' in response['location'] else ''
            item['zip_code'] = response['location']['zip'] if 'zip' in response['location'] else ''
            item['address'] = item['street'] + ', ' + item['zip_code']
            item['country'] = response['location']['country'] if 'country' in response['location'] else None
        else:
            item['city'] = None
            item['address'] = None
            item['country'] = None
        item['score'] = self.qualify(response)
        return item

    def build_row(self, item):
        """Return a row for insert_to google spreadsheet"""
        return [
                item['score'],
                item['website'] if 'website' in item else '',
                item['about'],
                item['category'],
                item['likes'],
                item['phone'],
                item['emails'],
                item['address'],
                item['city'],
                item['country'],
                datetime.datetime.now().strftime("%m%d%Y")
                ]

    def parse_item(self, page):
        """Extract data from facebook pages"""
        fields = str(
                '?fields=about,category,contact_address,engagement,emails,'
                'location,phone,website,category_list,description,'
                'has_whatsapp_number,whatsapp_number,hometown,name,products,'
                'rating_count,overall_star_rating,link,'
                'connected_instagram_account&access_token=')
        request = requests.get("%s/%s%s%s" % (
            self.graph, page, fields,
            self.access_token))
        return request.json()
