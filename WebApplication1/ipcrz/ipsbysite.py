#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2021/5/12
# @Author  : Mao ZhongJie
# @File    : ipsbysite
# @Description: 通过代理网站获取代理ip的方法文件


from socket import timeout
from config import *
from header import headers,headers1
from sql import *
from lxml import etree
import asyncio,aiohttp
import re,time
import base64,json

async def jc_ips(session,db,url,proip,sem):
    async with sem:
        try:
            start=time.time()
            proxy=f'http://{proip}'
            async with session.request('GET',url,headers=headers1,proxy=proxy,timeout=20) as resp:
                if resp.status!=200:
                    print(f'{proip}状态码错误{url}=>{resp.status}')
                    return False
                cot= await resp.read()
                if len(cot)<=20000:
                    print(f'{proip}=>{url}=>内容长度错误')
                    return False
                #存到数据库
                ping=round(time.time()-start,2)

                aff=await insert_ip(db,'ips',proip,ping)
                if aff:
                    print(f'{proip}检测访问{url}可用,并且保存到数据库')
                else:
                    print(f'{proip}检测可用{url},未保存到数据库')
                return proip
        except Exception as e:
            print(f'错误:{proip}=>{url}=>{e}')
            return False

#小苏代理
async def getdl_xiao_su():

    print('正在获取小苏代理...')

    host=dlurl['xiaosu']['host'] #小苏代理主机域名
    listUrls=[dlurl['xiaosu']['listUrl'].format(j) for j in range(1,2)]
    coturls=[]
    ips=[]
    checkIps=[]
 
    async def get_coturls(session,url,sem):
        '''从列表页采集的url'''
        async with sem:
            try:
                async with session.request('GET',url,headers=headers1) as resp:
                    resbt=await resp.read()
                    html=etree.HTML(resbt)
                    hrefs=html.xpath('//div[@class="title"]/a/@href')
                    print(f'{url}:获取到列表{len(set(hrefs))}个')
                    return hrefs
            except Exception as e:
                print(f'列表页:{url}出错=>{e}')

    async def get_ips(session,url,sem):
        '''从详情页采集ip'''
        async with sem:
            ips=[]
            try:
                async with session.request('GET',url,headers=headers1) as resp:
                    resbt=await resp.read()
                    ips=pats['patIp'].findall(resbt)
                    print(f'{url}:获取到{len(ips)}个')
            except Exception as e:
                print(f'详情页:{url}出错=>{e}')
            return ips
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
        start=time.time()
        sem = asyncio.Semaphore(20)
        tasks=[asyncio.create_task(get_coturls(session,listUrl,sem)) for listUrl in listUrls]
        print('小苏正在解析列表页获取url...')
        res=await asyncio.gather(*tasks)
        for hrefs in res:
            coturls.extend([f'{host}{href}' for href in hrefs])
        end=time.time()
        print(f'小苏代理共获取{len(coturls)}个url,去除重复后剩{len(set(coturls))},耗时{end-start:.2f}s')

        print('小苏代理开始解析详情页获取ip...')
        
        await asyncio.sleep(3)

        sem2 = asyncio.Semaphore(20)
        tasks2=[asyncio.create_task(get_ips(session,url,sem2)) for url in set(coturls)]
        res2=await asyncio.gather(*tasks2)
        for v in res2:
            ips.extend(v)
        print(f'小苏代理共获取{len(ips)}个ip,去除重复后剩{len(set(ips))}个')

    print('小苏代理开始筛选有用的ip...')
    await asyncio.sleep(3)
    
    for k,v in jcdl.items():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
            start=time.time()
            sem3=asyncio.Semaphore(20)
            tasks3=[asyncio.create_task(jc_ips(session,f'dbs/{k}.db3',f'https://{v}',ip.decode('utf8'),sem3)) for ip in set(ips)]
            res3=await asyncio.gather(*tasks3)
            for v in res3:
                if v:
                    checkIps.append(v)
            print(f'小苏代理,{k}共获取{len(checkIps)}个ip,去除重复后剩{len(set(checkIps))}个')
            end=time.time()
            print(f'小苏代理,{k}筛选耗时:{end-start:.2f}')
    
    return checkIps

