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
import shutil

class Task(object):   

    def PostProcess(self,folder,gameId):

        result = ""
        limitExtensions = ""
        dao = DAO()
        game = dao.GetWantedGame(gameId)
        genericProcessing = True
        result = result + 'Processing folder: ' + folder + '\n'
        platformName = game[1]
        gameTitle = game[2]
        result = result + 'Processing Game: ' + gameTitle + '\n'
        destFolderRoot = dao.GetSiteMasterData("destinationFolder")
        if 'win' in sys.platform:
            destFolderRoot = destFolderRoot[1:]
        if(destFolderRoot == None or destFolderRoot == ""):
            return "Destination Folder Missing"
        destFolderPlatform = os.path.join(destFolderRoot, platformName)
        destFolderGame = os.path.join(destFolderPlatform, gameTitle.replace(":", ""))
        if not os.path.exists(destFolderGame):
            result = result + 'Creating Game Folder\n'
            os.makedirs(destFolderGame)

        if(platformName == "Microsoft Xbox 360"):
            failedFile = False
            abgxEnabled = dao.GetSiteMasterData("abgx360Enabled")
            abgxPath = dao.GetSiteMasterData("abgx360Path")
            abgxRegion = dao.GetSiteMasterData("abgx360Region")
            xbox360Extensions = dao.GetSiteMasterData("xbox360Extensions")
            limitExtensions = xbox360Extensions
            if(abgxEnabled and abgxPath != None):
                if(os.path.exists(folder)):
                   for file in os.listdir(folder):
                       fileToProcess = os.path.join(folder, file)
                       if(os.path.isfile(fileToProcess)):
                           validFile = False
                           if(limitExtensions != ""):
                               for extension in limitExtensions.split(','):
                                   if(fileToProcess.endswith(extension)):
                                      validFile = True
                           else:
                                validFile = True
                           if(validFile):
                               #Run abgx against file
                                regionFree = False
                                command = abgxPath + ' --noverify --noupdate --stayoffline --nowrite --noautofix --norebuild --nofixdrt --nofixdev --noverbose "' + fileToProcess + '"'
                                p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                                lines = p.stdout.readlines()
                                for line in lines:
                                    if(line.startswith("Game Name:")):
                                        gameName = line.replace("Game Name: ", "").lstrip().rstrip()
                                    if(line.startswith("SS looks valid")):
                                        validSs = True
                                    if(line.startswith("DMI looks valid")):
                                        validDmi = True
                                    if(line.startswith("Region Code:")):
                                        regionCode = line.replace("Region Code: ", "").lstrip().rstrip().replace("0x", "")
                                    if(line.lstrip().startswith("Region Free")):
                                        regionFree = True
                                processFile = False
                                if(regionFree == False):
                                    if(abgxRegion == ""):
                                        processFile = True
                                    else:
                                        if(abgxRegion == regionCode):
                                            processFile = True
                                else:
                                    processFile = True
                                if(processFile and gameName != "" and validSs and validDmi):
                                    result = result + 'Copying file: ' + file + '\n'
                                    extension = os.path.splitext(fileToProcess)[len(os.path.splitext(fileToProcess))-1]
                                    finalFileName = os.path.join(destFolderGame,gameName + extension)
                                    buffer_size = 1024
                                    with open(fileToProcess, 'rb') as fsrc:
                                        with open(finalFileName, 'wb') as fdest:
                                              shutil.copyfileobj(fsrc, fdest, buffer_size) 
                                else:
                                    failedFile = True
                                    result = result + 'Unable to verify. Skipping file: ' + file + '\n'
                genericProcessing = False

        if(genericProcessing):
            result = result + "No specific processing defined. Just copying files\n"
            if(os.path.exists(folder)):
               for file in os.listdir(folder):
                   fileToProcess = os.path.join(folder, file)
                   if(os.path.isfile(fileToProcess)):
                       validFile = False
                       if(limitExtensions != ""):
                           for extension in limitExtensions.split(','):
                               if(fileToProcess.endswith(extension)):
                                  validFile = True
                       else:
                            validFile = True
                       if(validFile):
                           result = result + 'Copying file: ' + file + '\n'
                           shutil.copy2(fileToProcess, destFolderGame)
        if(failedFile):
            result = result + "Unable to completely process game: " + gameTitle
        else:
            dao.UpdateWantedGameStatus(gameId, "Downloaded")
            if(os.path.exists(folder)):
               shutil.rmtree(folder)
            result = result + "Processed " + gameTitle + " Succesfully"
        return result

    def Abgx360(self,folder):
        dao = DAO()
        abgxEnabled = dao.GetSiteMasterData("abgx360Enabled")
        abgxPath = dao.GetSiteMasterData("abgx360Path")
        abgxRegion = dao.GetSiteMasterData("abgx360Region")
        if(enabled == "true"):
            print ''
        else:
            return True
     
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