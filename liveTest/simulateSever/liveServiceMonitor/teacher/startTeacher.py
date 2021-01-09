#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import time
from kodec import msg_type_pb2, logical_pb2
from teacher import Teacher
import os
import re

user_type = 3
nickname = "test"
roomID = 1
msn_ip = "10.6.19.48"

while True:
    try:
        liveID = input("请输入直播ID: ")
        tea_UID = input("请输入老师ID: ")
        if re.match("^[0-9a-z]+$", liveID) and re.match("^[0-9a-z]+$", tea_UID):
            break
    except Exception as e:
        print("输入有误， 重新输入！")
        time.sleep(3)
        t = os.system('cls')

# 创建老师对象
teacher_a = Teacher.Teacher(liveID, tea_UID, user_type, nickname, roomID, msn_ip)
sampleText1 = "ear dressers"
sampleText2 = "playground"
sampleText3 = "washed the dishes"
sampleText4 = "snowy"
sampleText5 = "chocolate"
sampleText6 = "Colour it blue."
sampleText7 = "Did you do anything else?"
sampleText8 = "Everyone stars laughing because Matt's costume's so funny."
sampleText9 = "He is excited to play in the snow."
sampleText10 = "Is there a library in your school? Yes, there is. No, there isn't.On the farm, it is time for bed.She often plants flowers in the garden."
sampleTextList = [sampleText1, sampleText2, sampleText3, sampleText4, sampleText5,
                  sampleText6, sampleText7, sampleText8, sampleText9, sampleText10]

try:
    teacher_a.do_join()
    time.sleep(2)
    ## 发送老师聊天
    # teacher_a.do_chat()
    # 开始上课
    teacher_a.do_changeStatus(logical_pb2.LIVE_STATUS_START)
    # 投票
    teacher_a.do_vote(logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE, 60)
    # time.sleep(1)

    # 启动云测发语音线程
    # sampleText = "Hi David, Guess what? I'm writing to you from Beijing! It's my first summer holiday abroad and here I am, in China! I'm going to learn Chinese for two weeks at a summer camp. Then my parents are going to join me here. We're going on a tour around the country. It's going to be exciting! We're going to visit the Great Wall and the Palace Museum in Beijing. Then we're going to be in Xi'an form July twenty fourth to twenty seventh. My dad says he's going to take lots of photos of the Terracotta Warriors. After that, we're going to Jiuzhaigou. It's famous for its beautiful mountains and clear lakes. Our last stop on the trip is Sanya. My mum's going to spend a lot of time on the beach, but, I'm going to swim in the sea every day. I hope we will have a good time."
    # cloud_test = threading.Thread(target=teacher_a.cloudTest_voice, args=(sampleTextList,),
    #                               name='Thread_cloud_test')
    # cloud_test.start()
    time.sleep(10)
    # 下课
    # teacher_a.do_changeStatus(logical_pb2.LIVE_STATUS_STOP)
    teacher_a.do_leave()
    # # 等待云测线程退出
    # cloud_test.join()
except Exception as err:
    print("主线程:", err)
    teacher_a.isLogin = False