#89代理
async def getdl_89():

    print('正在获取89代理...')
    coturls=[f'https://www.89ip.cn/index_{j}.html' for j in range(1,128)]
    ips=[]
    checkIps=[]

    async def get_ips_89(session,url,sem):
        '''从详情页采集ip'''
        async with sem:
            ips=[]
            try:
                async with session.request('get',url,headers=headers1) as resp:
                    cot= await resp.read()
                    html=etree.HTML(cot)
                    ipandports=html.xpath('//table[@class="layui-table"]/tbody/tr/td[position()<3]/text()')
                    ips=[]
                    for j in range(0,len(ipandports)-1,2):
                        ips.append(f'{ipandports[j].strip()}:{ipandports[j+1].strip()}')
            except Exception as e:
                print(f'详情页:{url}出错=>{e}')
            return ips

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
        start=time.time()
        print('89代理开始解析详情页获取ip...')
        await asyncio.sleep(3)

        sem2 = asyncio.Semaphore(20)
        tasks2=[asyncio.create_task(get_ips_89(session,url,sem2)) for url in set(coturls)]
        res2=await asyncio.gather(*tasks2)
        for v in res2:
            ips.extend(v)
        print(f'89代理共获取{len(ips)}个ip,去除重复后剩{len(set(ips))}个')

    print('89代理开始筛选有用的ip...')
    await asyncio.sleep(3)
    
    for k,v in jcdl.items():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
            start=time.time()
            sem3=asyncio.Semaphore(20)
            tasks3=[asyncio.create_task(jc_ips(session,f'dbs/{k}.db3',f'https://{v}',ip,sem3)) for ip in set(ips)]
            res3=await asyncio.gather(*tasks3)
            for v in res3:
                if v:
                    checkIps.append(v)
            print(f'89代理,{k}共获取{len(checkIps)}个ip,去除重复后剩{len(set(checkIps))}个')
            end=time.time()
            print(f'89代理,{k}筛选耗时:{end-start:.2f}')
    
    return checkIps


#free-proxy-list.net
async def getdl_freelist():

    print('正在获取freelist...')
    coturls=[f'https://free-proxy-list.net']
    ips=[]
    checkIps=[]

    async def get_ips_qy(session,url,sem):
        '''从详情页采集ip'''
        async with sem:
            ips=[]
            try:
                async with session.request('get',url,headers=headers1) as resp:
                    cot= await resp.read()
                    html=etree.HTML(cot)
                    ipandports=html.xpath('//table[@class="table table-striped table-bordered"]/tbody/tr/td[position()<3]/text()')
                    ips=[]
                    for j in range(0,len(ipandports)-1,2):
                        ips.append(f'{ipandports[j].strip()}:{ipandports[j+1].strip()}')
            except Exception as e:
                print(f'详情页:{url}出错=>{e}')
            return ips

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
        start=time.time()
        print('freelist开始解析详情页获取ip...')
        await asyncio.sleep(3)

        sem2 = asyncio.Semaphore(20)
        tasks2=[asyncio.create_task(get_ips_qy(session,url,sem2)) for url in set(coturls)]
        res2=await asyncio.gather(*tasks2)
        for v in res2:
            ips.extend(v)
        print(f'freelist共获取{len(ips)}个ip,去除重复后剩{len(set(ips))}个')

    print('freelist开始筛选有用的ip...')
    await asyncio.sleep(3)
    
    for k,v in jcdl.items():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
            start=time.time()
            sem3=asyncio.Semaphore(20)
            tasks3=[asyncio.create_task(jc_ips(session,f'dbs/{k}.db3',f'https://{v}',ip,sem3)) for ip in set(ips)]
            res3=await asyncio.gather(*tasks3)
            for v in res3:
                if v:
                    checkIps.append(v)
            print(f'freelist,{k}共获取{len(checkIps)}个ip,去除重复后剩{len(set(checkIps))}个')
            end=time.time()
            print(f'freelist,{k}筛选耗时:{end-start:.2f}')
    
    return checkIps


