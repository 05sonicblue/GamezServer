using GamezServer.Utilities;
using Quartz;
using System;
using System.IO;
using System.Net;
using System.Web;
using GamezServer.DomainObject.External;

namespace GamezServer.ASPNET
{
    [DisallowConcurrentExecution()]
    public class UpdateGamesListJob : IJob
    {
        public void Execute(IJobExecutionContext context)
        {
            Platforms();
        }

        private void Platforms()
        {
            string url = "http://thegamesdb.net/api/GetPlatformsList.php";
            HttpWebRequest request = HttpWebRequest.CreateHttp(url);
            HttpWebResponse response = (HttpWebResponse)request.GetResponse();
            using (StreamReader reader = new StreamReader(response.GetResponseStream()))
            {
                string contents = reader.ReadToEnd();
                var platforms = Serialization.Deserialize<GamezServer.DomainObject.External.GameDB.Platform>(contents);
                if (platforms != null && platforms.Platforms != null && platforms.Platforms.Length > 0)
                {
                    foreach (var platform in platforms.Platforms)
                    {

                    }
                }
                
            }
        }
    }
}
