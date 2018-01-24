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
        print(self.access_token)
        self.graph = 'https://graph.facebook.com'

        lines = ["%s" % str(l).rstrip() for l in gs.get_urls(source_file)]
        fb = re.compile(r'facebook', re.IGNORECASE)
        self.start_urls = list(filter(fb.search, list(filter(None, lines))))

        print(self.start_urls)
        print(len(self.start_urls))

        for item in self.start_urls:
            print(item.split('/')[1])
            self.parse_item(item.split('/')[1])
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
            print(user)
            return user.fb_accessToken
        except Exception as ex:
            print(ex)
            return None


    def parse_item(self, page):
        """Extract data from facebook pages"""

        fields = str('?fields=about,category,contact_address,engagement,'
        'emails,location,phone&access_token=')
        print("%s/%s%s%s" % (self.graph, page, fields,
            self.access_token))
        r = requests.get("%s/%s%s%s" % (self.graph, page, fields,
            self.access_token))
        print(r.text)
        print(r.json())
        return None
