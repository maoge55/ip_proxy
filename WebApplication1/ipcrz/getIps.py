#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2021/5/11
# @File    : getIps.py
# @Description: 获取代理文件

__author__ = 'Mao ZhongJie'

from enum import Flag
from config import jcdl
from header import headers,headers1
from sql import *
from types import coroutine
from requests.sessions import session
from datetime import datetime
import asyncio,aiohttp,time

async def exe_fns(module_name):
    '''从网站获取ip'''
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    tasks=[]
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        if not attr.startswith('getdl_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            tasks.append(asyncio.create_task(fn()))
    res= await asyncio.gather(*tasks)
    return res

async def jc_ip(session,db,host,proip,sem):

    async with sem:
        try:
            url=f'https://{host}'
            proxy=f'http://{proip}'
            async with session.request('GET',url,headers=headers1,proxy=proxy,timeout=20) as resp:
                if resp.status!=200:
                    aff=await del_ip_one(db,'ips',proip)
                    print(f'{proip}状态码错误:{resp.status},删除该代理ip个数:{aff}')
                    return False
                cot= await resp.read()
                if len(cot)<=20000:
                    aff=await del_ip_one(db,'ips',proip)
                    print(f'{proip}=>内容长度错误,删除该代理ip个数:{aff}')
                    return False
                print(f'{proip}检测成功,保留')
                return True
        except Exception as e:
            aff=await del_ip_one(db,'ips',proip)
            print(f'错误:{proip}=>{e},删除该代理ip个数:{aff}')
            return False

async def main():
    n=1
    with open('count.txt','r',encoding='utf8') as f:
        s=f.readline()
        n=int(s) if s else n
    #程序开始，访问两个数据库并用目标站的所有host检测ip是否能运行
    while True:
        print(f'第{n}次维护开始，等待3秒...')
        st=time.time()
        await asyncio.sleep(3)
        for k,v in jcdl.items():
            taskJc=[]
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
                sem=asyncio.Semaphore(20)
                res=await find_all_ip(f'dbs/{k}.db3','ips')
                print(f'{k}数据库共{len(res)}个ip待检测')
                for tp in res:
                    taskJc.append(asyncio.create_task(jc_ip(session,f'dbs/{k}.db3',v,tp[0],sem)))

                await asyncio.gather(*taskJc)

        flag=False #判断是否需要重新采集代理ip（个数小于100）
        for k,v in jcdl.items():
            res=await find_all_ip(f'dbs/{k}.db3','ips')
            print(f'{k}检测完成，数据库还剩{len(res)}个')
            if len(res)<=100:
                flag=True

        if flag:
            print('存在数据库ip数不足100,开启采集任务...')
            await asyncio.sleep(3)
            await exe_fns('ipsbysite')
        
        et=time.time()
        print(f'第{n}次维护结束,耗时{(et-st):.2f}秒')

        n+=1

        with open('count.txt','w',encoding='utf8') as f:
            f.write(str(n))
        
        await asyncio.sleep(1000)
    # dateStr=(datetime.now()).strftime('%Y_%m_%d_%H_%M_%S')
    # ips=[]
    # for v in res:
    #     ips.extend(v)
    # fname='ips/ips_{0}.txt'.format(dateStr)

    # with open(fname,'w') as f:
    #     f.writelines((v+'\n' for v in ips))


if __name__=='__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop=asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
