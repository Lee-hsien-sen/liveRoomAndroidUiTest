# -*- coding:utf-8 -*-
# @Time : 2020/9/26  下午
# @Author: zeng.li
import os
import re


""""读取设备 id"""
readDeviceId = list(os.popen('adb devices').readlines())
"""正则表达式匹配出 id 信息"""
deviceName = re.findall(r'^\w*\b', readDeviceId[1])[0]
print("deviceName:", deviceName)
"""读取设备系统版本号"""
deviceAndroidVersion = list(os.popen('adb shell getprop ro.build.version.release').readlines())
deviceVersion = re.findall(r'^\w*\b', deviceAndroidVersion[0])[0]
print("deviceVersion:", deviceVersion)

