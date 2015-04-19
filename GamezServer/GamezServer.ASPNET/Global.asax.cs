using Quartz;
using Quartz.Impl;
using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Configuration;
using System.Linq;
using System.Threading;
using System.Web;
using System.Web.Security;
using System.Web.SessionState;

namespace GamezServer.ASPNET
{
    public class Global : System.Web.HttpApplication
    {
        IScheduler scheduler;

        protected void Application_Start(object sender, EventArgs e)
        {
            NameValueCollection quartzSettings = new NameValueCollection();
            quartzSettings["quartz.scheduler.instanceName"] = ConfigurationManager.AppSettings["quartz.scheduler.instanceName"].ToString();
            quartzSettings["quartz.threadPool.type"] = ConfigurationManager.AppSettings["quartz.threadPool.type"].ToString();
            quartzSettings["quartz.threadPool.threadCount"] = ConfigurationManager.AppSettings["quartz.threadPool.threadCount"].ToString();
            quartzSettings["quartz.threadPool.threadPriority"] = ConfigurationManager.AppSettings["quartz.threadPool.threadPriority"].ToString();
            scheduler = new StdSchedulerFactory(quartzSettings).GetScheduler();
            try
            {
                scheduler.Start();
                BuildJobs();
            }
            catch
            {
                if (scheduler != null && scheduler.IsStarted)
                {
                    scheduler.Shutdown();
                }
            }
        }

        protected void Session_Start(object sender, EventArgs e)
        {

        }

        protected void Application_BeginRequest(object sender, EventArgs e)
        {

        }

        protected void Application_AuthenticateRequest(object sender, EventArgs e)
        {

        }

        protected void Application_Error(object sender, EventArgs e)
        {

        }

        protected void Session_End(object sender, EventArgs e)
        {

        }

        protected void Application_End(object sender, EventArgs e)
        {
            if (scheduler != null && scheduler.IsStarted)
            {
                scheduler.Shutdown();
            }
        }

        private void BuildJobs()
        {
            string gameUpdaterSchedule = ConfigurationManager.AppSettings["GameUpdaterSchedule"];
            IJobDetail job = JobBuilder.Create(typeof(UpdateGamesListJob))
                .WithIdentity("GameUpdater", "GameUpdater")
                                .Build();
            ITrigger trigger = TriggerBuilder.Create()
                            .WithIdentity("GameUpdater", "GameUpdater")
                            .StartNow()
                            .WithCronSchedule(gameUpdaterSchedule, x => x.WithMisfireHandlingInstructionFireAndProceed())
                            .Build();
            scheduler.ScheduleJob(job, trigger);
        }
    }
}