from GamezServer import WebServe, Task
import cherrypy
import os
from cherrypy.process.plugins import Monitor
import webbrowser
import GamezServer
from GamezServer.DAO import DAO
DBPATH=""
class Service(object):
    def Start(configPath):
        rootPath = os.path.dirname(configPath)
        GamezServer.Service.DBPATH = os.path.join(rootPath, "GamezServer.db")
        print(GamezServer.Service.DBPATH)
        GamezServer.DAO.DAO.VerifyStructue()

        staticContentPath = os.path.join(rootPath, os.path.join("GamezServer","static-web"))
        appConfig = {'/static': {'tools.staticdir.on': True, 'tools.staticdir.dir': staticContentPath}}
        cherrypy.config.update(configPath)
        cherrypy.tree.mount(WebServe.WebServe(), '/', appConfig)
        DAO.LogMessage("Registering Background Processes", "Info")
        Monitor(cherrypy.engine, GamezServer.Task.Task().UpdatePlatforms, frequency=86400).subscribe()
        DAO.LogMessage("Starting Service", "Info")
        cherrypy.engine.start()
        webbrowser.open("http://127.0.0.1:8085")
        cherrypy.engine.block()
        