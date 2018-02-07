import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from crabs.sally.spiders.lightfoot_spider import BasicCrab
from crabs.hermit import hermit_spider
import crabs.google.spreadsheet as gs
import crabs.google.drive as gd


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main():
    uploads = gd.get_uploads(os.environ.get('DRIVE_UPLOADS'))
    process = CrawlerRunner(get_project_settings())
    for source_file in uploads:
        spreadsheet = gs.create_spreadsheet(source_file['name'])
        prefix_ = source_file['name'].split('_')
        if prefix_[0] == 'web':
            process.crawl(BasicCrab, csvfile=source_file['id'],
                    spreadsheet=spreadsheet['spreadsheetId'])
        elif prefix_[0] == 'fb':
            fb = hermit_spider.HermitCrab(source_file['id'], '10156018569427673')

    #process.crawl()


if __name__ == '__main__':
    main()

