using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using System.Xml.Serialization;

namespace GamezServer.Utilities
{
    /// <summary>
    /// Utility class for serialization
    /// </summary>
    public class Serialization
    {
        /// <summary>
        /// Serializes an object to an xml string
        /// </summary>
        /// <typeparam name="T">Object Type</typeparam>
        /// <param name="objectToSerialize">Object To Serialize</param>
        /// <returns>XML String</returns>
        public static string Serialize<T>(T objectToSerialize)
        {
            string result = String.Empty;
            if (objectToSerialize != null)
            {
                XmlSerializer serializer = new XmlSerializer(typeof(T));
                StringWriter stringWriter = new StringWriter();
                using (XmlWriter writer = XmlWriter.Create(stringWriter))
                {
                    serializer.Serialize(writer, objectToSerialize);
                    result = stringWriter.ToString();
                }
            }
            return result;
        }

        /// <summary>
        /// Deserializes an XML string into an object
        /// </summary>
        /// <typeparam name="T">Object Type</typeparam>
        /// <param name="xmlToDeserialize">XML String to Deserialize</param>
        /// <returns>Object based on Object Type</returns>
        public static T Deserialize<T>(string xmlToDeserialize) where T : class
        {
            if (String.IsNullOrEmpty(xmlToDeserialize))
            {
                return null;
            }
            XmlSerializer serializer = new XmlSerializer(typeof(T));
            using (StringReader reader = new StringReader(xmlToDeserialize))
            {
                return (T)serializer.Deserialize(reader);
            }
        }
    }
}
