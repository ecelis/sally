import os
import re
import logging
import requests
from mongoengine import connect
import model
import sally.google.spreadsheet as gs

logger = logging.getLogger(__name__)


class HermitCrab(object):

    def __init__(self, source_file, spreadsheet, fb_user_id, *args, **kwargs):
        self.spreadsheetId = spreadsheet
        self.config = gs.get_settings()
        self.score = gs.get_score()
        self.fb_user_id = fb_user_id
        self.access_token = self.get_token()
        self.graph = 'https://graph.facebook.com'

        lines = ["%s" % str(l).rstrip() for l in gs.get_urls(source_file)]
        fb = re.compile(r'facebook', re.IGNORECASE)
        self.start_urls = list(filter(fb.search, list(filter(None, lines))))
        print(self.start_urls)


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
        except Exception:
            return None


    def parse_item(self, page):
        """Extract data from facebook pages"""

        fields = str('?fields=about,category,contact_address,engagement,'
        'emails,location,phone&access_token=')
        print("%s/%s%s%s" % (self.graph, page, fields,
            user.fb_accessToken))
        r = requests.get("%s/%s%s%s" % (self.graph, page, fields,
            user.fb_accessToken))
        return None
