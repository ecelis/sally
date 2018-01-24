import os
import sys
import cherrypy
import requests
from mongoengine import connect
import model
from google import spreadsheet as gs


class HermitShell(object):

    def __init__(self):
        self.graph = 'https://graph.facebook.com'


    def get_long_ttl_token(self, accessToken):
        r = requests.get("%s/oauth/access_token?grant_type=fb_exchange_token"
                "&client_id=%s&client_secret=%s&fb_exchange_token=%s"
                % (self.graph,
                    os.environ.get('FACEBOOK_APP_ID'),
                    os.environ.get('FACEBOOK_APP_SECRET'),
                    accessToken))
        return r.json()


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def page(self, page, fb_user_id):

        data = cherrypy.request
        fields = str('?fields=about,category,contact_address,engagement,'
        'emails,location,phone&access_token=')

        try:
            connect(os.environ.get('MONGO_DBNAME'),
                    host="mongodb://" + os.environ.get('MONGO_HOST'),
                    port=int(os.environ.get('MONGO_PORT')),
                    replicaset=os.environ.get('MONGO_REPLICA_SET'),
                username=os.environ.get('MONGO_USER'),
                password=os.environ.get('MONGO_PASSWORD'))
        except Exception:
            cherrypy.error("[page] Can't connect to MongoDB", traceback=True)
            return {'status': 500, 'statusText': "Can't connect to MongoDB"}

        try:
            user = model.User.objects(fb_userId=fb_user_id).get()
        except:
            cherrypy.error("[page] Can't get Facebook user token", traceback=True)
            return {'status': 500, 'statusText': "Can't get Facebook user token"}
        print("%s/%s%s%s" % (self.graph, page, fields,
            user.fb_accessToken))
        r = requests.get("%s/%s%s%s" % (self.graph, page, fields,
            user.fb_accessToken))
        cherrypy.log(r.text)
        cherrypy.log('===')
        print(r.json())
        return {'status': 200, 'statusText': 'algo'}


    @cherrypy.expose
    def index(self):
        return open('index.html')


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def authorize(self):
        data = cherrypy.request.json
        try:
            connect(os.environ.get('MONGO_DBNAME'),
                    host="mongodb://" + os.environ.get('MONGO_HOST'),
                    port=int(os.environ.get('MONGO_PORT')),
                    replicaset=os.environ.get('MONGO_REPLICA_SET'),
                username=os.environ.get('MONGO_USER'),
                password=os.environ.get('MONGO_PASSWORD'))
        except Exception:
            cherrypy.log("[authorize]", traceback=True)
            return {'status': 500, 'statusText': 'Can\'t connect to MongoDB'}


        try:
            user = model.User.objects(email=data['email'], fb_userId=data['fb_userId']).get()
        except:
            user = model.User(
                    name = data['name'],
                    email = data['email'],
                    fb_userId = data['fb_userId'],
                    fb_accessToken = data['fb_accessToken'])
            user.save()

        token = self.get_long_ttl_token(user.fb_accessToken)
        user.fb_accessToken = token['access_token']
        user.save()
        return {'status': 200, 'statusText': 'OK'}


if __name__ == '__main__':
    config = {
            '/': {'server.socket_host': '0.0.0.0'}
            }
    cherrypy.quickstart(HermitShell(), '/', "app.conf")
