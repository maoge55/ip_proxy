using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Web.Http;
using System.Data;
using System.Data.SQLite;

namespace WebApplication1.Controllers
{
    public class IPsController : ApiController
    {
        // GET api/<controller>
        public DataTable Get()
        {
            using (SQLiteConnection connection = new SQLiteConnection(@"Data Source=E:\ftp\WebApplication1\ipcrz\dbs\amazon.db3"))
            {
                connection.Open();
                string sql = "select ip from ips order by ping";
                using (SQLiteCommand command = new SQLiteCommand(sql, connection))
                {
                    SQLiteDataAdapter adapter = new SQLiteDataAdapter(command);
                    DataTable data = new DataTable();
                    adapter.Fill(data);
                    return data;
                }
            }
        }

        // GET api/<controller>/5
        public DataTable Get(string id)
        {
            string strgd = @"Data Source=E:\datatwo\VSProgram\WebApplication1\ipcrz\dbs\";
            string db = strgd + id+@".db3";
            using (SQLiteConnection connection = new SQLiteConnection(db))
            {
                connection.Open();
                string sql = "select ip from ips order by ping";
                using (SQLiteCommand command = new SQLiteCommand(sql, connection))
                {
                    SQLiteDataAdapter adapter = new SQLiteDataAdapter(command);
                    DataTable data = new DataTable();
                    adapter.Fill(data);
                    return data;
                }
            }

        }

        // POST api/<controller>
        public void Post([FromBody] string value)
        {
        }

        // PUT api/<controller>/5
        public void Put(int id, [FromBody] string value)
        {
        }

        // DELETE api/<controller>/5
        public void Delete(int id)
        {
        }
    }
}