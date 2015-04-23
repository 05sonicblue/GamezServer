import sqlite3
from sqlite3 import *
import GamezServer

class DAO(object):
    """description of class"""


    def DBTest(self):
        dbPath = GamezServer.Service.DBPATH
        return

    def UpdateMasterPlatform(platformId, platformName, platformUniqueName):
        dbPath = GamezServer.Service.DBPATH
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            sql = "INSERT INTO MasterPlatforms(PlatformID,PlatformName,PlatformUniqueName) SELECT ?,?,? WHERE NOT EXISTS(SELECT 1 FROM MasterPlatforms WHERE PlatformUniqueName = ?)"
            cursor = db.cursor()
            cursor.execute(sql, [platformId, platformName, platformUniqueName, platformUniqueName])

    def VerifyStructue():
        DAO.LogMessage("Verifying DB Schema", "Info")
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute('pragma user_version')
            version = cursor.fetchone()[0]
            if(version==0):
                DAO.LogMessage("Building Tables", "Info")
                db.execute("CREATE TABLE IF NOT EXISTS MasterPlatforms (ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,PlatformID TEXT,PlatformName TEXT,PlatformUniqueName TEXT)")
                db.execute("CREATE TABLE IF NOT EXISTS Log (ID INTEGER PRIMARY KEY AUTOINCREMENT,Level TEXT,Message TEXT,MessageDateTime TEXT)")
                cursor.execute('pragma user_version=0')
            return;

    def LogMessage(message, level):
        print(level + " - " + message)
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Log(Message,Level,MessageDateTime) SELECT ?,?,datetime()", [message, level])
    def GetLogMessages(level=None):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            sql = 'SELECT Level,Message,MessageDateTime FROM Log'
            if(level != None):
                sql = sql + " WHERE Level='" + level + "'"
            cursor.execute(sql)
            results = cursor.fetchall()
            print(results)
            return results