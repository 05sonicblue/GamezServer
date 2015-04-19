<%@ Page Title="Home" Language="C#" MasterPageFile="~/Master.Master" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="GamezServer.ASPNET.Default" %>
<asp:Content ID="Content1" ContentPlaceHolderID="HeadContent" runat="server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="PageContent" runat="server">
    <script>
        $(document).ready(function () {
            $('#example').dataTable({
                "pagingType": "full_numbers"
            });
        });
    </script>
    <table id="example" class="display" cellspacing="0" width="100%">
				<thead>
					<tr>
						<th>Game</th>
						<th>System</th>
						<th>Status</th>
						<th>Downloaded Date</th>
					</tr>
				</thead>

				<tfoot>
					<tr>
						<th>Game</th>
						<th>System</th>
						<th>Status</th>
						<th>Downloaded Date</th>
					</tr>
				</tfoot>

				<tbody>
					<tr>
						<td>Tiger Nixon</td>
						<td>System Architect</td>
						<td>Edinburgh</td>
						<td>61</td>
					</tr>
				</tbody>
			</table>
</asp:Content>
