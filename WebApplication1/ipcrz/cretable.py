from sql import *
import asyncio,aiosqlite
import os

async def main():

    os.remove('dbs/amazon.db3')
    os.remove('dbs/google.db3')
    await doSql('create table ips(id varchar(50)  primary key not null, ip VARCHAR(50) UNIQUE not null,ping REAL,create_at REAL);','dbs/amazon.db3')
    await doSql('create table ips(id varchar(50)  primary key not null, ip VARCHAR(50) UNIQUE not null,ping REAL,create_at REAL);','dbs/google.db3')
 
if __name__=='__main__':
    loop= asyncio.get_event_loop()
    loop.run_until_complete(main())