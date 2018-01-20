import os
import cherrypy
from mongoengine import connect
import persistence


class HermitShell(object):

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

            user = persistence.User(
                    name = data['name'],
                    email = data['email'],
                    fb_userId = data['userID'],
                    fb_accessToken = data['accessToken'])
            user.save()
            return {'status': 200, 'statusText': 'OK'}
        except Exception:
            cherrypy.log("[authorize]", traceback=True)
            return {'status': 500, 'statusText': 'Internal server error'}


if __name__ == '__main__':
    config = {
            '/': {'server.socket_host': '0.0.0.0'}
            }
    cherrypy.quickstart(HermitShell(), '/', "app.conf")
