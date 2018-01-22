import os
import sally.google.spreadsheet as gs
import sally.google.drive as gd
import scrapy
import sendgrid
from sendgrid.helpers.mail import *
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sally.spiders.lightfoot_spider import BasicCrab


def main():
    uploads = gd.get_uploads(os.environ.get('DRIVE_UPLOADS'))
    process = CrawlerProcess(get_project_settings())
    for f in uploads:
        ss = gs.create_spreadsheet(f['name'])
        process.crawl(BasicCrab, csvfile=f['id'],
                spreadsheet=ss['spreadsheetId'])
        # Send email with info about the results
        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('MAIL_FROM'))
        to_email = Email(os.environ.get('MAIL_TO'))
        subject = "[lightfoot] results %s" % f['name']
        content = Content("text/plain", "https://docs.google.com/spreadsheets/d/%s"
                % ss['spreadsheetId'])
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())

    process.start()

if __name__ == '__main__':
    main()

