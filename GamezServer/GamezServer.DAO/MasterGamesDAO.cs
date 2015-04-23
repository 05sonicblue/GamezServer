using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GamezServer.DAO
{
    public class MasterGamesDAO
    {
        public static List<Platform> GetPlatforms()
        {
            List<Platform> result = null;
            try
            {
                using (var data = new GamezServerEntities())
                {
                    result = data.Platforms.ToList();
                }
            }
            catch(Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
            return result;
        }

        public static void SaveOrUpdate(Platform objectToSave)
        {
            try
            {
                using (var data = new GamezServerEntities())
                {
                    if (objectToSave.ID == default(int))
                    {
                        data.Platforms.Add(objectToSave);
                    }
                    else
                    {
                        data.Entry(objectToSave).State = System.Data.Entity.EntityState.Modified;
                    }
                    data.SaveChanges();
                }
            }
            catch(Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }
    }
}
