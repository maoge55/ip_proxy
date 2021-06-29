#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2021/5/14
# @Author  : Mao ZhongJie
# @File    : sql.py
# @Description: 连接数据库函数库

import aiosqlite
import time
import uuid

from aiosqlite import cursor

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

async def doSql(sql,db):
    async with aiosqlite.connect(db) as db:
        async with db.execute(sql) as cursor:
            await db.commit()
            if db.total_changes:
                return db.total_changes
            else:
                rows=await cursor.fetchall()
                return rows

async def insert_ip(db,table,ip,ping):
    async with aiosqlite.connect(db) as db:
        tt=round(time.time(),3)
        await db.execute(f"insert into {table} (id,ip,ping,create_at) values ('{next_id()}','{ip}',{ping},{tt})")
        await db.commit()
        return db.total_changes

async def del_ip_one(db,table,ip):
    async with aiosqlite.connect(db) as db:
        await db.execute(f"delete from {table} where ip='{ip}'")
        await db.commit()
        return db.total_changes

async def del_ip_where(db,table,where):
    async with aiosqlite.connect(db) as db:
        await db.execute(f"delete from {table} where {where}")
        await db.commit()
        return db.total_changes

async def update(db,table,ip,nip):
    pass

async def find_all_ip(db,table):
    async with aiosqlite.connect(db) as db:
        #db.row_factory = aiosqlite.Row
        async with db.execute(f"select ip,ping from {table} order by ping") as cursor:
            rows= await cursor.fetchall()
            #print(db.total_changes)
            return rows

async def find_ips(db,table,where):
    async with aiosqlite.connect(db) as db:
        #db.row_factory = aiosqlite.Row
        async with db.execute(f"select ip,ping from {table} where {where} order by ping") as cursor:
            rows= await cursor.fetchall()
            return rows


