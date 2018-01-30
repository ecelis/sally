import os
import logging
import sally.google.spreadsheet as gs
import sally.google.drive as gd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sally.spiders.lightfoot_spider import BasicCrab
from hermit import hermit_spider

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main():
    uploads = gd.get_uploads(os.environ.get('DRIVE_UPLOADS'))
    logger.debug(uploads)
    process = CrawlerProcess(get_project_settings())
    for source_file in uploads:
        spreadsheet = gs.create_spreadsheet(source_file['name'])
        prefix_ = source_file['name'].split('_')
        if prefix_[0] == 'web':
            process.crawl(BasicCrab, csvfile=source_file['id'],
                    spreadsheet=spreadsheet['spreadsheetId'])
        elif prefix_[0] == 'fb':
            fb = hermit_spider.HermitCrab(source_file['id'], '10156018569427673')

    process.start()


if __name__ == '__main__':
    main()

