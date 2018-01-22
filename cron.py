import os
import sally.google.spreadsheet as gs
import sally.google.drive as gd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sally.spiders.lightfoot_spider import BasicCrab


def main():
    uploads = gd.get_uploads(os.environ.get('DRIVE_UPLOADS'))
    process = CrawlerProcess(get_project_settings())
    for f in uploads:
        process.crawl(BasicCrab, csvfile=f['id'])
    process.start()

if __name__ == '__main__':
    main()

