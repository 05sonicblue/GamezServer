import lxml
import urllib.request
import xml
from xml import etree
from xml.etree import ElementTree
import GamezServer
from GamezServer.DAO import DAO

class Task(object):    
    
    def UpdatePlatforms(self):
        DAO.LogMessage("Updating Master Platforms", "Info")
        webRequest = urllib.request.Request('http://thegamesdb.net/api/GetPlatformsList.php', headers={'User-Agent' : "Magic Browser"})
        with urllib.request.urlopen(webRequest) as response:
            platformData = response.read()
            treeData =ElementTree.fromstring(platformData)
            for matchedElement in treeData.findall('./Platforms/Platform'):
                if matchedElement.find('id') != None and matchedElement.find('alias') != None and matchedElement.find('name') != None:
                    platformId = matchedElement.find('id').text
                    platformName = matchedElement.find('name').text
                    platformAlias = matchedElement.find('alias').text
                    DAO.UpdateMasterPlatform(platformId, platformName, platformAlias)

    def UpdateMasterGames(self):
        DAO.LogMessage("Updating Master Games", "Info")