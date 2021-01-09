#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import socket
import time
from student import Student
import random
import threading
import re
import os
import xlrd
from multiprocessing import Process


# 学生端基本信息
client_ip = socket.gethostbyname(socket.gethostname())
app_secret = '4911898908f9d03ae7bf913f2ae16cb1'
#app_secret = 'ea4958b53cd9da924e1223252d5d215b'


stu_UID = "257005"
tea_UID = "12976231"
user_type = 1   # 可选值 1学生，2助教，3老师 4 监课 5 超级管理员
client_list = list()

# 获取UID列表
uid_exec = xlrd.open_workbook(os.getcwd() + '\IdList.xlsx')
uid_sheet = uid_exec.sheet_by_index(0)
uid_rows_num = uid_sheet.nrows

def startchat(user_num, user_list):
    current_user = None
    while True:
        try:
            client_list = random.sample(user_list, user_num)
            for client in client_list:
                current_user = client
                # chatobj = LogicalClass.ChatClass(client.userId, client.roomIndex, client.joinObj.join_token)
                client.do_chat(client.token)
        except Exception as e:
            print("网络不稳定重连中（启动聊天）：", e)
            if not current_user.event.is_set():
                current_user.event.wait()

if __name__ == "__main__":
    while True:
        try:
            liveID = input("请输入直播ID: ")
            roomID = int(input("请输入组ID: "))
            #user_Num = int(input("输入模拟人数： "))
            #no_participation = int(input("输入不参与率(0-100)："))
            if liveID != "" and re.match("^[0-9]+$", str(roomID)):
                break
        except Exception as e:
            print("输入有误， 重新输入！")
            time.sleep(3)
            t = os.system('cls')


    group_id = str(roomID)
    login_date_time = time.strftime("%m%d%H%M%S", time.localtime())
    #no_participation_rate = round(no_participation/100, 2)
    if uid_rows_num >= 1:
        for index in range(uid_rows_num):
            stu_UID = str(uid_sheet.cell(index, 0).value)[:-2]
            #nick_name = "d" + group_id +'_' + stu_UID
            nick_name = " "
            # 创建学生端对象
            locals()['client%s' % index] = Student.Student(liveID, stu_UID, nick_name, user_type, roomID)
            # if round((index+1)/uid_rows_num, 2) <= no_participation_rate:
            #     #print (round((index+1)/user_Num, 2))
            #     locals()['client%s' % index].interaciton = False
            client_list.append(locals()['client%s' % index])

            # 对每个学生端开启do_join线程
            # locals()['p%s' % index] = Process(target=client.do_join, args=())
            # locals()['p%s' % index] = threading.Thread(target=locals()['client%s' % index].do_join, args=())
            # locals()['p%s' % index].setDaemon(True)
            # locals()['p%s' % index].start()
            locals()['client%s' % index].do_join()
            time.sleep(0.05)
            # locals()['pp%s' % index] = threading.Thread(target=locals()['client%s' % index].do_chat,
            #                                             args=(locals()['client%s' % index].joinObj.join_token,),
            #                                             name='Thread-chat' + str(index))
            # locals()['pp%s' % index].setDaemon(True)
            # locals()['pp%s' % index].start()

        # Thread_chat = threading.Thread(target=startchat,args=(random.randint(1, uid_rows_num), client_list), name='Thread-chat')
        # # Thread_chat = threading.Thread(target=startchat, args=(user_Num, client_list),
        # #                                name='Thread-chat')
        # Thread_chat.setDaemon(True)
        # Thread_chat.start()

        # ### 开启do_chat线程
        # for index in range(0, uid_rows_num):
        #     locals()['pp%s' % index] = threading.Thread(target=locals()['client%s' % index].do_chat,
        #                                                 args=(locals()['client%s' % index].joinObj.join_token,),
        #                                                 name='Thread-chat' + str(index))
        #     locals()['pp%s' % index].setDaemon(True)
        #     locals()['pp%s' % index].start()

        # time.sleep(10)
        # ### 主动退出教室
        # for index in range(0, user_Num//2):
        #     locals()['tt%s' % index] = threading.Thread(target=locals()['client%s' % index].do_leave, args=())
        #     locals()['tt%s' % index].setDaemon(True)
        #     locals()['tt%s' % index].start()
        #     locals()['tt%s' % index].join()

    else:
        print ("输入模拟人数错误！")



