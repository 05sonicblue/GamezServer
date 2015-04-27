#import cherrypy
from GamezServer.Service import Service
import os
import sys


if __name__ == '__main__':
    iniPath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"GamezServer.ini")
    service = Service()
    service.Start(iniPath)