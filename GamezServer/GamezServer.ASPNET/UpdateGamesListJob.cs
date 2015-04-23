using GamezServer.Utilities;
using Quartz;
using System;
using System.IO;
using System.Net;
using System.Web;
using GamezServer.DomainObject.External;
using System.Collections;
using GamezServer.DAO;
using System.Collections.Generic;
using System.Linq;

namespace GamezServer.ASPNET
{
    [DisallowConcurrentExecution()]
    public class UpdateGamesListJob : IJob
    {
        public void Execute(IJobExecutionContext context)
        {
            Platforms();
        }

        public static void Platforms()
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
                    List<Platform> existingPlatforms = MasterGamesDAO.GetPlatforms();
                    foreach (var platform in platforms.Platforms)
                    {
                        if (existingPlatforms.Where(x => x.PlatformUniqueName == platform.alias).FirstOrDefault() != null)
                        {
                            //Update
                            Platform existingRecord = existingPlatforms.Where(x => x.PlatformUniqueName == platform.alias).FirstOrDefault();
                            existingRecord.PlatformID = platform.id.ToString();
                            existingRecord.PlatformName = platform.name;
                            MasterGamesDAO.SaveOrUpdate(existingRecord);
                        }
                        else
                        {
                            //Add
                            Platform newRecord = new Platform();
                            newRecord.PlatformID = platform.id.ToString();
                            newRecord.PlatformName = platform.name;
                            newRecord.PlatformUniqueName = platform.alias;
                            MasterGamesDAO.SaveOrUpdate(newRecord);
                        }
                    }
                }
            }
        }
    }
}
