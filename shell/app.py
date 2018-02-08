"""Facebook web shell for hermit."""
import os
import datetime as dt
import logging
import threading
import cherrypy
from cherrypy.lib import cpstats
import requests
from mongoengine import connect
import model
import crabs.google.drive as gd
from crabs import cron

logger = logging.getLogger(__name__)


class HermitShell(object):
    """Facebook web shell for Hermit"""
    def __init__(self):
        self.graph = 'https://graph.facebook.com'

    def get_long_ttl_token(self, accessToken):
        """Exchange short lived Facebook user token for long lived one"""
        request = requests.get(
            "%s/oauth/access_token?grant_type=fb_exchange_token"
            "&client_id=%s&client_secret=%s&fb_exchange_token=%s"
            % (self.graph,
               os.environ.get('FACEBOOK_APP_ID'),
               os.environ.get('FACEBOOK_APP_SECRET'),
               accessToken))
        return request.json()

    @cherrypy.expose
    def index(self):
        """Return landing page"""
        return open(os.path.join(os.path.dirname(__file__), 'index.html'))

    @cherrypy.expose
    def home(self):
        """Return user home"""
        return open(os.path.join(os.path.dirname(__file__), "home.html"))

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def authorize(self):
        """Authorize or register user with Facebook account"""
        data = cherrypy.request.json
        logger.debug(data)
        model.mongo_connect()

        try:
            user = model.User.objects(
                email=data['email'],
                fb_userId=data['fb_userId']).get()
        except:
            user = model.User(
                name=data['name'],
                email=data['email'],
                fb_userId=data['fb_userId'],
                fb_accessToken=data['fb_accessToken'])
            user.save()

        token = self.get_long_ttl_token(user.fb_accessToken)
        user.fb_accessToken = token['access_token']
        user.updated_at=dt.datetime.now()
        user.save()
        return {'status': 200, 'statusText': 'OK'}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def queue(self):
        """Return a list of files in queue"""
        items = gd.get_files(os.environ.get('DRIVE_UPLOADS'))
        return items


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def output(self):
        """Return a list of result files"""
        items = gd.get_files(os.environ.get('DRIVE_RESULTS'))
        return items


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def done(self):
        """return a list of finished files"""
        items = gd.get_files(os.environ.get('DRIVE_DONE'))
        return items

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def processing(self):
        """Return a list of files being processed"""
        items = gd.get_files(os.environ.get('DRIVE_PROC'))
        return items


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        """Force a start of crawlers"""
        thr = threading.Thread(target=cron.main, args=(), kwargs={})
        thr.start()
        return {'status': 200, 'statusText': 'OK'}

if __name__ == '__main__':
    conf = os.path.join(os.path.dirname(__file__), 'app.conf')
    cherrypy.quickstart(HermitShell(), '/', conf)
