import os
import shutil
import cherrypy
import GamezServer
import sys
from GamezServer.DAO import DAO
from GamezServer.Task import Task
import urllib2
import json
import urllib
from distutils import version
from distutils.version import StrictVersion
import tarfile
import subprocess
class WebServe(object):
    """description of class"""

    @cherrypy.expose
    def upgradeGamezServer(self, downloadUrl, newVersion):
        appPath = GamezServer.Service.APPPATH
        filesToIgnore = ["GamezServer.ini","GamezServer.db"]
        filesToIgnoreSet = set(filesToIgnore)
        updatePath = os.path.join(appPath,"update")
        if not os.path.exists(updatePath):     
            os.makedirs(updatePath)
        data = urllib2.urlopen(downloadUrl)
        downloadPath = os.path.join(appPath,data.geturl().split('/')[-1])
        downloadedFile = open(downloadPath,'wb')
        downloadedFile.write(data.read())
        downloadedFile.close()
        tarredFile = tarfile.open(downloadPath)
        tarredFile.extractall(updatePath)
        tarredFile.close()
        os.remove(downloadPath)
        contentsDir = [x for x in os.listdir(updatePath) if os.path.isdir(os.path.join(updatePath, x))]
        updatedFilesPath = os.path.join(updatePath,contentsDir[0])
        for dirname, dirnames, filenames in os.walk(updatedFilesPath):
            dirname = dirname[len(updatedFilesPath)+1:]
            for file in filenames:
                src = os.path.join(updatedFilesPath,dirname,file)
                dest = os.path.join(appPath,dirname,file)
                if((file in filesToIgnoreSet) == True):
                    continue
                if(os.path.isfile(dest)):
                    os.remove(dest)
                os.renames(src,dest)
        shutil.rmtree(updatePath)
        dao = DAO()
        dao.UpdateMasterSiteData("currentVersion",newVersion)
        dao.UpdateMasterSiteData("HeaderContents", """ 
                    <script src="/static/scripts/jquery.js"></script>
            <script src="/static/scripts/jquery-ui.js"></script>
            <script src="/static/scripts/Menu.js"></script>
            <script src="/static/scripts/jquery.dataTables.js"></script>
            <script src="/static/scripts/dataTables.jqueryui.js"></script>
            <script src="/static/scripts/dataTables.tableTools.js"></script>
            <script src="/static/scripts/chosen.jquery.js"></script>
            <script src="/static/scripts/toastr.js"></script>

            <link href="/static/styles/jquery-ui.css" rel="stylesheet" />
            <link href="/static/styles/Menu.css" rel="stylesheet" />
            <link href="/static/styles/dataTables.jqueryui.css" rel="stylesheet" />
            <link href="/static/styles/dataTables.tableTools.css" rel="stylesheet" />
            <link href="/static/styles/chosen.css" rel="stylesheet" />
            <link href="/static/styles/toastr.css" rel="stylesheet" />
            <div id='cssmenu'>
                <ul>
                    <li class='active align-center'>
                        <a href='/'><span>Home</span></a>
                        <ul>
                            <li><a href='/AddGame'><span>Add Game</span></a></li>
                            <li><a href='/AddByPlatform'><span>Add by Platform</span></a></li>
                        </ul>
                    </li>
                    <li class='active align-center'>
                        <a href='/Manage'><span>Manage</span></a>
                    </li>
                    <li class='active has-sub'><a href='/Settings'><span>Settings</span></a>
                        <ul>
                            <li><a href='/Settings#gamezserver-tab'><span>Gamez Server</span></a></li>
                            <li><a href='/Settings#downloaders-tab'><span>Downloaders</span></a></li>
                            <li><a href='/Settings#searchers-tab'><span>Searchers</span></a></li>
                            <li><a href='/Settings#postprocess-tab'><span>Post Process</span></a></li>
                        </ul>
                    </li>
                    <li class='active align-center'>
                        <a href='/Log'><span>Log</span></a>
                    </li>
                    <div style="float:right;padding: 15px 20px;color: #7a8189;">v.0.0.1</div>
                </ul>
            </div>
        """)
        result = "Gamez Server updated to V." + newVersion
        raise cherrypy.HTTPRedirect("/?statusMessage=" + result)

    @cherrypy.expose
    def checkForVersion(self):
        dao = DAO()
        currentVersion = dao.GetSiteMasterData("currentVersion")
        if(currentVersion == None or currentVersion == ""):
            currentVersion = '0.0.0'
        webRequest = urllib2.Request('https://api.github.com/repos/mdlesk/GamezServer/releases', headers={'User-Agent' : "Magic Browser", "Accept" : "application/vnd.github.v3+json"})
        response = urllib2.urlopen(webRequest)
        githubReleaseData = response.read()
        jsonReleaseData = json.loads(githubReleaseData)
        highestVersion = currentVersion
        upgradeVersionDescription = ""
        upgradeVersionUrl = ""
        for jsonRelease in jsonReleaseData:
            releaseVersion = jsonRelease['tag_name']
            if(StrictVersion(releaseVersion) > StrictVersion(highestVersion)):
               highestVersion = releaseVersion
               upgradeVersionUrl = jsonRelease['tarball_url']
               upgradeVersionDescription = jsonRelease['body']
        if(StrictVersion(highestVersion) > StrictVersion(currentVersion) and upgradeVersionUrl != ""):
            return "GamezServer v." + highestVersion + " is available. Release Notes: " + upgradeVersionDescription + ". Click <a href='/upgradeGamezServer?downloadUrl=" + urllib.quote_plus(upgradeVersionUrl) + "&newVersion=" + highestVersion  + "'>Here</a> to upgrade"
        return ""

    @cherrypy.expose
    def Manage(self):
        content = ""
        dao = DAO()
        snatchedGames = dao.GetWantedGamesByStatus("Snatched")
        downloadedGames = dao.GetWantedGamesByStatus("Downloaded")
        wantedGames = dao.GetWantedGamesByStatus("Wanted")
        currentVersion = dao.GetSiteMasterData("currentVersion")
        currentHeaderContent = dao.GetSiteMasterData("HeaderContents")
        currentFooterContent = dao.GetSiteMasterData("FooterContents")
        content = content + currentHeaderContent.format(currentVersion)
        content = content + """
            <div id="manageTabs"  style="height:500">
              <ul>
                <li><a href="#status-tab">Snatched Games</a></li>
              </ul>
              <div id="status-tab">                
                <table align="left" valign="top" style="height:325px">
                    <thead>
                        <th>Downloaded</th>
                        <th>Snatched</th>
                        <th>Wanted</th>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <ul id="downloadedList" style="overflow-y:scroll;border: 1px solid black;width: 300px;min-height: 300px;max-height:300px;list-style-type: none;margin: 0;padding: 5px 0 0 0;float: left;margin-right: 10px;" class="connectedSortable">
                                """
        for downloadedGame in downloadedGames:
            content = content + '<li style="margin: 0 5px 5px 5px;padding: 5px;font-size: 1.2em;width: 300px;" class="ui-state-default" value="' + str(downloadedGame[4]) + '">' + str(downloadedGame[1]) + '</li>'
        content = content + """
                                  
                                </ul>
                            </td>
                            <td>
                                <ul id="snatchedList" style="overflow-y:scroll;border: 1px solid black;width: 300px;min-height: 300px;max-height:300px;list-style-type: none;margin: 0;padding: 5px 0 0 0;float: left;margin-right: 10px;" class="connectedSortable">
                                """
        for snatchedGame in snatchedGames:
            content = content + '<li style="margin: 0 5px 5px 5px;padding: 5px;font-size: 1.2em;width: 300px;" class="ui-state-default" value="' + str(snatchedGame[4]) + '">' + str(snatchedGame[1]) + '</li>'
        content = content + """
                                </ul>
                            </td>
                            <td>
                                <ul id="wantedList" style="overflow-y:scroll;border: 1px solid black;width: 300px;min-height: 300px;max-height:300px;list-style-type: none;margin: 0;padding: 5px 0 0 0;float: left;margin-right: 10px;" class="connectedSortable">
                                """
        for wantedGame in wantedGames:
            content = content + '<li style="margin: 0 5px 5px 5px;padding: 5px;font-size: 1.2em;width: 300px;" class="ui-state-default" value="' + str(wantedGame[4]) + '">' + str(wantedGame[1]) + '</li>'
        content = content + """
                                </ul>
                            </td>
                        </tr>
                    </tbody>
                </table>
              </div>
            </div>
            <script>
                $(document).ready(function(){
                    
                    $("#downloadedList").sortable({
    		            connectWith: ['.connectedSortable'],
                        receive: function( event, ui ) {
                            status = 'Downloaded';
                            gameId = ui.item.val();
                            $.ajax({
                                type: "GET",
                                url: '/UpdateStatus?status=' + status + '&gameId=' + gameId,
                                success: function (data) {
                                    if(data != "")
                                    {
                                        toastr.info(data);
                                    }
                                }
                            });
                        }
    	            });
                    $("#snatchedList").sortable({
    		            connectWith: ['.connectedSortable'],
                        receive: function( event, ui ) {
                            status = 'Snatched';
                            gameId = ui.item.val();
                            $.ajax({
                                type: "GET",
                                url: '/UpdateStatus?status=' + status + '&gameId=' + gameId,
                                success: function (data) {
                                    if(data != "")
                                    {
                                        toastr.info(data);
                                    }
                                }
                            });
                        }
    	            });
                    $("#wantedList").sortable({
    		            connectWith: ['.connectedSortable'],
                        receive: function( event, ui ) {
                            status = 'Wanted'
                            gameId = ui.item.val();
                            $.ajax({
                                type: "GET",
                                url: '/UpdateStatus?status=' + status + '&gameId=' + gameId,
                                success: function (data) {
                                    if(data != "")
                                    {
                                        toastr.info(data);
                                    }
                                }
                            });
                        }
    	            });
                    $("#manageTabs").tabs();
                });
            </script>
        """
        content = content + currentFooterContent
        return content

    @cherrypy.expose
    def index(self,statusMessage=None,addedGameId=None):
        dao = DAO()
        wantedGames = dao.GetWantedGames()
        currentHeaderContent = dao.GetSiteMasterData("HeaderContents")
        currentFooterContent = dao.GetSiteMasterData("FooterContents")
        currentVersion = dao.GetSiteMasterData("currentVersion")
        content = ""
        content = content + currentHeaderContent.format(currentVersion)
        if(statusMessage != None):
            content = content + "<script>$(document).ready(function () {toastr.info('" + statusMessage + "');});</script>"
        content = content + """
            <br />     
            <table id="wantedGamesTable" class="display" cellspacing="0" width="100%"><thead><tr><th>Platform</th><th>Game</th><th>Release Date</th><th>Status</th><th>Actions</th></tr></thead><tfoot><tr><th>Platform</th><th>Game</th><th>Release Date</th><th>Status</th><th>Actions</th></tr></tfoot></td></tr>
        """
        content = content + "<tbody>"
        for game in wantedGames:
            optionList = ""
            if(game[3] == 'Wanted'):
                optionList = optionList + '<option selected>Wanted</option>'
            else:
                optionList = optionList + '<option>Wanted</option>'
            if(game[3] == 'Snatched'):
                optionList = optionList + '<option selected>Snatched</option>'
            else:
                optionList = optionList + '<option>Snatched</option>'
            if(game[3] == 'Downloaded'):
                optionList = optionList + '<option selected>Downloaded</option>'
            else:
                optionList = optionList + '<option>Ignored</option>'
            rowContent = "<tr><td>" + game[0] + "</td><td>" + game[1] + "</td><td>" + game[2] + """</td><td><select onchange="statusUrl='/UpdateStatus?status=' + $(this).val() + '&gameId=""" + str(game[4]) + """';$.ajax({type: 'GET',url: statusUrl,success: function (data) {toastr.info(data);},error: function (xhr, ajaxOptions, thrownError) {toastr.info('Unable to update: ' + thrownError);}});">""" + optionList + "</select></td><td><a href='/DeleteGame?gameId=" + str(game[4]) + "'>Delete</a>&nbsp;|&nbsp;<a href='/ForceSearch?gameId=" + str(game[4]) + """' onclick="forceSearchUrl = '/ForceSearch?gameId=""" + str(game[4]) + """';$.ajax({type: 'GET',url: forceSearchUrl,success: function (data) {toastr.info(data);},error: function (xhr, ajaxOptions, thrownError) {toastr.info('Unable to force search: ' + thrownError);}});return false;">Force Search</a>&nbsp;|&nbsp;<a href='/ForceSearch?gameId=""" + str(game[4]) + """' onclick="forceSearchNewUrl = '/ForceSearchNew?gameId=""" + str(game[4]) + """';$.ajax({type: 'GET',url: forceSearchNewUrl,success: function (data) {toastr.info(data);},error: function (xhr, ajaxOptions, thrownError) {toastr.info('Unable to force search: ' + thrownError);}});return false;">Force Search New</a></td></tr>"""
            content = content + rowContent
        content = content + "</tbody>"
        content = content + """
            </table>
            <br />
            """
        content = content + currentFooterContent.format(currentVersion)
        content = content + """
            <script>
                $(document).ready(function () {
                    $('#wantedGamesTable').dataTable({
                        "pagingType": "full_numbers"
                    });
                    $.ajax({
                        type: "GET",
                        url: '/checkForVersion',
                        success: function (data) {
                            if(data != "")
                            {
                                toastr.info(data);
                            }
                        }
                    });
        """
        if(addedGameId != None):
            for item in str(addedGameId).split(','):
                addedGame = dao.GetWantedGame(item)
                if(addedGame != None):
                    content = content + """
                            toastr.info('Searching for game """ + str(addedGame[2]).replace("'", "\\'") + """');
                            forceSearchUrl = '/ForceSearch?gameId=""" + str(addedGame[0]) + """';
                            $.ajax({
                                type: 'GET',
                                url: forceSearchUrl,
                                success: function (data) {
                                    toastr.info(data);
                                },
                                error: function (xhr, ajaxOptions, thrownError) {
                                    toastr.info('Unable to force search: ' + thrownError);
                                }
                            });
                    """
        content = content + """
                });
            </script>
        """
        
        return content

    @cherrypy.expose
    def AddByPlatform(self):
        dao = DAO()
        currentVersion = dao.GetSiteMasterData("currentVersion")
        currentHeaderContent = dao.GetSiteMasterData("HeaderContents")
        content = ""
        content = content + currentHeaderContent.format(currentVersion)
        content = content + """
            <br />
            <div id="addGameTabs" align="left">
              <ul>
                <li><a href="#addgame-tab">Add Game</a></li>
              </ul>
              <div id="addgame-tab">
                    <div class="ui-widget">
                        <label for="platforms">Platform: </label>
                        <br />
                        <select id="platforms"></select>
                        <br /><br />
                        <button id="addGameButton">Add Games for Platform</button>
                    </div>
              </div>
            </div>
            <script>
                $(document).ready(function(){
                    $("#addGameButton").button();
                    $("#addGameTabs").tabs();
                    $("#addGameButton").click(function() {
                        var platformId = $("#platforms").val();
                        if(platformId == "---")
                        {
                            alert("Please select a platform");
                            return;
                        }                        
                        window.location.href = "/AddWantedGameByPlatform?platformId=" + platformId;
                    });
                    $.getJSON( "/GetPlatforms", function( data ) {
                      var items = [];
                      items.push('<option>---</option>');
                      $.each( data, function( key, val ) {
                        items.push('<option value="'+ key +'">'+ val +'</option>');
                      });
                      $( "#platforms" ).html('');
                      $( "#platforms" ).html(items);
                      var opt = $("#platforms option").sort(function (a,b) { return a.text.toUpperCase().localeCompare(b.text.toUpperCase()) });
                      $("#platforms").append(opt);
                      $("#platforms").find('option:first').attr('selected','selected');
                      $( "#platforms" ).chosen();
                      $("#platforms").trigger("chosen:updated");
                    });  
                });
            </script>
            """
        return content

    @cherrypy.expose
    def AddGame(self):
        dao = DAO()
        currentVersion = dao.GetSiteMasterData("currentVersion")
        currentHeaderContent = dao.GetSiteMasterData("HeaderContents")
        content = ""
        content = content + currentHeaderContent.format(currentVersion)
        content = content + """
            <br />
            <div id="addGameTabs" align="left">
              <ul>
                <li><a href="#addgame-tab">Add Game</a></li>
              </ul>
              <div id="addgame-tab">
                    <div class="ui-widget">
                        <label for="platforms">Platform: </label>
                        <br />
                        <select id="platforms"></select>
                        <br /><br />
                        <label for="games">Game: </label>
                        <br />
                        <select id="games"></select>
                        <br /><br />
                        <button id="addGameButton">Add Game</button>
                    </div>
              </div>
            </div>
            <script>
                $(document).ready(function(){
                    $("#addGameButton").button();
                    $("#addGameTabs").tabs();
                    $("#addGameButton").click(function() {
                        var platformId = $("#platforms").val();
                        var gameId = $("#games").val();
                        if(platformId == "---")
                        {
                            alert("Please select a platform");
                            return;
                        }                        
                        if(gameId == "---")
                        {
                            alert("Please select a game");
                            return;
                        }
                        window.location.href = "/AddWantedGame?platformId=" + platformId + "&gameId=" + gameId;
                    });
                    $("#platforms").change(function() {
                      var selectedValue = $(this).val();
                      if(selectedValue=="---")
                      {
                        $('#games').attr("disabled","disabled");
                      }
                      else
                      {
                        $.getJSON( "/GetGames?platformId=" + selectedValue, function( data ) {
                          var gameItems = [];
                          $( "#games" ).html('');
                          gameItems.push('<option>---</option>');
                          $.each( data, function( key, val ) {
                            gameItems.push('<option value="'+ key +'">'+ val +'</option>');
                          });
                          $( "#games" ).html('');
                          $( "#games" ).html(gameItems);
                          var opt = $("#games option").sort(function (a,b) { return a.text.toUpperCase().localeCompare(b.text.toUpperCase()) });
                          $("#games").append(opt);
                          $("#games").find('option:first').attr('selected','selected');
                          $( "#games" ).chosen();
                          $("#games").trigger("chosen:updated");
                        });
                      }
                    });
                    $.getJSON( "/GetPlatforms", function( data ) {
                      var items = [];
                      items.push('<option>---</option>');
                      $.each( data, function( key, val ) {
                        items.push('<option value="'+ key +'">'+ val +'</option>');
                      });
                      $( "#platforms" ).html('');
                      $( "#platforms" ).html(items);
                      var opt = $("#platforms option").sort(function (a,b) { return a.text.toUpperCase().localeCompare(b.text.toUpperCase()) });
                      $("#platforms").append(opt);
                      $("#platforms").find('option:first').attr('selected','selected');
                      $( "#platforms" ).chosen();
                      $("#platforms").trigger("chosen:updated");
                    });  
                });
            </script>
        """
        return content

    @cherrypy.expose
    def GetPlatforms(self):
        content = '{'
        dao = DAO()
        platforms = dao.GetMasterPlatforms()
        for platform in platforms:
            content = content + '"' + platform[1] + '":"' + platform[2] + '",'
        content = content[:-1]
        content = content + '}'
        return content

    @cherrypy.expose
    def GetGames(self, platformId):
        content = '{'
        dao = DAO()
        games = dao.GetUnwantedMasterGames(platformId)
        for game in games:
            content = content + '"' + game[1] + '":"' + game[2] + '",'
        content = content[:-1]
        content = content + '}'
        return content

    @cherrypy.expose
    def DeleteLogs(self):
        dao = DAO()
        dao.DeleteLogs();
        raise cherrypy.HTTPRedirect("/?statusMessage=Logs Cleared")

    @cherrypy.expose
    def PostProcess(self,gameId,processDir):
        processDir = urllib.unquote_plus(processDir)
        task = Task()
        return task.PostProcess(processDir, gameId)

    @cherrypy.expose
    def AddWantedGame(self, platformId, gameId):
        dao = DAO()
        wantedGameId = dao.AddWantedGame(platformId, gameId, "Wanted")
        raise cherrypy.HTTPRedirect("/?statusMessage=Game Added&addedGameId=" + str(wantedGameId[0]))

    @cherrypy.expose
    def AddWantedGameByPlatform(self, platformId):
        dao = DAO()
        gamesList = dao.GetMasterGames(platformId)
        wantedGameIds = ''
        for game in gamesList:
            gameId = game[1]
            wantedGameIds = wantedGameIds + str(dao.AddWantedGame(platformId, gameId, "Wanted")[0]) + ','
        print wantedGameIds
        if(len(wantedGameIds) > 0):
            wantedGameIds = wantedGameIds[:-1]
        raise cherrypy.HTTPRedirect("/?statusMessage=Games Added&addedGameId=" + wantedGameIds)

    @cherrypy.expose
    def GetFolders(self,folderPath,upDirectory):
        task = Task()
        print('Getting folders')
        return task.GetFolders(folderPath,upDirectory)

    @cherrypy.expose
    def DeleteGame(self,gameId):
        dao = DAO()
        dao.DeleteWantedGame(gameId)
        raise cherrypy.HTTPRedirect("/?statusMessage=Game Deleted")

    @cherrypy.expose
    def ForceSearch(self,gameId):
        task = Task()
        return task.ForceGameSearch(gameId)

    @cherrypy.expose
    def ForceSearchNew(self,gameId):
        task = Task()
        return task.ForceGameSearch(gameId, True)

    @cherrypy.expose
    def UpdateStatus(self,status,gameId):
        try:
            dao = DAO()
            dao.UpdateWantedGameStatus(gameId, status)
            return "Status Updated"
        except Exception as e:
            return e

    @cherrypy.expose
    def SaveSettings(self,headerContent=None,usenetCrawlerEnabled=None,usenetCrawlerApiKey=None,searcherPriority=None,sabnzbdEnabled=None,sabnzbdBaseUrl=None,
                     sabnzbdApiKey=None,sabnzbdCategory=None,destinationFolder=None,footerContent=None,onlySearchNew=None,launchBrowser=None,
                     abgx360Region=None,abgx360Path=None,abgx360Enabled=None,xbox360Extensions=None):
        try:
            dao = DAO()
            if(headerContent != None):
                dao.UpdateMasterSiteData("HeaderContents", headerContent)
            if(footerContent != None):
                dao.UpdateMasterSiteData("FooterContents", footerContent)
            if(usenetCrawlerEnabled != None):
                dao.UpdateMasterSiteData("usenetCrawlerEnabled", usenetCrawlerEnabled)
            if(usenetCrawlerApiKey != None):
                dao.UpdateMasterSiteData("usenetCrawlerApiKey", usenetCrawlerApiKey)
            if(searcherPriority != None):
                dao.SetSearcherPriority(searcherPriority)
            if(usenetCrawlerApiKey != None):
                dao.UpdateMasterSiteData("sabnzbdEnabled", sabnzbdEnabled)
            if(usenetCrawlerApiKey != None):
                dao.UpdateMasterSiteData("sabnzbdBaseUrl", sabnzbdBaseUrl)
            if(usenetCrawlerApiKey != None):
                dao.UpdateMasterSiteData("sabnzbdApiKey", sabnzbdApiKey)
            if(sabnzbdCategory != None):
                dao.UpdateMasterSiteData("sabnzbdCategory", sabnzbdCategory)
            if(destinationFolder != None):
                dao.UpdateMasterSiteData("destinationFolder", destinationFolder)
            if(onlySearchNew != None):
                dao.UpdateMasterSiteData("onlySearchNew", onlySearchNew)
            if(launchBrowser != None):
                dao.UpdateMasterSiteData("launchBrowser", launchBrowser)
            if(abgx360Enabled != None):
                dao.UpdateMasterSiteData("abgx360Enabled", abgx360Enabled)
            if(abgx360Path != None):
                dao.UpdateMasterSiteData("abgx360Path", abgx360Path)
            if(abgx360Region != None):
                dao.UpdateMasterSiteData("abgx360Region", abgx360Region)
            if(xbox360Extensions != None):
                dao.UpdateMasterSiteData("xbox360Extensions",xbox360Extensions)
            return "Settings Saved"
        except Exception as e:
            #e = sys.exc_info()[0]
            return "Error: " + e
    
    @cherrypy.expose
    def Settings(self):
        dao = DAO()
        currentVersion = dao.GetSiteMasterData("currentVersion")
        currentHeaderContent = dao.GetSiteMasterData("HeaderContents")
        currentFooterContent = dao.GetSiteMasterData("FooterContents")
        onlySearchNew = dao.GetSiteMasterData("onlySearchNew")
        launchBrowser = dao.GetSiteMasterData("launchBrowser")

        usenetCrawlerEnabled = dao.GetSiteMasterData("usenetCrawlerEnabled")
        usenetCrawlerApiKey = dao.GetSiteMasterData("usenetCrawlerApiKey")

        sabnzbdEnabled = dao.GetSiteMasterData("sabnzbdEnabled")
        sabnzbdBaseUrl = dao.GetSiteMasterData("sabnzbdBaseUrl")
        sabnzbdApiKey = dao.GetSiteMasterData("sabnzbdApiKey")
        sabnzbdCategory = dao.GetSiteMasterData("sabnzbdCategory")

        destinationFolder = dao.GetSiteMasterData("destinationFolder")

        abgx360Enabled = dao.GetSiteMasterData("abgx360Enabled")
        abgx360Path = dao.GetSiteMasterData("abgx360Path")
        abgx360Region = dao.GetSiteMasterData("abgx360Region")
        xbox360Extensions = dao.GetSiteMasterData("xbox360Extensions")
        
        if(abgx360Region == None):
            abgx360Region = ""

        if(usenetCrawlerEnabled == "true"):
            usenetCrawlerEnabled = "checked"
        else:
            usenetCrawlerEnabled = ""
        if(sabnzbdEnabled == "true"):
            sabnzbdEnabled = "checked"
        else:
            sabnzbdEnabled = ""
        if(onlySearchNew == "true"):
            onlySearchNew = "checked"
        else:
            onlySearchNew = ""
        if(launchBrowser == "true"):
            launchBrowser = "checked"
        else:
            launchBrowser = ""
        if(abgx360Enabled == "true"):
            abgx360Enabled = "checked"
        else:
            abgx360Enabled = ""

        content = ""
        content = content + currentHeaderContent.format(currentVersion)
        content = content + """
            
            <br />
            <div align="right">
            <button id="saveButton">Save</button>
            </div>
            <div id="settingsTabs">
              <ul>
                <li><a href="#gamezserver-tab">Gamez Server</a></li>
                <li><a href="#downloaders-tab">Downloaders</a></li>
                <li><a href="#searchers-tab">Searchers</a></li>
                <li><a href="#postprocess-tab">Post Process</a></li>
              </ul>
              <div id="gamezserver-tab">
                
                <fieldset align="left">
                    <legend>General</legend>
                    <div>
                        <input type="checkbox" name="launchBrowser" id="launchBrowser" """ + launchBrowser + """ />
                        <label for="launchBrowser">Launch browser on startup</label>
                    </div>
                    <br />
                    <label for="headerContent">Header Content</label>
                    <br />
                    <textarea name="headerContent" id="headerContent" rows="10" cols="100">"""
        content = content + currentHeaderContent.format(currentVersion)
        content = content + """</textarea>
                    <br /><br />
                    <label for="footerContent">Footer Content</label>
                    <br />
                    <textarea name="footerContent" id="footerContent" rows="10" cols="100">"""
        content = content + currentFooterContent
        content = content + """</textarea>
                </fieldset>
                <br />
                <fieldset>
                    <legend>Search Settings</legend>
                    <div>
                        <input type="checkbox" name="onlySearchNew" id="onlySearchNew" """ + onlySearchNew + """ />
                        <label for="onlySearchNew">Only Search New (Ignores previously snatched items)</label>
                    </div>
                </fieldset>
              </div>
              <div id="downloaders-tab">
                <fieldset align="left">
                    <legend>Sabnzbd+</legend>
                    Enable?
                    <input type="checkbox" id="sabnzbdEnabled" """ + sabnzbdEnabled + """ />
                    <div id="sabnzbdSection" style="display:none">
                        <div>
                            <label for="sabnzbdBaseUrl">Sabnzbd+ Base Url (ie: http://localhost:8080)</label>
                            <br />
                            <input type="text" size="50" name="sabnzbdBaseUrl" id="sabnzbdBaseUrl" value='""" + sabnzbdBaseUrl  + """' />
                        </div>
                        <br />
                        <div>
                            <label for="sabnzbdApiKey">Sabnzbd+ API Key</label>
                            <br />
                            <input type="text" size="50" name="sabnzbdApiKey" id="sabnzbdApiKey" value='""" + sabnzbdApiKey + """' />
                        </div>
                        <br />
                        <div>
                            <label for="sabnzbdApiKey">Sabnzbd+ Category</label>
                            <br />
                            <input type="text" size="50" name="sabnzbdCategory" id="sabnzbdCategory" value='""" + sabnzbdCategory + """' />
                        </div>
                    </div>
                </fieldset>
              </div>
              <div id="searchers-tab">
                <fieldset align="left">
                <legend>Search Order</legend>
                <ul id="prioritiesSorter" align="left" border="1">
                  <li class="ui-state-default" id="usenetCrawlerPriority"><span class="ui-icon ui-icon-arrowthick-2-n-s"></span>Usenet-Crawler</li>
                </ul>
                </fieldset>
                <fieldset align="left">
                    <legend>Usenet-Crawler</legend>
                    Enable?
                    <input type="checkbox" id="usenetCrawlerEnabled" """ + usenetCrawlerEnabled + """ />
                    <div id="usenetCrawlerSection" style="display:none">
                        <label for="usenetCrawlerApiKey">API Key</label>
                        <br />
                        <input type="text" size="50" name="usenetCrawlerApiKey" id="usenetCrawlerApiKey" value='""" + usenetCrawlerApiKey + """' />
                    </div>
                </fieldset>
              </div>
              <div id="postprocess-tab">
                <fieldset align="left">
                    <legend>General</legend>
                    <label for="destinationFolder">Destination Folder</label>
                    <br />
                    <input type="input" size="50" id="destinationFolder" value='""" + destinationFolder + """' />
                    <input type="button" id="browseButton" value="Browse" />
                    <div id="folderBrowser" title="Select Folder">
                    </div>
                </fieldset>
                <fieldset>
                    <legend>XBOX 360</legend>
                    Enable ABGX360?
                    <input type="checkbox" id="abgx360Enabled" """ + abgx360Enabled + """ />
                    <div id="abgx360Section" style="display:none">
                        <div>
                            <label for="abgx360Path">ABGX360 Path (ie: C:\\Windows\\SysWOW64\\abgx360.exe)</label>
                            <br />
                            <input type="text" size="50" name="abgx360Path" id="abgx360Path" value='""" + abgx360Path  + """' />
                        </div>
                        <br />
                        <div>
                            <label for="abgx360Region">Console Region</label>
                            <br />
                            <select id="abgx360Region" name="abgx360Region">
                                <option value="">Any</option>
                                <option value="000000FF">NTSC/U</option>
                                <option value="00010000">PAL (Australia)
                                <option value="00FE0000">PAL (Europe)</option>
                                <option value="00000100">NTSC/J (Japan)</option>
                                <option value="00000300">NTSC/J (China)</option>
                                <option value="0000FC00">NTSC/J (Other)</option>
                            </select>
                        </div>
                        <br />
                        <div>
                            <label for="xbox360Extensions">Valid Extensions</label>
                            <br />
                            <input type="text" size="50" id="xbox360Extensions" name="xbox360Extensions" value='""" + xbox360Extensions + """' />
                        </div>
                    </div>
                </fieldset>
              </div>
            </div>
            <style>
                  #sortable { list-style-type: none; margin: 0; padding: 0; width: 60%; }
                  #sortable li { margin: 0 3px 3px 3px; padding: 0.4em; padding-left: 1.5em; font-size: 1.4em; height: 18px; }
                  #sortable li span { position: absolute; margin-left: -1.3em; }
                  #folderBrowserSelector .ui-selecting { background: #FECA40; }
                  #folderBrowserSelector .ui-selected { background: #F39814; color: white; }
                  #folderBrowserSelector { list-style-type: none; margin: 0; padding: 0; width: 80%; }
                  #folderBrowserSelector li { margin: 3px; padding: 0.4em; font-size: 1.4em; height: 18px; }
            </style>
             <script>
                $(document).ready(function () {
                    $("#abgx360Region").val('""" + abgx360Region + """');
                    $("#abgx360Region").chosen({width:200});
                    var previousNestedPathNode = ''
                    var previousPathNode = ''
                    var pathNode = '';
                    var lastSubPath = ''
                    var selectedPath = '';
                    var folderPathUrl = '';
                    $("#browseButton").button();
                    function folderHandling()
                    {
                        if(selectedPath == "/")
                        {
                            selectedPath = "";
                        }
                        if(pathNode=="...")
                        {
                            selectedPath = selectedPath.substring( 0, selectedPath.indexOf(previousPathNode));
                            previousPathNode = selectedPath;
                            folderPathUrl = '/GetFolders?upDirectory=True&folderPath=' + selectedPath;
                        }
                        else
                        {
                            folderPathUrl = '/GetFolders?upDirectory=False&folderPath=' + selectedPath;
                        }
                        $.ajax({
                            type: "GET",
                            url: folderPathUrl,
                            success: function (data) {
                                var resultData = '';
                                resultData = resultData + '<h4>' + selectedPath + '</h4>'
                                resultData = resultData +'<ul id="folderBrowserSelector">';
                                var arrayLength = data.split(',').length;
                                for (var i = 0; i < arrayLength; i++) {
                                    resultData = resultData + '<li class="ui-widget-content" id="' + data.split(',')[i]  + '">' + data.split(',')[i] + '</li>';
                                }
                                resultData = resultData + '</ul>';
                                $('#folderBrowser').html(resultData);
                                $("#folderBrowserSelector").selectable({
                                    selecting: function(event, ui){
                                        if( $(".ui-selected, .ui-selecting").length > 1){
                                              $(ui.selecting).removeClass("ui-selecting");
                                        }
                                    },
                                    selected: function(event,ui) {
                                        if(ui.selected.id != "...")
                                        {
                                            lastSubPath = ui.selected.id;
                                            selectedPath = selectedPath + ui.selected.id;
                                            previousPathNode = pathNode;
                                            pathNode = ui.selected.id;
                                        }
                                        else
                                        {
                                            alert(selectedPath)
                                            tmpPath = selectedPath.substr(0,selectedPath.length-1)
                                            indexToRemove = selectedPath.lastIndexOf(selectedPath.substr(tmpPath.lastIndexOf("/"), tmpPath.length-tmpPath.lastIndexOf("/")));
                                            selectedPath = selectedPath.substr(0,indexToRemove) + '/';
                                        }
                                        
                                        folderHandling();
                                    }
                                });
                            },
                            error: function (xhr, ajaxOptions, thrownError) 
                            {
                                toastr.info('Unable to get folders: ' + thrownError);
                            }
                        });
                    }
                    $("#browseButton").click(function(){
                        folderHandling();
                        $('#folderBrowser').dialog('open');
                    });
                    $("#folderBrowser").dialog({
                        bgiframe: true,
                        autoOpen: false,
                        minHeight: 450,
                        width: 600,
                        modal: true,
                        closeOnEscape: false,
                        draggable: false,
                        resizable: false,
                        buttons: {
                                'OK': function(){
                                    $(this).dialog('close');
                                    callback('OK');
                                },
                                'Cancel': function(){
                                    $(this).dialog('close');
                                    callback('Cancel');
                                }
                            }
                    });
                    function callback(value){
                         if(value=="OK")
                         {
                            $("#destinationFolder").val(selectedPath)
                         }
                         selectedPath = '';
                    }
                    if($("#usenetCrawlerEnabled").is(':checked'))
                    {
                        $('#usenetCrawlerSection').toggle();
                    }
                    if($("#sabnzbdEnabled").is(':checked'))
                    {
                        $('#sabnzbdSection').toggle();
                    }
                    $( "#prioritiesSorter" ).sortable();
                    $( "#prioritiesSorter" ).disableSelection();
                    $('#sabnzbdEnabled').change(function() {
                        $('#sabnzbdSection').toggle();
                    });
                    $('#usenetCrawlerEnabled').change(function() {
                        $('#usenetCrawlerSection').toggle();
                    });
                    if($("#abgx360Enabled").is(':checked'))
                    {
                        $('#abgx360Section').toggle();
                    }
                    $('#abgx360Enabled').change(function() {
                        $('#abgx360Section').toggle();
                    });
                    $("#settingsTabs").tabs();
                    $("#saveButton").button();
                    $("#saveButton").click(function () {
                        var assembledUrl = "/SaveSettings?headerContent=" + encodeURIComponent($("#headerContent").val());
                        assembledUrl = assembledUrl + "&usenetCrawlerEnabled=" + $("#usenetCrawlerEnabled").is(':checked');
                        assembledUrl = assembledUrl + "&usenetCrawlerApiKey=" + $("#usenetCrawlerApiKey").val();
                        assembledUrl = assembledUrl + "&searcherPriority=" + $("#prioritiesSorter").sortable('toArray');
                        assembledUrl = assembledUrl + "&sabnzbdEnabled=" + $("#sabnzbdEnabled").is(':checked');
                        assembledUrl = assembledUrl + "&sabnzbdBaseUrl=" + $("#sabnzbdBaseUrl").val();
                        assembledUrl = assembledUrl + "&sabnzbdApiKey=" + $("#sabnzbdApiKey").val();
                        assembledUrl = assembledUrl + "&sabnzbdCategory=" + $("#sabnzbdCategory").val();
                        assembledUrl = assembledUrl + "&destinationFolder=" + $("#destinationFolder").val();
                        assembledUrl = assembledUrl + "&footerContent=" + encodeURIComponent($("#footerContent").val())
                        assembledUrl = assembledUrl + "&onlySearchNew=" + $("#onlySearchNew").is(':checked');
                        assembledUrl = assembledUrl + "&launchBrowser=" + $("#launchBrowser").is(':checked');
                        assembledUrl = assembledUrl + "&abgx360Enabled=" + $("#abgx360Enabled").is(':checked');
                        assembledUrl = assembledUrl + "&abgx360Path=" + $("#abgx360Path").val();
                        assembledUrl = assembledUrl + "&abgx360Region=" + $("#abgx360Region").val();
                        assembledUrl = assembledUrl + "&xbox360Extensions=" + $("#xbox360Extensions").val();

                        $.ajax({
                            type: "GET",
                            url: assembledUrl,
                            success: function (data) {
                                toastr.info(data);
                            }
                        });
                    });
                });
            </script>           
            
            
        """
        return content

    @cherrypy.expose
    def Log(self,level=None):
        dao = DAO()
        if(level==None or level=="All"):
            level = "All"
            logs = dao.GetLogMessages()
        else:
            logs = dao.GetLogMessages(level)
        currentHeaderContent = dao.GetSiteMasterData("HeaderContents")
        content = ""
        currentVersion = dao.GetSiteMasterData("currentVersion")
        content = content + currentHeaderContent.format(currentVersion)
        content = content + """
            <br />
            <table width="100%"><tr>
                <td>
                    <select id="levelDropDown">
                        <option>All</option>
                        <option>Error</option>
                        <option>Info</option>
                        <option>Warning</option>
                    </select>
                </td><td align="right"><button id="clearLogsButton">Clear All Logs</button></td></tr></table>
            
            
            <table id="logTable" class="display" cellspacing="0" width="100%"><thead><tr><th>Level</th><th>Message</th><th>Date</th></tr></thead><tfoot><tr><th>Level</th><th>Message</th><th>Date</th></tr></tfoot></td></tr>
        """
        content = content + "<tbody>"
        for logRow in logs:
            rowContent = "<tr><td>" + logRow[0] + "</td><td>" + logRow[1] + "</td><td>" + logRow[2] + "</td></tr>"
            content = content + rowContent
        content = content + "</tbody>"
        content = content + """
            </table>
            <script>
                $(document).ready(function () {
                    $('#clearLogsButton').button();
                    $('#clearLogsButton').click(function(){
                        window.location.href = '/DeleteLogs';
                    });
                    $('#logTable').dataTable({
                        "pagingType": "full_numbers"
                    });
                    """
        content = content + "$('#levelDropDown').val('" + level + "');"
        content = content + """
                    
                    $("#levelDropDown").chosen({width:100});
                    $('#levelDropDown').change(function() {
                      var selectedValue = $(this).val();
                      var pageUrl = '/Log/?level=' + selectedValue;
                      window.location.href = pageUrl;
                    });
                });
            </script>
        """
        return content
   