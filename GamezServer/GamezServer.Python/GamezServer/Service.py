from GamezServer import WebServe, Task
import cherrypy
import os
from cherrypy.process.plugins import Monitor
import webbrowser
import GamezServer
from GamezServer.DAO import DAO
from GamezServer.Task import Task
DBPATH=""
class Service(object):
    def Start(self,configPath):
        rootPath = os.path.dirname(configPath)
        GamezServer.Service.DBPATH = os.path.join(rootPath, "GamezServer.db")
        
        dao = DAO()
        dao.VerifyStructue()

        staticContentPath = os.path.join(rootPath, os.path.join("GamezServer","static-web"))
        appConfig = {'/static': {'tools.staticdir.on': True, 'tools.staticdir.dir': staticContentPath}}
        cherrypy.config.update(configPath)
        cherrypy.tree.mount(WebServe.WebServe(), '/', appConfig)
        
        dao.LogMessage("Registering Background Processes", "Info")
        Monitor(cherrypy.engine, GamezServer.Task.Task().UpdateMasterPlatforms, frequency=86400).subscribe()
        Monitor(cherrypy.engine, GamezServer.Task.Task().UpdateMasterGames, frequency=86400).subscribe()
        Monitor(cherrypy.engine, GamezServer.Task.Task().WantedGameSearch, frequency=86400).subscribe()
        dao.LogMessage("Starting Service", "Info")
        cherrypy.engine.start()
        webbrowser.open("http://" + cherrypy.server.socket_host + ":" + str(cherrypy.server.socket_port))
        cherrypy.engine.block()
        
        