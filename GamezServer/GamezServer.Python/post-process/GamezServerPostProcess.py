import sys
import urllib
import urllib2
import re
try:
    nzbName = sys.argv[3]
    regMatch = re.search(r"\[([A-Za-z0-9_]+)\]", nzbName)
    gameId = regMatch.group(1)
    if(gameId == None):
        print('Unable to parse game ID')
        sys.exit(1)
    sourceFolder = sys.argv[1]
    webRequest = urllib2.Request('http://127.0.0.1:8085/PostProcess?gameId=' + str(gameId) + '&processDir=' + urllib.quote_plus(sourceFolder), headers={'User-Agent' : "GamezServer"})
    response = urllib2.urlopen(webRequest)
    responseData = response.read()
    print(responseData)
except Exception,e:
    print("Unable to post process: " + str(e))
    sys.exit(1)