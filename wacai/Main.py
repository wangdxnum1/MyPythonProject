#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import json

from collections import namedtuple
import smtplib
from email.mime.text import MIMEText
from TWCacheProduct import *
from datetime import datetime
import time;


wacai_product_url = 'https://8.wacai.com/finance/app/productByClassifyId.do?classifyId=1'
wacai_days_limit = 25

#

mailto_list=['906819823@qq.com','164766326@qq.com']
mail_host="smtp.163.com"  #设置服务器
mail_user="906819823@163.com"    #用户名
mail_pass="wzfxxx82916033"   #口令
mail_postfix="163.com"  #发件箱的后缀

task_time = 60

global_emails_product_cache = []


def get_product_by_classify_id():
    print 'url = ' + wacai_product_url
    response = requests.get(wacai_product_url)

    print 'response code = ' + str(response.status_code)

    # print response.text

    # print better_print(response.text)

    responseObj = json.loads(response.text, encoding='utf-8')
    # print type(responseObj)
    # print responseObj

    data = responseObj['data']
    # print data

    classifies = data['classifies']

    for classfiy in classifies:
        if(classfiy['classifyId']==12):
            print '过滤', classfiy['classifyName']
            continue

        print "解析", classfiy['classifyName'], '...'
        parse_products(classfiy)
    # print classifies


def parse_products(classfiy):
    products = classfiy['products']
    for product in products:
        typeId = product['type']
        if(typeId == 3):
            print product['title'], '已售罄'
            continue

        text2 = product['text2']

        number_of_days = 0

        print text2
        if(text2.find(u'-') != -1):
            print "解析期限不定的标的,例如季度宝,月薪宝"
            temp = number_of_days_str = text2[0:len(text2) - 1]
            tempArray = temp.split(u"-")
            number_of_days_str = tempArray[0]

            number_of_days = int(number_of_days_str)
        else:
            number_of_days_str = text2[0:len(text2) - 1]
            number_of_days = int(number_of_days_str)

        if(number_of_days < wacai_days_limit):
            print product['title'], '投资期限 =', text2 ,' 天数不符合要求,忽略'
        else:
            if need_send_email(product['code']):
                print product['title'],'符合你的要求,给予推荐'
                limit = u'期限' + text2

                content_array = [product['title'],limit]

                content = u' '.join(content_array)
                send_email('',content,product['code'])


def need_send_email(code):
    for p in global_emails_product_cache:
        if(p.pcode == code):
            return  p.need_send_email()
    return True;


def remark_for_email(p):
    p.send_time = datetime.now()


def send_email(sub,content,code):
    flag = False
    for to in mailto_list:
        if send_mail(to,u'挖财新标的提醒(大于25天且可买)',content,to):
            flag = True
            print "发送成功"
        else:
            print "发送失败"

    if flag:
        pp = None
        for p in global_emails_product_cache:
            if(p.pcode == code):
                pp = p

        if(pp == None):
            pp = TWCacheProduct(code)
            global_emails_product_cache.append(pp)

        remark_for_email(pp)

def send_mail(to_list,sub,content,to):
    me="王大虾"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain',_charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = to;
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False

def app_main():
    while True:
        get_product_by_classify_id()
        time.sleep(task_time)
    # d = datetime.datetime.now()
    #
    # s = datetime.datetime.now()
    #
    # deaa = (s-d).seconds
    #
    # if deaa < 0.1 :
    #     print 'haah'
    # print deaa
    # test()


# 辅助方法
def better_print(json_str):
    return json.dumps(json.loads(json_str),indent=4)


def _json_object_hook(d): return namedtuple('XObject', d.keys())(*d.values())


def json2obj(data): return json.loads(data, object_hook=_json_object_hook)


def test():
    data = '{"name": "王大虾", "hometown": {"name": "New York", "id": 123}}'
    x = json2obj(data)

    print x
    print x.name


if __name__ == '__main__':
    print ("作者:王大虾(906819823@qq.com)")
    print "开始爬取挖财标的数据"
    print '需要邮件提醒的用户:'
    for email in mailto_list:
        print(email)
    print ("发送邮件的条件:1.可买,未售罄 2.投资期限大于25天")
    print ('爬虫刷新时间: %ss'% (str(task_time)))
    app_main()