#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests#获取网页内容
import pymysql#数据库操作
import random
import time,re
import chardet#获取网页编码
from urllib.request import urlopen
threshold_of_article = 5  #设置的正文长度阈值

#数据库操作函数
def database(sql):
    type = sql.split(' ')[0].lower()
    conn = pymysql.connect(host='127.0.0.1', user='username', password='password', db='database_name',charset='utf8')  # 连接数据库
    cur = conn.cursor()  # 用于访问和操作数据库中的数据（一个游标，像一个指针）
    if type == 'select':
        cur.execute(sql)  # 执行操作
        result = cur.fetchall()  # 匹配所有满足的
        return result
    elif type == 'insert' or type == 'update' or type == 'delete':
        try:
            cur.execute(sql)
            conn.commit()  # 提交事务
            print("{} ok".format(type))
        except:
            # 发生错误时回滚
            print('something wrong!')
            conn.rollback()  # 回滚事务
        # 关闭数据库连接
    conn.close()

#获取编码格式
def encoding(url):
    html = urlopen(url).read()
    encode = chardet.detect(html)['encoding']
    return encode

#随机选择一个User-Agent
def get_headers():
    '''
    随机获取一个headers
    '''
    user_agents =  ["Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
                    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
                    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
                    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
                    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
                    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
                    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
                    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
                    ]

    headers = {'User-Agent':random.choice(user_agents)}
    return headers

#获取网页正文
def html2Article(html_file):

    #首先去除可能导致误差的script和css，之后再去标签
    tempResult = re.sub('<script([\s\S]*?)</script>','',html_file)
    tempResult = re.sub('<SCRIPT([\s\S]*?)</SCRIPT>', '', tempResult)
    tempResult = re.sub('<style([\s\S]*?)</style>','',tempResult)

    #去除所有的超链接及链接内容
    # tempResult = re.sub('<[Aa].+?</[Aa]>','',tempResult)
    #可跨行匹配<a></a>
    r=re.compile('<[Aa].+?</[Aa]>',re.S | re.M)
    tempResult = r.sub('',tempResult)
    #去除选择框的链接
    r = re.compile('<select.+?</select>', re.S | re.M)
    tempResult = r.sub('', tempResult)
    #去除所有的HTML标签
    tempResult = re.sub('(?is)<.*?>','',tempResult)

    #去除页脚标记
    tempResult = re.sub('.*版权所有.*', '', tempResult)
    tempResult = re.sub('.*[Cc]opy[Rr]ight.*', '', tempResult)

    # 去除强制空格及2个以上的空格（大于等于2是因为考虑到英文文本的自然空格）
    tempResult = tempResult.replace('&nbsp;', '')
    tempResult = tempResult.replace('&nbsp', '')
    tempResult = tempResult.replace('&raquo;', '')
    tempResult = tempResult.replace('  ', '')

    #去除空行
    r = re.compile(r'''^\s+$''', re.M | re.S)
    tempResult = r.sub('', tempResult)
    r = re.compile(r'''\n+''', re.M | re.S)
    tempResult = r.sub('\n', tempResult)

    #以\n为分隔符对字符串进行切片，返回列表
    tempResultArray = tempResult.split('\n')
    #print(tempResult)

    result_data = []

    #依据每行的长度判断是否为正文
    for oneLine in tempResultArray:
        if len(oneLine) > threshold_of_article:
            #print(oneLine)
            result_data.append(oneLine.strip())
    print(result_data)
    return result_data

def main():
    sql = 'select * from error_info'
    error_urls = database(sql)  # 错误信息
    for i in error_urls:
        try:
            header = get_headers()  # 获取一个随机浏览器代理
            res = requests.get(i[3], headers=header)
            res.encoding = encoding(i[3])  # 编码
            time.sleep(1)  # 睡眠1s
            if len(res.text) > 0:  # 空网页也不要
                print('{}可以正常访问，此条数据删除！'.format(i[3]))
                print('正在爬取网页详情内容！')
                text = html2Article(res.text)
                text = ' '.join(text)  # 变为字符串
                print(text)
                # 插入数据库
                sql='insert into academic_info values("{}","{}","{}","{}")'.format(i[1],i[2],i[3],text)
                database(sql)
                # 删除该条数据
                sql='delete from error_info where id_detail="{}"'.format(i[0])
                database(sql)
                print('{}此条数据已删除！'.format(i[3]))
            elif len(res.text) == 0:  # 内容为空
                print('{}网页内容为空！'.format(i[3]))
            else:  # 其他错误
                print('{} 访问错误！'.format(i[3]))
        except:
            print('异常错误！')

if __name__ == '__main__':
    main()
