#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2021/5/11
# @Author  : Mao ZhongJie
# @File    : test
# @Description: 测试文件

from socket import timeout
from getIps import main
from requests.models import Response
from config import dlurl,pats
from header import headers1
from requests.sessions import session
from lxml import etree
import re,json,time
import asyncio,aiohttp

patip=re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,4}'.encode('utf8'))
host=dlurl['xiaosu']['host'] #小苏代理主机域名
listUrls=[dlurl['xiaosu']['listUrl'].format(j) for j in range(1,101)]
coturls=[]
ips=[]

def get_proips(sess,url):
    ips=[]
    try:
        response=sess.get(url,headers=headers1,timeout=10)
        #print(response.status_code)
        res=response.content
        t=patip.findall(res)
        ips=[v.decode('utf8') for v in t]
        print(f'{url}:获取到{len(ips)}个')
    except Exception as e:
        print(f'详情页:{url}出错=>{e}')

    return ips

def get_urls(sess,url):
    urls=[]
    try:
        response=sess.get(url,headers=headers1,timeout=10)
        html=etree.HTML(response.content)
        hrefs=html.xpath('//div[@class="title"]/a/@href')
        urls=[f'{host}{href}' for href in hrefs]
        print(f'{url}:获取到列表{len(hrefs)}个')
    except Exception as e:
        print(f'列表页:{url}出错=>{e}')

    return urls
#requsts验证
def checkip(proip):
    try:
        start=time.time()
        url='https://www.amazon.com'
        proxies = {'http':f'http://{proip}', 'https': f'http://{proip}'}
        xusession=session()
        response =xusession.get(url, headers=headers1, proxies=proxies, timeout=20)
        print(response.status_code)
        if response.status_code!=200:
            print(f'{proip}状态码错误:{response.status_code}')
            return
        if len(response.content)<=20000:
            print(f'{proip}=>内容长度错误')
            return


        with open('ips.txt','a',encoding='utf8') as f:
            end=time.time()
            longt=f'{end-start:.2f}'
            print(f'{proip}=>检测有效正在存入')
            f.write(proip+','+longt+'\n')
            print(f'消耗时间{longt}')

    except Exception as e:
        print(f'{proip}=>{e}')


def main():
    sess=session()
    print('正在解析列表页获取url...')
    start=time.time()
    for url in listUrls:
        t=get_urls(sess,url)
        coturls.extend(t)
    end=time.time()
    print(f'共获取{len(coturls)}个url,去除重复后剩{len(coturls)},耗时{end-start:.2f}s')
    time.sleep(1)

    print('正在解析详情页获取ip...')
    for url in coturls:
        t=get_proips(sess,url)
        ips.extend(t)
    print(f'共获取{len(ips)}个ip,去除重复后剩{len(set(ips))}')

if __name__=='__main__':
    start=time.time()
    main()
    end=time.time()
    print(f'程序总耗时{end-start:.2f}s')
    # for v in ips:
    #     print(f'正在检验代理ip:{v}')
    #     checkip(v)
