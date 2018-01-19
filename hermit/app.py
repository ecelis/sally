import cherrypy
import hermit.persistence as persist


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
        cherrypy.log(str(persist))
        return "Authorize app %s" % data

if __name__ == '__main__':
    config = {
            '/': {'server.socket_host': '0.0.0.0'}
            }
    cherrypy.quickstart(HermitShell(), '/', "app.conf")
