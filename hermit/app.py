import cherrypy
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

        user = persistence.User(email='algo@mail.com',
                fb_userId=date['userID'],
                fb_accessToken=data['accessToken'])
        return "Authorize app %s" % data

if __name__ == '__main__':
    config = {
            '/': {'server.socket_host': '0.0.0.0'}
            }
    cherrypy.quickstart(HermitShell(), '/', "app.conf")
