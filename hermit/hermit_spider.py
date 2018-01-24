import os
import requests
from mongoengine import connect
import model
import sally.google.spreadsheet as gs


class HermitCrab(object):

    def __init__(self, source_file, spreadsheet, *args, **kwargs):
        self.source_urls = source_file
        self.spreadsheetId = spreadsheet

        self.config = gs.get_settings()
        self.score = gs.get_score()

        lines = ["%s" % str(l).rstrip() for l in gs.get_urls(source_file)]


    def extract_data(self, page, token):
        """Extract data from facebook pages"""

        print("%s %s" % (page, token))
        return
