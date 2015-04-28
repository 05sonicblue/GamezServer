import sqlite3
from sqlite3 import *
import GamezServer
import sys

class DAO(object):
    """description of class"""


    def DBTest(self):
        dbPath = GamezServer.Service.DBPATH
        return

    def UpdateMasterPlatform(self,platformId, platformName, platformUniqueName):
        dbPath = GamezServer.Service.DBPATH
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            sql = "INSERT INTO MasterPlatforms(PlatformID,PlatformName,PlatformUniqueName) SELECT ?,?,? WHERE NOT EXISTS(SELECT 1 FROM MasterPlatforms WHERE PlatformUniqueName = ?)"
            cursor = db.cursor()
            cursor.execute(sql, [platformId, platformName, platformUniqueName, platformUniqueName])
    def GetMasterPlatforms(self):
        dbPath = GamezServer.Service.DBPATH
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("SELECT ID,PlatformID,PlatformName,PlatformUniqueName FROM MasterPlatforms ORDER BY PlatformName")
            return cursor.fetchall()
    def VerifyStructue(self):
        self.LogMessage("Verifying DB Schema", "Info")
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute('pragma user_version')
            version = cursor.fetchone()[0]
            if(version==0):
                self.LogMessage("Building Tables", "Info")
                db.execute("CREATE TABLE IF NOT EXISTS MasterPlatforms (ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,PlatformID TEXT,PlatformName TEXT,PlatformUniqueName TEXT)")
                db.execute("CREATE TABLE IF NOT EXISTS MasterGames (ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,PlatformID TEXT,GameID TEXT,GameTitle TEXT,ReleaseDate TEXT)")
                db.execute("CREATE TABLE IF NOT EXISTS WantedGames (ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,PlatformID TEXT,GameID TEXT,STATUS TEXT)")
                db.execute("CREATE TABLE IF NOT EXISTS Log (ID INTEGER PRIMARY KEY AUTOINCREMENT,Level TEXT,Message TEXT,MessageDateTime TEXT)")
                db.execute("CREATE TABLE IF NOT EXISTS SiteMasterData (ID INTEGER PRIMARY KEY AUTOINCREMENT,Type TEXT,Content TEXT)")
                db.execute("CREATE TABLE IF NOT EXISTS SearcherPriority (ID INTEGER PRIMARY KEY AUTOINCREMENT,Searcher TEXT,SortOrder INTEGER)")
                db.execute("CREATE TABLE IF NOT EXISTS SearcherHistory (ID INTEGER PRIMARY KEY AUTOINCREMENT,Searcher TEXT,SearcherID TEXT)")
                db.execute("INSERT INTO SiteMasterData (Type,Content) SELECT 'HeaderContents','' WHERE NOT EXISTS(SELECT 1 FROM SiteMasterData WHERE Type='HeaderContents')")
                db.execute("INSERT INTO SiteMasterData (Type,Content) SELECT 'currentVersion','0.0.1' WHERE NOT EXISTS(SELECT 1 FROM SiteMasterData WHERE Type='currentVersion')")
                cursor.execute('pragma user_version=1')
            return;

    def LogMessage(self,message, level):
        print(level + " - " + message)
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Log(Message,Level,MessageDateTime) SELECT ?,?,datetime()", [message, level])
    
    def GetLogMessages(self,level=None):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            sql = 'SELECT Level,Message,MessageDateTime FROM Log'
            if(level != None):
                sql = sql + " WHERE Level='" + level + "'"
            cursor.execute(sql)
            results = cursor.fetchall()
            return results

    def AddSnatchedHistory(self,searcher, searcherId):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO SearcherHistory(Searcher,SearcherID) SELECT ?,? WHERE NOT EXISTS(SELECT 1 FROM SearcherHistory WHERE Searcher=? and SearcherID=?)", [searcher, searcherId, searcher, searcherId])

    def GetSnatchHistory(self,searcher, searcherId):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("SELECT Searcher,SearcherID FROM SearcherHistory SearcherHistory WHERE Searcher=? and SearcherID=?)", [searcher, searcherId])
            return cursor.fetchone()
    def DeleteLogs(self):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Log")

    def GetSiteMasterData(self,key):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            sql = "SELECT Content FROM SiteMasterData WHERE Type='" + key + "'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if(result != None):
                if(result[0] == None):
                    return ""
                else:
                    return result[0]
            else:
                return ""
    def UpdateMasterSiteData(self,type, content):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO SiteMasterData(Type,Content) SELECT ?,? WHERE NOT EXISTS(SELECT 1 FROM SiteMasterData WHERE Type=?)", [type,content,type])
            cursor.execute("UPDATE SiteMasterData SET Content=? WHERE Type=?", [content,type])
    
    def UpdateMasterGame(self,platformId, gameId, gameTitle, releaseDate):
        dbPath = GamezServer.Service.DBPATH
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            sql = "INSERT INTO MasterGames(PlatformID,GameID,GameTitle,ReleaseDate) SELECT ?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM MasterGames WHERE GameID = ?)"
            cursor = db.cursor()
            cursor.execute(sql, [platformId, gameId, gameTitle, releaseDate, gameId])

    def GetMasterGames(self,platformId):
        dbPath = GamezServer.Service.DBPATH
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("SELECT PlatformID,GameID,GameTitle,ReleaseDate FROM MasterGames WHERE PlatformID=" + platformId + " ORDER BY GameTitle")
            return cursor.fetchall()

    def AddWantedGame(self,platformId,gameId, status):
        dbPath = GamezServer.Service.DBPATH
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            sql = "INSERT INTO WantedGames(PlatformID,GameID,Status) SELECT ?,?,? WHERE NOT EXISTS(SELECT 1 FROM WantedGames WHERE GameID = ? and PlatformID = ?)"
            cursor = db.cursor()
            cursor.execute(sql, [platformId, gameId, status, gameId, platformId])
        return

    def SetSearcherPriority(self,priorities):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM SearcherPriority")
            counter = 0
            for priority in priorities.split(","):
                cursor.execute("INSERT INTO SearcherPriority(Searcher,SortOrder) SELECT ?,?", [priority,counter])
                counter = counter + 1

    def GetWantedGames(self):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("SELECT MasterPlatforms.PlatformName,MasterGames.GameTitle,MasterGames.ReleaseDate,WantedGames.STATUS,WantedGames.ID FROM WantedGames inner join MasterPlatforms on (MasterPlatforms.PlatformID=WantedGames.PlatformID) inner join MasterGames on (MasterGames.GameID=WantedGames.gameID and MasterGames.PlatformID=MasterPlatforms.platformID)")
            return cursor.fetchall()

    def GetNeededGames(self):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("SELECT WantedGames.ID,MasterPlatforms.PlatformName,MasterGames.GameTitle,MasterGames.ReleaseDate,WantedGames.STATUS FROM WantedGames inner join MasterPlatforms on (MasterPlatforms.PlatformID=WantedGames.PlatformID) inner join MasterGames on (MasterGames.GameID=WantedGames.gameID and MasterGames.PlatformID=MasterPlatforms.platformID) WHERE WantedGames.Status='Wanted'")
            return cursor.fetchall()

    def GetWantedGame(self,gameId):
        print gameId
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("SELECT WantedGames.ID,MasterPlatforms.PlatformName,MasterGames.GameTitle,MasterGames.ReleaseDate,WantedGames.STATUS FROM WantedGames inner join MasterPlatforms on (MasterPlatforms.PlatformID=WantedGames.PlatformID) inner join MasterGames on (MasterGames.GameID=WantedGames.gameID and MasterGames.PlatformID=MasterPlatforms.platformID) WHERE WantedGames.ID=?", [gameId])
            return cursor.fetchone()

    def GetSearcherPriority(self):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            cursor = db.cursor()
            cursor.execute("select Replace(Searcher,'Priority','') from SiteMasterData inner join searcherPriority on (replace(type,'Enabled','')=replace(Searcher,'Priority','')) order by SortOrder asc")
            return cursor.fetchall()

    def UpdateWantedGameStatus(self,gameId, status):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            sql = "UPDATE WantedGames SET Status=? WHERE ID=?"
            cursor = db.cursor()
            cursor.execute(sql, [status, gameId])
        return

    def DeleteWantedGame(self,gameId):
        with sqlite3.connect(GamezServer.Service.DBPATH) as db:
            sql = "DELETE FROM WantedGames WHERE ID=?"
            cursor = db.cursor()
            cursor.execute(sql, [gameId])
        return