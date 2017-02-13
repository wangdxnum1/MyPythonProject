#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime

class TWCacheProduct:
    #初始化
    def __init__(self,pcode):
        self.pcode = pcode
        self.send_time = None


    def need_send_email(self):
        if(self.send_time == None):
            return True

        currentTime = datetime.now()
        if(currentTime - self.send_time).seconds >= 60 * 5:
            return True
        return False
