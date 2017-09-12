# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: find_main_text_from_html.py
@ time: $17-9-12 上午10:45
"""
import requests
from bs4 import BeautifulSoup
import re
import chardet

def countchn(string):
    """
    计算div中文字在全部div中文字总和的比例
    :param string:
    :return:
    """
    try:
        string = string.decode('utf-8')
    except:
        print 'part of the content can not decode by utf-8'
    pattern = re.compile(u'[\u4e00-\u9fa5]+?') #\u4e00-\u9fa5  \u1100-\uFFFD
    result = re.findall(pattern, string)
    chnnum = len(result)            #list的长度即是中文的字数
    possible = chnnum/float(len(string))       #possible = 中文字数/总字数
    return (chnnum, possible)


def findtext(part):
    length = 50000000
    text = ''
    l = []
    for paragraph in part:
        chnstatus = countchn(str(paragraph))
        possible = chnstatus[1]
        if possible > 0.15:
            l.append(paragraph)
    l_t = l[:]
    #这里需要复制一下表，在新表中再次筛选，要不然会出问题，跟Python的内存机制有关
    for elements in l_t:
        chnstatus = countchn(str(elements))
        chnnum2 = chnstatus[0]
        if chnnum2 < 300:
        #最终测试结果表明300字是一个比较靠谱的标准，低于300字的正文咱也不想要了对不
            l.remove(elements)
        elif len(str(elements))<length:
            length = len(str(elements))
            paragraph_f = elements
            text += paragraph_f.text
    return text


test_url = 'http://news.sina.com.cn/gov/xlxw/2017-09-11/doc-ifykusey8177381.shtml'
page = requests.get(test_url)
# page.encoding = 'utf-8'
# content = page.content.encode().decode('utf-8')
coding = chardet.detect(page.content)['encoding']
print coding
content = page.content.decode(coding)
soup = BeautifulSoup(content,'html.parser')
div_part = soup.find_all('div')
text = findtext(div_part)
print text