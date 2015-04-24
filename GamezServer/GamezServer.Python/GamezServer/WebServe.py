

import cherrypy
import GamezServer
class WebServe(object):
    """description of class"""

    @cherrypy.expose
    def index(self):
        currentHeaderContent = GamezServer.DAO.DAO.GetSiteMasterData("HeaderContents")
        content = ""
        content = content + currentHeaderContent
        return content

    @cherrypy.expose
    def SaveSettings(self,headerContent=None):
        try:
            if(headerContent != None):
                GamezServer.DAO.DAO.UpdateMasterSiteData(headerContent)
            return "Settings Saved"
        except:
            e = sys.exc_info()[0]
            return "Error: " + e
    
    @cherrypy.expose
    def Settings(self):
        currentHeaderContent = GamezServer.DAO.DAO.GetSiteMasterData("HeaderContents")
        content = ""
        content = content + currentHeaderContent
        content = content + """
            
            <br />
            <div id="settingsTabs" align="right">
              <ul>
                <li><a href="#gamezserver-tab">Gamez Server</a></li>
              </ul>
              <div id="gamezserver-tab">
                <button id="saveButton">Save</button>
                <fieldset align="left">
                    <legend>General</legend>
                    <label for="headerContent">Header Content</label>
                    <br />
                    <textarea name="headerContent" id="headerContent" rows="10" cols="100">"""
        content = content + currentHeaderContent
        content = content + """</textarea>
                </fieldset>
              </div>
            </div>
             <script>
                $(document).ready(function () {
                    $("#settingsTabs").tabs();
                    $("#saveButton").button();
                    $("#saveButton").click(function () {
                        $.ajax({
                            type: "GET",
                            url: "/SaveSettings?headerContent=" + encodeURIComponent($("#headerContent").val()),
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
        if(level==None or level=="All"):
            level = "All"
            logs = GamezServer.DAO.DAO.GetLogMessages()
        else:
            logs = GamezServer.DAO.DAO.GetLogMessages(level)
        currentHeaderContent = GamezServer.DAO.DAO.GetSiteMasterData("HeaderContents")
        content = ""
        content = content + currentHeaderContent
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
                </td><td align="right"><button>Clear All Logs</button></td></tr></table>
            
            
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
   