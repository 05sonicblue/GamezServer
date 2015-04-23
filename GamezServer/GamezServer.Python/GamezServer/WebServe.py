

import cherrypy
import GamezServer
class WebServe(object):
    """description of class"""

    @cherrypy.expose
    def index(self):
        return """
            <link href='static/styles/Menu.css' rel='stylesheet' />
            <div id='cssmenu'>
                <ul>
                    <li class='active align-center'>
                        <a href='#'><span>Home</span></a>
                    </li>
                    <li class='active has-sub'><a href='#'><span>Settings</span></a>
                        <ul>
                            <li class='has-sub'><a href='#'><span>Notifications</span></a></li>
                        </ul>
                    </li>
                    <li class='active align-center'>
                        <a href='/Log'><span>Log</span></a>
                    </li>
                </ul>
            </div>
        """

    @cherrypy.expose
    def Log(self,level=None):
        if(level==None or level=="All"):
            level = "All"
            logs = GamezServer.DAO.DAO.GetLogMessages()
        else:
            logs = GamezServer.DAO.DAO.GetLogMessages(level)
        print(logs)
        content = ""
        content = content + """
            <script src="/static/scripts/jquery.js"></script>
            <script src="/static/scripts/jquery-ui.js"></script>
            <script src="/static/scripts/Menu.js"></script>
            <script src="/static/scripts/jquery.dataTables.js"></script>
            <script src="/static/scripts/dataTables.jqueryui.js"></script>
            <script src="/static/scripts/chosen.jquery.js"></script>

            <link href="/static/styles/jquery-ui.css" rel="stylesheet" />
            <link href="/static/styles/Menu.css" rel="stylesheet" />
            <link href="/static/styles/dataTables.jqueryui.css" rel="stylesheet" />
            <link href="/static/styles/chosen.css" rel="stylesheet" />
            <div id='cssmenu'>
                <ul>
                    <li class='active align-center'>
                        <a href='#'><span>Home</span></a>
                    </li>
                    <li class='active has-sub'><a href='#'><span>Settings</span></a>
                        <ul>
                            <li class='has-sub'><a href='#'><span>Notifications</span></a></li>
                        </ul>
                    </li>
                    <li class='active align-center'>
                        <a href='/Log'><span>Log</span></a>
                    </li>
                </ul>
            </div>
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
                    
                    $("#levelDropDown").chosen();
                    $('#levelDropDown').change(function() {
                      var selectedValue = $(this).val();
                      var pageUrl = '/Log/?level=' + selectedValue;
                      window.location.href = pageUrl;
                    });
                });
            </script>
        """
        return content
   