#http://free-proxy.cz/
async def getdl_cz():

    print('正在获取free-proxy.cz...')
    coturls=[f'http://free-proxy.cz/zh/proxylist/country/all/http/ping/all/{j}' for j in range(1,6)]
    ips=[]
    checkIps=[]
    pat=re.compile(r'document\.write\(Base64\.decode\("(.*?)"\)\)')

    async def get_ips_cz(session,url,sem):
        '''从详情页采集ip'''
        async with sem:
            ips=[]
            try:
                async with session.request('get',url,proxy='http://127.0.0.1:1080') as resp:
                    cot= await resp.read()
                    html=etree.HTML(cot)
                    print(len(cot))
                    ipandports=html.xpath('//table[@id="proxy_list"]/tbody/tr/td[1]/script/text()|//table[@id="proxy_list"]/tbody/tr/td[2]/span/text()')
                    ips=[]
                    for j in range(0,len(ipandports)-1,2):
                        js_str=ipandports[j].strip()
                        mat=pat.search(js_str)
                        if mat:
                            ip=base64.b64decode(mat.group(1)).decode('utf-8')
                            ips.append(f'{ip}:{ipandports[j+1].strip()}')
            except Exception as e:
                print(f'详情页:{url}出错=>{e}')
            return ips

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
        start=time.time()
        print('free-proxy.cz开始解析详情页获取ip...')
        await asyncio.sleep(3)

        sem2 = asyncio.Semaphore(20)
        tasks2=[asyncio.create_task(get_ips_cz(session,url,sem2)) for url in set(coturls)]
        res2=await asyncio.gather(*tasks2)
        for v in res2:
            ips.extend(v)
        print(f'free-proxy.cz共获取{len(ips)}个ip,去除重复后剩{len(set(ips))}个')

    print('free-proxy.cz开始筛选有用的ip...')
    await asyncio.sleep(3)
    
    for k,v in jcdl.items():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
            start=time.time()
            sem3=asyncio.Semaphore(20)
            tasks3=[asyncio.create_task(jc_ips(session,f'dbs/{k}.db3',f'https://{v}',ip,sem3)) for ip in set(ips)]
            res3=await asyncio.gather(*tasks3)
            for v in res3:
                if v:
                    checkIps.append(v)
            print(f'free-proxy.cz,{k}共获取{len(checkIps)}个ip,去除重复后剩{len(set(checkIps))}个')
            end=time.time()
            print(f'free-proxy.cz,{k}筛选耗时:{end-start:.2f}')
    
    return checkIps
    
