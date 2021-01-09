#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import socket
import time
from LiveSimulator import StudentClassroom
import re
import os
import xlrd
from LiveSimulator.public.redisClient import RedisClient
import json


# 学生端基本信息
client_ip = socket.gethostbyname(socket.gethostname())
app_secret = '4911898908f9d03ae7bf913f2ae16cb1'
#app_secret = 'ea4958b53cd9da924e1223252d5d215b'
user_type = 2   # 可选值 1学生，2助教，3老师 4 监课 5 超级管理员

# 获取UID列表
uid_exec = xlrd.open_workbook(os.getcwd() + '\IdList.xlsx')
uid_sheet = uid_exec.sheet_by_index(0)
uid_rows_num = uid_sheet.nrows

if __name__ == "__main__":
    while True:
        try:
            liveID = input("请输入直播ID: ")
            group_id = int(input("请输入组ID: "))
            tea_UID = input("请输入老师ID: ")
            if liveID != "" and re.match("^[0-9]+$", str(group_id)) and re.match("^[0-9]+$", tea_UID):
                break
        except Exception as e:
            print("输入有误， 重新输入！")
            time.sleep(3)
            t = os.system('cls')

    redis_client = RedisClient('10.200.2.220', '6381')
    if uid_rows_num >= 1:
        stu_id_list = list()
        for index in range(uid_rows_num):
            stu_UID = str(uid_sheet.cell(index, 0).value)[:-2]
            stu_id_list.append(stu_UID)
            # 设置学生列表信息，并写入redis中
            double_stu_key = "zylive:enroll_student_list_contain_avatar_hash:" + liveID + ":" + str(group_id)
            stu_info = {'studentId':str(stu_UID),'studentName':"test_"+str(stu_UID),'avatar':"https://manage.test.17zuoye.net/static/img/img.2aab7b4.jpg"}
            stu_info_dict = {stu_UID:json.dumps(stu_info)}
            # print (double_stu_key)
            redis_client.hm_set(double_stu_key, stu_info_dict)
        nick_name = u"学生教室" + str(group_id)
        # 创建学生教室对象
        stuRoom_obj = StudentClassroom.StudentClassroom(liveID,tea_UID, nick_name, user_type, group_id, stu_id_list)
        stuRoom_obj.do_join()
    else:
        print ("学生uid列表为空！")