import GamezServer
import urllib
import urllib2
from GamezServer.UsenetCrawler import UsenetCrawler
from GamezServer.DAO import DAO
class Searchers(object):
    """description of class"""
    

    def GetSearcher(self,searcherName,forceNew):
        if(searcherName == "usenetCrawler"):
            return UsenetCrawler(forceNew)
        return None

    def SendToSab(self,sabnzbdBaseUrl,sabnzbdApiKey,nzbLink,nzbTitle, wantedGameId):
        dao = DAO()
        nzbTitle = "[" + str(wantedGameId) + "] - " + nzbTitle
        category = dao.GetSiteMasterData('sabnzbdCategory')
        sabUrl = sabnzbdBaseUrl
        if(sabUrl.endswith('/') == False):
            sabUrl = sabUrl + "/"
        sabUrl = sabUrl + "sabnzbd/api"
        sabUrl = sabUrl + "?apikey=" + sabnzbdApiKey
        sabUrl = sabUrl + "&mode=addurl&name=" + urllib.quote_plus(nzbLink)
        sabUrl = sabUrl + "&nzbname=" + urllib.quote_plus(nzbTitle)
        if(category != None and category != ""):
            sabUrl = sabUrl + "&cat=" + category
        sabRequest = urllib2.Request(sabUrl, headers={'User-Agent' : "GamezServer"})
        response = urllib2.urlopen(sabRequest)
        sabRespData = response.read()
        return sabRespData