#https://spys.one/en/http-proxy-list/
async def getdl_spys():

    print('正在获取spys.one...')
    coturls=['https://spys.one/en/http-proxy-list/']
    ips=[]
    checkIps=[]
    async def get_ips_spys(session,url,sem):
        '''从详情页采集ip'''
        async with sem:
            ips=[]
            try:
                data={}
                async with session.request('post',url,headers=headers1,data=data) as resp:
                    cot= await resp.read()
                    xx0=etree.HTML(cot).xpath('//form[@action="/en/http-proxy-list/"]/td[1]/input[@name="xx0"]/@value')
                    data={
                        'xx0': xx0[0],
                        'xpp': 5,
                        'xf1': 0,
                        'xf2': 0,
                        'xf4': 0,
                        'xf5': 0
                    }
                async with session.request('post',url,headers=headers1,data=data) as resp:
                    cot= await resp.read()
                    html= etree.HTML(cot)
                    jstext= html.xpath('body/script[1]/text()')
                    ls=jstext[0].split(';')
                    mapjs={}
                    for item in ls:
                        if item:
                            lkv=item.split('=')
                            k,v=lkv[0],lkv[1]
                            if '^' in lkv[1]:
                                lwy=lkv[1].split('^')
                                v=int(lwy[0])^int(mapjs[lwy[1]])
                            mapjs[k]=v
                    lsippo=html.xpath('//tr[@class="spy1xx" or @class="spy1x"]/td[1]/font/text() | //tr[@class="spy1xx" or @class="spy1x"]/td[1]/font/script/text()')
                    lsippo=lsippo[1:]
                    l=len(lsippo)
                    pat_port=re.compile(r".*?\+(.*)\)")
                    for j in range(0,l-1,2):
                        ip_str=lsippo[j]
                        port_str=lsippo[j+1]
                        mat=pat_port.search(port_str)
                        port_str=mat.group(1)
                        lsex=port_str.split('+')
                        lsex=[item.strip('()') for item in lsex]
                        port=''
                        for item in lsex:
                            a,b=item.split('^')
                            port+=str(int(mapjs[a])^int(mapjs[b]))
                        
                        prip=f'{ip_str}:{port}'
                        ips.append(prip)
            except Exception as e:
                print(f'spys.one详情页:{url}出错=>{e}')
            return ips

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
        start=time.time()
        print('spys.one开始解析详情页获取ip...')
        await asyncio.sleep(3)

        sem2 = asyncio.Semaphore(20)
        tasks2=[asyncio.create_task(get_ips_spys(session,url,sem2)) for url in set(coturls)]
        res2=await asyncio.gather(*tasks2)
        for v in res2:
            ips.extend(v)
        print(f'spys.one共获取{len(ips)}个ip,去除重复后剩{len(set(ips))}个')

    print('spys.one开始筛选有用的ip...')
    await asyncio.sleep(3)
    
    for k,v in jcdl.items():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
            start=time.time()
            sem3=asyncio.Semaphore(20)
            tasks3=[asyncio.create_task(jc_ips(session,f'dbs/{k}.db3',f'https://{v}',ip,sem3)) for ip in set(ips)]
            res3=await asyncio.gather(*tasks3)
            for v in res3:
                if v:
                    checkIps.append(v)
            print(f'spys.one,{k}共获取{len(checkIps)}个ip,去除重复后剩{len(set(checkIps))}个')
            end=time.time()
            print(f'spys.one,{k}筛选耗时:{end-start:.2f}')
    
    return checkIps
    
#https://www.hide-my-ip.com/proxylist.shtml
async def getdl_hide():

    print('正在获取hide-my-ip...')
    coturls=['https://www.hide-my-ip.com/proxylist.shtml']
    ips=[]
    checkIps=[]
    async def get_ips_hide(session,url,sem):
        '''从详情页采集ip'''
        pat=re.compile(r'<script type="text/javascript">.*?var json =(.*?);<!-- proxylist -->'.encode('utf-8'),re.S)
        async with sem:
            ips=[]
            try:
                async with session.request('get',url,headers=headers1) as resp:
                    cot= await resp.read()
                    mat=pat.search(cot)
                    ls=json.loads(mat.group(1))
                    for item in ls:
                        i,p=item.get('i'),item.get('p')
                        ips.append(f'{i}:{p}')
            except Exception as e:
                print(f'hide-my-ip详情页:{url}出错=>{e}')
            return ips

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
        start=time.time()
        print('hide-my-ip开始解析详情页获取ip...')
        await asyncio.sleep(3)

        sem2 = asyncio.Semaphore(20)
        tasks2=[asyncio.create_task(get_ips_hide(session,url,sem2)) for url in set(coturls)]
        res2=await asyncio.gather(*tasks2)
        for v in res2:
            ips.extend(v)
        print(f'hide-my-ip共获取{len(ips)}个ip,去除重复后剩{len(set(ips))}个')

    print('hide-my-ip开始筛选有用的ip...')
    await asyncio.sleep(3)
    
    for k,v in jcdl.items():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20,ssl=False), trust_env=True) as session:
            start=time.time()
            sem3=asyncio.Semaphore(20)
            tasks3=[asyncio.create_task(jc_ips(session,f'dbs/{k}.db3',f'https://{v}',ip,sem3)) for ip in set(ips)]
            res3=await asyncio.gather(*tasks3)
            for v in res3:
                if v:
                    checkIps.append(v)
            print(f'hide-my-ip,{k}共获取{len(checkIps)}个ip,去除重复后剩{len(set(checkIps))}个')
            end=time.time()
            print(f'hide-my-ip,{k}筛选耗时:{end-start:.2f}')
    
    return checkIps


