import lxml
import urllib
import xml
from xml import etree
from xml.etree import ElementTree
import GamezServer
from GamezServer.DAO import DAO
from GamezServer.Searchers import Searchers
import urllib2
import os
import sys
import subprocess
import os.path
import json

class Task(object):   
     
    def GetFolders(self,folder=None,upDirectory=None):
        result = ""
        if 'win' in sys.platform:
            if(folder=="/"):
                folder = ""
            print(folder)
            if(len(folder) > 1):
                folder = folder[1:]
                print(folder)
            if(str(upDirectory) == "True"):
                baseFolder = folder
                folder = os.path.dirname(os.path.dirname(folder))
                if(folder == baseFolder):
                    folder = ""
            if(folder==None or folder==""):
                dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
                drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)] 
                for drive in drives:
                    result = result + "/" + drive + "/,"
                if(len(result)>0):
                    result = result[:-1]
            else:
                result = result + "...,"
                for nameVal in [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]:
                    result = result + nameVal + "/,"
                if(len(result)>0):
                    result = result[:-1]
                #print(result)
                #drivelist = subprocess.Popen('wmic logicaldisk get name,description', shell=True, stdout=subprocess.PIPE)
                #drivelisto, err = drivelist.communicate()
                #driveLines = drivelisto.split('\n')
                #print(driveLines)
        else:
            #TODO: Handle Linux: http://stackoverflow.com/questions/5067005/python-udisks-enumerating-device-information/5081937#5081937
             #listdrives=subprocess.Popen('mount', shell=True, stdout=subprocess.PIPE)
             #listdrivesout, err=listdrives.communicate()
             #for idx,drive in enumerate(filter(None,listdrivesout)):
             #    listdrivesout[idx]=drive.split()[2]
             print('Linux not yet implemented')
        return result
    
    def UpdateMasterPlatforms(self):
        dao = DAO()
        dao.LogMessage("Updating Master Platforms", "Info")
        webRequest = urllib.request.Request('http://thegamesdb.net/api/GetPlatformsList.php', headers={'User-Agent' : "Magic Browser"})
        response = urllib2.urlopen(urllib2.urlopen(webRequest))
        platformData = response.read()
        treeData =ElementTree.fromstring(platformData)
        for matchedElement in treeData.findall('./Platforms/Platform'):
            if matchedElement.find('id') != None and matchedElement.find('alias') != None and matchedElement.find('name') != None:
                platformId = matchedElement.find('id').text
                platformName = matchedElement.find('name').text
                platformAlias = matchedElement.find('alias').text
                dao.UpdateMasterPlatform(platformId, platformName, platformAlias)

    def UpdateMasterGames(self):
        try:
            dao = DAO()
            dao.LogMessage("Updating Master Games", "Info")
            platforms = dao.GetMasterPlatforms()
            for platform in platforms:
                platformId = platform[1]
                url = 'http://thegamesdb.net/api/GetPlatformGames.php?platform=' + platformId
                webRequest = urllib2.request.Request(url, headers={'User-Agent' : "Magic Browser"})
                response = urllib2.urlopen(urllib2.urlopen(webRequest))
                gameData = response.read()
                treeData =ElementTree.fromstring(gameData)
                for matchedElement in treeData.findall('./Game'):
                    if matchedElement.find('id') != None and matchedElement.find('GameTitle') != None and matchedElement.find('ReleaseDate') != None:
                        gameId = matchedElement.find('id').text
                        gameTitle = matchedElement.find('GameTitle').text.encode('ascii', 'ignore').decode('ascii')
                        releaseDate = matchedElement.find('ReleaseDate').text
                        dao.UpdateMasterGame(platformId, gameId, gameTitle, releaseDate)
        except:
            e = sys.exc_info()[0]
            dao.LogMessage(e, "Error")

    def WantedGameSearch(self):
        dao = DAO()
        sabnzbdEnabled = dao.GetSiteMasterData("sabnzbdEnabled")
        if(sabnzbdEnabled == "true"):
            sabnzbdApiKey = dao.GetSiteMasterData("sabnzbdApiKey")
            if(sabnzbdApiKey == None):
                dao.LogMessage("No Sabnzbd+ API Key Configured. Unable to continue", "Warning")
            else:
                wantedGames = dao.GetNeededGames()
                searchers = dao.GetSearcherPriority()
                result = ""
                searchers = Searchers()
                for game in wantedGames:
                    for searcher in searchers:
                        searcherInstance = searchers.GetSearcher(searcher[0])
                        if(searcherInstance != None):
                            tmpResult = searcherInstance.search(game[1],game[2],game[0]);
                            if(tmpResult != None):
                                result = result + tmpResult
        else:
            dao.LogMessage("No Downloaders Configured", "Warning")

    def ForceGameSearch(self,gameId, forceNew=False):
        dao = DAO()
        searchNewOnly = dao.GetSiteMasterData("onlySearchNew")
        if(searchNewOnly != None and searchNewOnly == "true"):
            forceNew = True
        sabnzbdEnabled = dao.GetSiteMasterData("sabnzbdEnabled")
        if(sabnzbdEnabled == "true"):
            sabnzbdApiKey = dao.GetSiteMasterData("sabnzbdApiKey")
            if(sabnzbdApiKey == None):
                dao.LogMessage("No Sabnzbd+ API Key Configured. Unable to continue", "Warning")
                return "No Sabnzbd+ API Key Configured. Unable to continue"
            else:
                game = dao.GetWantedGame(gameId)
                searchers = dao.GetSearcherPriority()
                result = ""
                for searcher in searchers:
                    if("Snatched Game" not in result):
                        searchers = Searchers()
                        searcherInstance = searchers.GetSearcher(searcher[0],forceNew)
                        if(searcherInstance != None):
                            tmpResult = searcherInstance.search(game[1],game[2],game[0]);
                            if(tmpResult != None):
                                result = result + tmpResult
                if(result != ""):
                    return result
                else:
                    return "Unable to find game"
        else:
            dao.LogMessage("No Downloaders Configured", "Warning")
            return "No Downloaders Configured"