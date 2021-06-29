#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2021/5/12
# @Author  : Mao ZhongJie
# @File    : config.py
# @Description: 配置文件


#----------代理网址开始----------

import re

dlurl={
    #小苏代理
    'xiaosu':{
        'host':'http://www.xsdaili.cn',
        'listUrl':'http://www.xsdaili.cn/dayProxy/{0}.html',
        'deatilUrl:':'http://www.xsdaili.cn/dayProxy/ip/{0}.html'
    }
}

#----------代理网址结束----------


#----------正则表达式开始----------

pats={
    'patIp':re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,4}'.encode('utf8'))
}

#----------正则表达式结束----------

#----------检测代理的域名开始----------

jcdl={
    'amazon':'www.amazon.com',
    'google':'www.google.com'
}

#----------检测代理的域名结束----------