# -*- coding: utf-8 -*-
import scrapy
import json
import pymssql
import time
import urllib

class BilibiliAttention(scrapy.Spider):
    name = "bilibiliatt"
    allowed_domains = {"bilibili.com"}
    start_urls = {
        "http://space.bilibili.com/ajax/friend/GetAttentionList?mid=1"
    }
    conn = pymssql.connect(host='localhost:1433', database='bilibili')
    
    def parse(self,response):
        for i in rang(1,37272100):
            id=i
            url = "http://space.bilibili.com/ajax/friend/GetAttentionList?mid=%d"%id
            yield scrapy.Request(url,callback=self.perserve)
            
    def perserve(self,response):
        dic = json.loads(response.text)
        if( dic["status"] and dic["date"]["results"]>0):
            dt = dic["data"]
            for att in dt["list"]:
                t = time.gmtime(att["addtime"])
                cur = self.conn.cursor()
                cur.execute("INSERT INTO [bilibili].[dbo].[attention](mid,fid,uname,addtime_y,addtime_m,addtime_md,addtime_yd,addtime_wd) VALUES (%d,%d,%s,%d,%d,%d,%d,%d);"
                    %(id,att["fid"],att["uname"].encode('utf-8'),t.tm_year,t.tm_mon,t.tm_mday,t.tm_yday,t.tm_wday))
                self.conn.commit()
                cur.close()
            if dt["pages"] > 1:
                page = 2
                while(page <= dt["pages"]):
                    dt_next = urllib.request.urlopen("http://space.bilibili.com/ajax/friend/GetAttentionList?mid=%d&page=%d"%(id,page)).read()
                    js = json.loads(dt_next.decode('utf-8'))
                    dt_next = js["data"]
                    for att in dt_next["list"]:
                        t = time.gmtime(att["addtime"])
                        cur = self.conn.cursor()
                        cur.execute("INSERT INTO [bilibili].[dbo].[attention](mid,fid,uname,addtime_y,addtime_m,addtime_md,addtime_yd,addtime_wd) VALUES (%d,%d,%s,%d,%d,%d,%d,%d);"
                            %(id,att["fid"],att["uname"].encode('utf-8'),t.tm_year,t.tm_mon,t.tm_mday,t.tm_yday,t.tm_wday))
                        self.conn.commit()
                        cur.close()