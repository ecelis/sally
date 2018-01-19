import cherrypy


class HermitShell(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')

    @cherrypy.expose
    def authorize(self, token=""):
        return "Authorize app %s" % token

if __name__ == '__main__':
    config = {
            '/': {'server.socket_host': '0.0.0.0'}
            }
    cherrypy.quickstart(HermitShell(), '/', "app.conf")
