using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GamezServer.DomainObject.External.GameDB
{
    [System.Xml.Serialization.XmlRootAttribute(ElementName="Data", Namespace="", IsNullable=false)]
    public class Platform
    {
        public string basePlatformUrl { get; set; }

        [System.Xml.Serialization.XmlArrayItemAttribute("Platform", IsNullable = false)]
        public PlatformData[] Platforms { get; set; }
    }

    public class PlatformData
    {
        public ushort id { get; set; }
        public string name { get; set; }
        public string alias { get; set; }
    }
}
