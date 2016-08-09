#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2016 - L.E.R
import requests
from bs4 import BeautifulSoup
import base64
import urllib
import string
#import os
#import time

DY_PAGE_URL = "http://www.dy2018.com/i/%d.html"
class Movie:
    def __init__(self):
        self.name = ""
        self.brief= ""
        self.id = 0
        self.desc = ""
        self.huaxu = ""
        self.pic = []
        self.director = ""
        self.series = ""
        self.actors = []
        self.inittime = "2000-1-1"
        self.tags = []
        self.cats = []
        self.playurl = []
        self.dldurl = []
        self.lang = []
    def __str__(self):
        return "Class Movie:\nname: %s\nbrief:%s\nid:%d\ndesc:%s\nhuaxu:%s\npic:%s\ndirector:%s\nseries:%s\nactors:%s\ninittime:%s\ntags:%s\ncats:%s\nplayurl:%s\ndldurl:%s\nlang:%s\n"%(self.name, self.brief, self.id, self.desc,self.huaxu, self.pic, self.director,self.series,self.actors,self.inittime, self.tags, self.cats, self.playurl, self.dldurl, self.lang)


class Iden:
    def __init__(self):
        self.name = "片名"
        self.tags = "类别"
        self.lang = "语言"
        self.series = "集数"
        self.director = "导演"
        self.desc = "简介"
        self.huaxu = "絮"
        self.actors = "主演"

def getWebpage(id):
    r = requests.get(DY_PAGE_URL%(id))
    r.encoding = 'gb2312'
    if (r.status_code != 200):
        return ""
    else:
        return r.text

def idenvalue(txt, iden):
    return txt[txt.find(iden)+len(iden):]

def thunderurl(url):
    linktmp = 'AA'+urllib.parse.quote(bytes(url, encoding="utf-8"))+'ZZ'
    linkfinal = str(base64.b64encode(bytes(linktmp, encoding="utf-8")),encoding="utf-8")
    return "thunder://"+linkfinal

def elim(stri, stre):
    return stri.replace(stre, "")

def processWebpage(text):
    text = elim(text, u"\u3000")#text.replace(u"\u3000", u"")
    text = elim(text, u"\xa0")#text.replace(u"\xa0", u"")
    text = elim(text, u"\xc2\xa0")#text.replace(u"\xc2\xa0", u"")
    text = elim(text, "【")#text.replace("【", "")
    text = elim(text, "】")#text.replace("】", "")
    mov = Movie()
    iden = Iden()
    startdesc = 0
    starthuaxu = 0
    startactors = 0
    soup = BeautifulSoup(text, "html.parser")

    # get brief
    #print(soup.title.string)
    brief = soup.find("div", { "class" : "title_all" })
    mov.brief = brief.text.replace("","")#soup.title.string
    mov.brief = mov.brief.replace("\\","/")
    print(mov.brief)

    # get category
    cat = soup.find("div", { "class" : "bd3l" })
    #print(cat)
    cattext = cat.text
    cattext = cattext.replace(u"\u3000",u"")
    cats = cattext.split(">")
    mov.cats.append(cats[-2].replace(u"\xa0",u""))

    #get pictures
    for pics in soup.find_all('img'):
        mov.pic.append(pics.get("src"))

    for links in soup.find_all('a'):
        if (links.get("href").find("webPlay") != -1):
            mov.playurl.append("http://www.dy2018.com"+links.get("href"))
        if (links.get("href").find("ftp") != -1):
            #print(links.get('href'))
            mov.dldurl.append(links.get('href'))

    uptime = soup.find("span",{"class":"updatetime"})
    mov.inittime = uptime.text.replace("发布时间：","")

    # get properties
    for prop in soup.find_all('p'):
        #print(prop)
        if (prop.get("style") == None):
            txt = prop.text
            if (startactors == 1):
                if (txt != " " and txt.find("◎") == -1 and txt!="&nbsp;" or len(mov.actors) == 0):
                    mov.actors.append(txt)
                    continue
                else:
                    startactors = 0
                    #print(mov.actors)
            if (startdesc == 1):
                if (txt != " " and txt.find("◎") == -1 and txt!="&nbsp;" or len(mov.desc) == 0):
                    mov.desc += txt
                    continue
                else:
                    startdesc = 0
                    #print(mov.desc)
            if (starthuaxu == 1):
                if (txt != " " and txt.find("◎") == -1 and txt != "&nbsp;" or len(mov.huaxu) == 0):
                    mov.huaxu += txt
                    continue
                else:
                    starthuaxu =0
                    #print(mov.huaxu)
            if (txt.find(iden.name) != -1):
                mov.name = idenvalue(txt, iden.name)#txt[txt.find(iden.name) + len(iden.name):]
                mov.name = elim(mov.name, "\\")
                #print(mov.name)
            if (txt.find(iden.tags) != -1):
                tagstring = idenvalue(txt, iden.tags)
                tagstring = tagstring.replace(" ","")
                tagstring = tagstring.replace(u"\xa0",u"")
                mov.tags = tagstring.split('/')
                #print(mov.tags)
            if (txt.find(iden.lang) != -1):
                langstring = idenvalue(txt, iden.lang)
                langstring = langstring.replace(" ", "")
                mov.lang = langstring.split("/")
                #print(mov.lang)
            if (txt.find(iden.director) != -1):
                mov.director = idenvalue(txt, iden.director)
                #print(mov.director)
            if (txt.find(iden.series) != -1):
                mov.series = idenvalue(txt, iden.series)
                #print(mov.series)
            if (txt.find(iden.desc) != -1):
                startdesc = 1
                #print("jianjie start")
            if (txt.find(iden.huaxu) != -1):
                starthuaxu = 1
                #print("huaxu start")
            if (txt.find(iden.actors) != -1):
                startactors = 1
                mov.actors.append(idenvalue(txt,iden.actors))
                #while (txt != " " and txt.find("◎") == -1):
    #print(mov)
    return mov

