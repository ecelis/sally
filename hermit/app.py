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
    def authorize(self):
        data = cherrypy.request.json
        # TODO persist data['accessToken']
        # data['userID']
        connect(os.environ.get('MONGO_DBNAME'),
                host=os.environ.get('MONGO_HOST'),
                port=int(os.environ.get('MONGO_PORT')),
                replicaset=os.environ.get('MONGO_REPLICA_SET'),
            username=os.environ.get('MONGO_USER'),
            password=os.environ.get('MONGO_PASSWORD'))

        user = persistence.User(email = 'algo@mail.com',
                fb_userId = data['userID'],
                fb_accessToken = data['accessToken'])
        user.save()
        return user


if __name__ == '__main__':
    config = {
            '/': {'server.socket_host': '0.0.0.0'}
            }
    cherrypy.quickstart(HermitShell(), '/', "app.conf")
