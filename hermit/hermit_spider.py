import os
import re
import time
import logging
import requests
from mongoengine import connect
import hermit.model as model
import sally.google.spreadsheet as gs

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class HermitCrab(object):

    def __init__(self, source_file, spreadsheet, fb_user_id, *args, **kwargs):
        self.spreadsheetId = spreadsheet
        self.config = gs.get_settings()
        self.score = gs.get_score()
        self.fb_user_id = fb_user_id
        self.access_token = self.get_token()
        self.graph = 'https://graph.facebook.com'
        self.sheet_rows = [
                ['SCORE','WEB SITE', 'OFFER', 'META', 'TELPHONE', 'EMAIL',
                'ECOMMERCE','SHOPPING CART', 'SOCIAL NETWORKS' 'PLACE', 'CRAWL DATE']
                ]

        lines = ["%s" % str(l).rstrip() for l in gs.get_urls(source_file)]
        fb = re.compile(r'facebook', re.IGNORECASE)
        self.start_urls = list(filter(fb.search, list(filter(None, lines))))

        for item in self.start_urls:
            response = self.parse_item(item.split('/')[1])
            if 'error' in response:
#                print(response['error']['message'])
                continue
            else:
                if 'location' in response:
                    city = response['location']['city'] if 'city' in response['location'] else None
                    street = response['location']['street'] if 'street' in response['location'] else ''
                    zip_code = response['location']['zip'] if 'zip' in response['location'] else ''
                    address = street +', '+zip_code
                    country = response['location']['country'] if 'country' in response['location'] else None
                else:
                    city = None
                    address = None
                    country = None

                row = [
                        0,
                        "https://www.facebook.com/%s" % item,
                        response['about'] if'about' in response else None,
                        response['category'] if 'category' in response else None,
                        response['engagement']['count'] if 'engagement' in response else None,
                        response['phone'] if 'phone' in response else None,
                        ','.join(response['emails']) if 'emails' in response else None,
                        address,
                        city,
                        country
                        ]
                print(row)
                self.sheet_rows.append(row)
            time.sleep(3)


    def get_token(self):

        try:
            connect(os.environ.get('MONGO_DBNAME'),
                    host="mongodb://" + os.environ.get('MONGO_HOST'),
                    port=int(os.environ.get('MONGO_PORT')),
                    replicaset=os.environ.get('MONGO_REPLICA_SET'),
                username=os.environ.get('MONGO_USER'),
                password=os.environ.get('MONGO_PASSWORD'))
            user = model.User.objects(fb_userId=self.fb_user_id).get()
            return user.fb_accessToken
        except Exception as ex:
            print(ex)
            return None


    def parse_item(self, page):
        """Extract data from facebook pages"""

        fields = str('?fields=about,category,contact_address,engagement,'
        'emails,location,phone&access_token=')
        #print("%s/%s%s%s" % (self.graph, page, fields,
        #    self.access_token))
        r = requests.get("%s/%s%s%s" % (self.graph, page, fields,
            self.access_token))
        return r.json()