def writemd(mov):
    f = open("post/%d.md"%(mov.id), "w+")
    li = []
    li.append("```toml\n")
    li.append('title="%s"\n'%(mov.name+" - "+mov.brief))
    li.append('slug="%d"\n'%(mov.id))
    li.append('desc="%s"\n'%(mov.brief))
    li.append('date="%s"\n'%(mov.inittime))
    li.append('author="L.E.R"\n')
    li.append('categories=%s\n'%(mov.cats))
    li.append('tags=%s\n'%(mov.tags))


    li.append('```\n')
    li.append('##### 简介  \n')
    li.append('%s  \n'%(mov.desc))
    li.append('<!--more-->  \n')
    if (len(mov.dldurl) !=0):
        li.append('### 下载地址:  \n')
        for durl in mov.dldurl:
            li.append('[%s](%s)  \n'%(durl,thunderurl(durl)))
    if (len(mov.playurl) !=0):
        li.append('### 在线播放地址：  \n')
        for purl in mov.playurl:
            indstart = purl.find("collection-")
            indend = purl.find(".html")
            li.append('[第%d集](%s)  \n'%(int(purl[indstart+len("collection-"):indend])+1, purl))

    li.append('### 介绍  \n')
    li.append('##### %s\n'%(mov.name))
    li.append('##### 海报/截图  \n')
    for img in mov.pic:
        li.append("![Dydy.cf Picture](%s)  \n"%(img))
    li.append('##### 主演  \n')
    for act in mov.actors:
        li.append('%s  \n'%(act))
    li.append('##### 导演  \n')
    li.append('%s  \n'%(mov.director))
    li.append('##### 语言  \n')
    for lang in mov.lang:
        li.append("%s  \n"%(lang))
    if (mov.series != ""): 
        li.append("##### 集数  \n")
        li.append("%s  \n"%(mov.series))
    li.append("##### 标签分类  \n###### ")
    for tags in mov.tags:
        li.append("%s "%(tags))
    li.append("\n")

    li.append('##### 信息原地址  \n')
    li.append("[电影天堂](http://www.dy2018.com/i/%d.html)  \n"%(mov.id))
    f.writelines(li)
    f.close()

for i in range(96260, 97200):#(97065, 97066):
    print(i)
    page = getWebpage(i)
    if (page == ""):
        continue
    mov = processWebpage(page)
    mov.id = i
    writemd(mov)

#i = 97065

#mov = processWebpage(getWebpage(i))
#mov.id = i
#print(mov)
#writemd(mov)
