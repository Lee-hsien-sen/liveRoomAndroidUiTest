# -*- coding:utf-8 -*-
# @Time : 2020/9/26  下午
# @Author: zeng.li

import unittest
import re
from datetime import datetime

from django.conf.locale import gl
from selenium.webdriver.support.ui import WebDriverWait
import time
import os

cur_path = os.path.dirname(os.path.realpath(__file__))
screenshot_path = os.path.join(os.path.dirname(cur_path),'screenshots')

class utils():
    """"底层封装方法"""

    def __init__(self):
        self.driver = None

    def find_element(self, loc):
        # 重写查找元素方法
        try:
            WebDriverWait(self.driver, 15).until(lambda driver:driver.find_element(*loc).is_displayed())
            return self.driver.find_element(*loc)
        except:
            print('%s 页面中未能找到%s 元素'%(self, loc))


    def clear_key(self,loc):
        """重写清空文本输入法"""
        time.sleep(3)
        self.find_element(loc).clear()


    def send_keys(self, loc, value):
        """重写在文本框中输入内容的方法"""
        self.clear_key(loc) # 先调用
        self.find_element(loc).send_keys(value)


    def click_button(self, loc):
        """重写点击按钮的方法"""
        self.find_element(loc).click()


    def getScreenShot(self):
        """重写截图方法"""
        self.sh_file = os.path.join(screenshot_path, '%s.png' % time.strftime('%Y_%m_%d'))
        self.driver.get_screenshot_as_file(self.sh_file)


    def get_windows_size(self):
        """获取屏幕大小"""
        windows_size = self.driver.get_window_size()
        return windows_size

    def click_id(self, loc):
        """点击元素id"""
        self.driver.find_element_by_id(loc).click()

    def click_text(self, loc):
        """点击元素text"""
        self.driver.find_element_by_link_text(loc).click()



    def wait_Actily(self, activity):
        """等待 activity"""
        self.driver.wait_activity(activity, 10)

    def getText(self, loc):
        """通过元素获取text"""
        return self.driver.find_element_by_id(loc).text


    def getSize(self):
        """获得机器屏幕大小x,y"""
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        return x, y

    def swipeup(self, t):
        """屏幕向上滑动"""
        l = self.getSize()
        x1 = int(l[0] * 0.5)
        y1 = int(l[1] * 0.75)
        y2 = int(l[1] * 0.25)
        self.driver.swipe(x1, y1, x1, y2, t)

    def swipeDown(self, t):
        """"屏幕向下滑动"""
        l = self.getSize()
        x1 = int(l[0] * 0.5)
        y1 = int(l[1] * 0.25)
        y2 = int(l[1] * 0.75)
        self.driver.swipe(x1, y1, x1, y2, t)

    def swipLeft(self, t):
        """屏幕向左滑动"""
        l = self.getSize()
        x1 = int(l[0] * 0.75)
        y1 = int(l[1] * 0.5)
        x2 = int(l[0] * 0.05)
        self.driver.swipe(x1, y1, x2, y1, t)

    def swipRight(self, t):
        """"屏幕向右滑动"""
        l = self.getSize()
        x1 = int(l[0] * 0.05)
        y1 = int(l[1] * 0.5)
        x2 = int(l[0] * 0.75)
        self.driver.swipe(x1, y1, x2, y1, t)

    # def swipe_up(self, x1, y1, x2, y2, t):
    #     """屏幕从(x1,y1)向（x2,y2）滑动"""
    #     l = self.getSize()
    #     x1 = int(l[0] * 0.05)
    #     y1 = int(l[1] * 0.5)
    #     x2 = int(l[0] * 0.75)
    #     self.driver.swipe(x1, y1, x2, y2, t)

    def cutTextLastNumberToLast(self, n, string):
        """"取字符串倒数第N个到最后"""
        l = len(string)
        return string.str[l-n, l]

    def cutTextNum(self, n, string):
        """"取字符串的前N个字符"""
        if n > len(string):
            return string
        else:
            return string.str[0, n]

    def birthChangeAge(self, string):
        """"生日转换年龄"""
        day = self.cutTextLastNumberToLast(2, string)
        month = self.cutTextNum(2, self.cutTextLastNumberToLast(5, string))
        year = self.cutTextNum(4, string)
        print("testCase:"+ year + " 年" + month + "月" + day + "日")
        if datetime.datetime.now().month > month:
            i = int(datetime.datetime.now().year) - int(year)
            return ++i - 1 + "d"
        else:
            if datetime.datetime.now().day > day:
             i = int(datetime.datetime.now().year) - int(year)
             return i - 1 + ""
            else:
                if int(datetime.datetime.now().year) < int(year):
                    i = int(datetime.datetime.now().year) - int(year)
                    return ++i - 1 + "";
                else:
                    i = int(datetime.datetime.now().year) - int(year)
                    return i - 1 + "";

