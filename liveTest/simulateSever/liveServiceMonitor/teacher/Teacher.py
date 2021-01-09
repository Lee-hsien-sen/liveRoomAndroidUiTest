#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import socket
import time
import sys
a=sys.path
print(a)
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2, kodec_pb2
from commons.liveServiceMonitor.logical_teach import TChatClass
from commons.liveServiceMonitor.logical_teach import TChatControlClass
from commons.liveServiceMonitor.logical_teach import TContestClass
from commons.liveServiceMonitor.logical_teach import TCoursewareClass
from commons.liveServiceMonitor.logical_teach import TJoinRoom
from commons.liveServiceMonitor.logical_teach import TLeaveClass
from commons.liveServiceMonitor.logical_teach import TNoticeClass
from commons.liveServiceMonitor.logical_teach import TReadSentenceClass
from commons.liveServiceMonitor.logical_teach import TRewardClass
from commons.liveServiceMonitor.logical_teach import TUserListClass
from commons.liveServiceMonitor.logical_teach import TVoiceReadClass
from commons.liveServiceMonitor.logical_teach import TVoteClass
import struct
import gzip
import threading
from bitarray import bitarray
import requests
import os
import configparser
import logging
import random
import re
from commons.liveServiceMonitor.public import globalvar

# 老师端基本信息
client_ip = socket.gethostbyname(socket.gethostname())

# 测试环境常量
app_id = '58eee6ac19b005fec0d848ce'
app_secret = '4911898908f9d03ae7bf913f2ae16cb1'

# 正式环境
# app_id = '59a91c3237d3d8d28516801c'
# app_secret = 'ea4958b53cd9da924e1223252d5d215b'


## 云测ID 5bebc26259b69e218e69e084
#liveID = '5d514c783b819c4dd66ca51a'
## 互动课件用  5d5bb4c17325e851d2dcc194
## 5df98e6c1b213d1b8c7d053e
#liveID = '5bebc26259b69e218e69e084'

roomID = 34361
# tea_UID = "12976231"
# tea_UID = "8"
nickname = "直播测试"
user_type = 3 # 可选值 1学生，2助教，3老师 4 监课 5 超级管理员
join_token = ""
isForbidden = False
chatDisabled = False
groupChatDisabled = False
onlineNum = 0
msn_ip="10.200.241.44"
#初始化Config对象，读取ini配置文件
# conf = configparser.ConfigParser()
# conf.read(os.getcwd() + '\config.ini')
# setting = int(conf.get("switch", "setting"))
# # 测试环境
# if setting == 1:
#     app_id = conf.get("switch", "app_id_test")
#     app_secret = conf.get("switch", "app_secret_test")
#     msn_ip = conf.get("msn", "test_ip")
#     #print (msn_ip)
# # 开发环境
# elif setting == 3:
#     app_id = conf.get("switch", "app_id_test")
#     app_secret = conf.get("switch", "app_secret_test")
#     #msn_ip = conf.get("msn", "debug_ip")
# # 正式环境
# elif setting == 2:
#     app_id = conf.get("switch", "app_id_prod")
#     app_secret = conf.get("switch", "app_secret_prod")

def getMsnIp():
    url = "http://118.178.171.60:36666/dns"
    payload = {'q': 'msn.17zuoye.com', 'uid': '43.227.252.50', 'output': 'json'}
    try:
        r = requests.request("GET", url, params = payload)
        if r.status_code == 200:
            httpdns_Res = r.json()
            if len(httpdns_Res['addressList']) != 0:
                msnIpList = httpdns_Res['addressList']
                return msnIpList
            else:
                print (u"MSN地址返回为空")
                return httpdns_Res['addressList']
        else:
            print (u"Json消息返回失败")
    except Exception as err:
            print(err)

class Teacher(object):
    def __init__(self, liveId, userId, user_type, nickName, roomIndex, msn_ip):
        self.liveId = liveId
        self.userId = userId
        self.userType = user_type
        self.nickName = nickName
        self.roomIndex = roomIndex
        # 设置连接的msnip
        self.msn_ip = msn_ip
        self.event = threading.Event()
        self.isLogin = False
        self.token = ""

        # 创建joinRoom对象
        self.joinObj = TJoinRoom.JoinRoom(self.liveId, self.userId, self.nickName, self.userType, self.roomIndex,
                                             app_id, app_secret)
        # self.joinReqMessage = self.joinObj.pack_joinReq()
        # 创建获取用户列表对象
        self.userListObj = TUserListClass.UserListClass(self.userId)
        # 创建老师聊天对象
        self.teaChat = TChatClass.ChatClass(self.userId, self.roomIndex, self.joinObj.join_token)
        # 创建抢答题对象
        self.contestObj = TContestClass.ContestClass(self.userId)
        # 创建答题器对象
        self.voteObj = TVoteClass.VoteClass(self.userId)
        # 创建语音题对象
        self.voiceObj = TVoiceReadClass.VoiceReadClass(self.userId)
        # 创建朗读题对象
        self.readSentenceObj = TReadSentenceClass.ReadSentenceClass(self.userId)
        # 创建发送奖励对象
        self.rewardObj = TRewardClass.RewardClass(self.userId)
        # 创建公告对象
        self.noticeObj = TNoticeClass.NoticeClass(self.userId)
        # 创建聊天开关对象
        self.controlObj = TChatControlClass.ChatControlClass(self.userId)
        # 创建互动课件逻辑对象
        self.coursewareObj = TCoursewareClass.CoursewareClass(self.userId)

    # 接收socket数据
    def readSockData(self, event):
        try:
            while True:
                # 每次先读取4个字节
                size = 4
                dataLen = self.sock.recv(size)
                if dataLen:
                    size = struct.unpack('!I', dataLen)[0]
                    dataPack = b''
                    # 按照size大小完整读取数据包，再解析
                    while len(dataPack) < size:
                        packet = self.sock.recv(size - len(dataPack))
                        if not packet:
                            pass
                        dataPack += packet
                    self.dataParser(dataPack, size)
                else:
                    self.sock.close()
                    break
        except Exception as e:
            print("老师已断开长连接：", e)

    # 收取数据包解包函数
    def dataParser(self, data, data_len):
        # 将数据初始化为字节数组
        dataArray = bytearray(data)

        body = dataArray[2: data_len + 2]
        HeadByte = bitarray()
        HeadByte.frombytes((dataArray[0].to_bytes(1, byteorder='little')))

        dataType = HeadByte[1:4]  # 取出第一个字节的2到3bit位

        # 判断消息体是否需要解压缩
        MsgBody = b''
        if (HeadByte[0] == 0):
            # 不需要解压缩
            MsgBody = body
        elif (HeadByte[0] == 1):
            # 需要解压缩处理
            MsgBody = gzip.decompress(body)

        # 判断消息的类型，分别处理
        message = b''
        if dataType == bitarray('000'):
            message = logical_pb2.ResponsePackage()
            message.ParseFromString(MsgBody)
        elif dataType == bitarray('001'):
            message = kodec_pb2.Cmd()
            message.ParseFromString(MsgBody)
        elif dataType == bitarray('010'):
            message = kodec_pb2.Ack()
            message.ParseFromString(MsgBody)
        else:
            print("不支持消息类型")
        logicData = {'bagId': dataType, 'bagData': message}
        self.messageHandling(logicData)

        return {'bagId': dataType, 'bagData': message}

    # 消息归类&引导处理函数
    def messageHandling(self, LogicData):
        global onlineNum
        if LogicData["bagId"] == bitarray('001'):  # Cmd包
            # 处理心跳返回
            if LogicData["bagData"].tp == LogicData["bagData"].PONG:
                HeartContent = LogicData["bagData"].Pong()
                HeartContent.ParseFromString(LogicData["bagData"].d)
                # 赋值在线人数
                self.online_number = HeartContent.userSize
                if onlineNum != HeartContent.userSize:
                    onlineNum = HeartContent.userSize
                    print(u"在线人数:", onlineNum)
            elif LogicData["bagData"].tp == LogicData["bagData"].KICK:
                KickMsg = LogicData["bagData"].Kick()
                KickMsg.ParseFromString(LogicData["bagData"].d)
                print(u"被踢uid: ", KickMsg.userId)
                print(u"被踢的原因：", KickMsg.reason)
            # 处理主动离线
            elif LogicData["bagData"].tp == LogicData["bagData"].LEAVEROOM:
                print(u"学生主动退出: ", self.userId)
        elif LogicData["bagId"] == bitarray('010'):  # Ack包
            # print(u"发送成功收到ACK：", LogicData["bagData"].id)
            pass
        elif LogicData["bagId"] == bitarray('000'):  # 逻辑数据包
            resMsg = LogicData["bagData"]
            self.doLogical(resMsg)

    # 逻辑服务分发函数
    def doLogical(self, resMsg):
        # 处理加入直播间
        if resMsg.head_frame.msg_type in [msg_type_pb2.JOIN_ROOM_RES, msg_type_pb2.RE_JOIN_RES]:
            self.token = self.joinObj.joinLogic(resMsg)
            # 判断token是否不空
            if self.token:
                # 设置登录成功
                self.isLogin = True
                self.isForbidden = self.joinObj.isForbidden
                self.chatDisabled = self.joinObj.chatDisabled
                self.groupChatDisabled = self.joinObj.groupChatDisabled
                # 开启心跳线程
                self.heartThread = threading.Thread(target=self.heartLink, args=(), name='Thread-heart')
                self.heartThread.start()

                # 开始获取直播配置信息
                self.do_getLiveconfig()

        # 获取用户列表逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.GET_USER_LIST_RES]:

            self.userListObj.getuserlistLogic(resMsg)
        # 获取直播配置信息
        elif resMsg.head_frame.msg_type in [msg_type_pb2.GET_LIVE_CONFIG_RES]:
            self.joinObj.joinLogic(resMsg)
            self.reactive_host = self.joinObj.live_config.reactive_host
            #print (self.reactive_host)
            self.stream_items = self.joinObj.live_config.stream_items
            self.cdn_upload_file_host = self.joinObj.live_config.cdn_upload_file_host
            self.is_assistant_stage_enabled = self.joinObj.live_config.is_assistant_stage_enabled
            self.examination_teacher_web = self.joinObj.live_config.examination_teacher_web
            self.examination_asistant_web = self.joinObj.live_config.examination_asistant_web
            self.examination_student_web = self.joinObj.live_config.examination_student_web
            self.reactive_frames_url = self.joinObj.live_config.reactive_frames_url

        # 处理聊天逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.STUDENT_CHAT_RES, msg_type_pb2.STUDENT_CHAT_BROADCAST,
                                            msg_type_pb2.CHAT_RES, msg_type_pb2.CHAT_BROADCAST]:

            self.teaChat.chatLogic(resMsg)

        # 处理答题投票逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.VOTE_START_RES, msg_type_pb2.VOTE_STOP_RES,
                                            msg_type_pb2.VOTE_START_BROADCAST,
                                            msg_type_pb2.VOTE_START_NEW_BROADCAST,
                                            msg_type_pb2.VOTE_STOP_BROADCAST, msg_type_pb2.SUBMIT_VOTE_RES,
                                            msg_type_pb2.VOTE_NO_FINISH_P2P]:
            self.voteObj.voteLogic(resMsg)

        ### 处理语音答题逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.VOICE_READ_START_RES, msg_type_pb2.VOICE_READ_STOP_RES,
                                            msg_type_pb2.VOICE_READ_QUERY_RES,
                                            msg_type_pb2.VOICE_READ_START_BROADCAST,
                                            msg_type_pb2.VOICE_NO_FINISH_P2P,
                                            msg_type_pb2.VOICE_READ_STOP_BROADCAST,
                                            msg_type_pb2.VOICE_READ_REPORT_RES]:

            self.voiceObj.voiceLogic(resMsg)

        ### 处理朗读题逻辑 ###
        elif resMsg.head_frame.msg_type in [msg_type_pb2.READ_SENTENCE_START_RES,
                                            msg_type_pb2.READ_SENTENCE_STOP_RES,
                                            msg_type_pb2.READ_SENTENCE_QUERY_RES,
                                            msg_type_pb2.READ_SENTENCE_STOP_BROADCAST]:

            self.readSentenceObj.readLogic(resMsg)

        ### 处理抢答题逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.OPEN_CONTEST_RES, msg_type_pb2.CLOSE_CONTEST_RES,
                                            msg_type_pb2.OPEN_CONTEST_BROADCAST,
                                            msg_type_pb2.SUBMIT_CONTEST_BROADCAST,
                                            msg_type_pb2.CLOSE_CONTEST_BROADCAST]:

            self.contestObj.contestLogic(resMsg)

        ### 处理奖励逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.REWARD_EVERYONE_RES,
                                            msg_type_pb2.REWARD_EVERYONE_BROADCAST]:
            self.rewardObj.rewardLogic(resMsg)

        ### 处理公告逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.NOTICE_PUBLISH_RES,
                                            msg_type_pb2.NOTICE_DELETE_RES]:

            self.noticeObj.noticeLogic(resMsg)

        ### 处理关闭聊天及禁言逻辑
        elif resMsg.head_frame.msg_type in [msg_type_pb2.CHAT_CONTROL_RES]:

            self.controlObj.chatcontrolLogic(resMsg)

        ### 更改直播状态
        elif resMsg.head_frame.msg_type in [msg_type_pb2.LIVE_STATUS_CHANGE_RES,
                                            msg_type_pb2.LIVE_STATUS_CHANGE_BROADCAST]:
            pass

        ### 处理互动课件
        elif resMsg.head_frame.msg_type in [msg_type_pb2.COURSEWARE_CONFIG_RES,
                                            msg_type_pb2.COURSEWARE_EXERCISE_START_RES,
                                            msg_type_pb2.COURSEWARE_EXERCISE_STOP_RES]:
            self.coursewareObj.coursewareExerciselogic(resMsg)
        else:
            print("其他代码：", resMsg.head_frame.msg_type, resMsg.result_frame.code, resMsg.result_frame.msg)

    # 心跳函数
    def heartLink(self):
        try:
            while self.isLogin:
                # 构造心跳包
                heartPack = kodec_pb2.Cmd()
                heartPack.tp = kodec_pb2.Cmd.PING
                heartPack.ct = int(time.time() * 1000)
                ####
                msg_ping = heartPack.Ping()
                msg_ping.groupId = str(self.roomIndex)
                heartPack.d = msg_ping.SerializeToString()

                heartMsg_len = heartPack.ByteSize() + 2
                heartMsg_flag = int('0x1000', 16)
                heartMsg = heartPack.SerializeToString()
                heartBeat = struct.pack('!IH', heartMsg_len, heartMsg_flag) + heartMsg
                self.sock.sendall(heartBeat)
                time.sleep(15)
        except Exception as err:
            print(u"心跳链接出错：", err)

    # 加入房间
    def do_join(self):
        try:
            # 创建新的tcp socket连接
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            # 与MSN建立连接
            if self.sock.connect_ex((self.msn_ip, 8114)) == 0:
                self.sock.getpeername()
                print("老师连接成功", self.sock.getpeername())
                # 启动接收socket数据线程
                self.readThread = threading.Thread(target=self.readSockData, args=(self.event,), name='Thread-read')
                self.readThread.start()
                # 构造加入房间请求包
                self.joinReqMessage = self.joinObj.pack_joinReq()
                # 发送加入房间请求
                self.sock.sendall(self.joinReqMessage)
                # 设置老师加入房间请求时间戳
                self.joinObj.join_req_time = int(time.time()*1000)
                # 设置响应时间间隔为0，以判断是否无响应
                self.joinObj.join_duration = 0
            else:
                print("老师连接失败", self.sock.getpeername())
        except Exception as err:
            print(err)

    # 重新加入房间
    def do_rejoin(self):
        try:
            self.sock.close()
            # 设置登录状态为False
            self.isLogin = False
            # 等待读数据和心跳线程退出
            self.heartThread.join()
            self.readThread.join()
            # 初始化新的socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            if self.sock.connect_ex((self.msn_ip, 8114)) == 0:
                print("老师重连成功", self.sock.getpeername())
                time.sleep(2)
                self.readThread = threading.Thread(target=self.readSockData, args=(self.event,), name='Thread-read')
                self.readThread.start()
                # 重新加入房间
                self.rejoin_msg = self.joinObj.pack_rejoin(self.token)
                self.sock.sendall(self.rejoin_msg)
                # self.event.set()
                # 设置重新加入房间请求开始时间戳
                self.joinObj.rejoin_req_time = int(time.time() * 1000)
                # 设置响应时间间隔为0，以判断是否无响应
                self.joinObj.rejoin_duration = 0
        except Exception as err:
            print(err)

    # 离开房间
    def do_leave(self):
        # 构造leaveRoom cmd包
        leavePack = kodec_pb2.Cmd()
        leavePack.tp = kodec_pb2.Cmd.LEAVEROOM
        leavePack.ct = int(time.time() * 1000)

        Msg_len = leavePack.ByteSize() + 2
        Msg_flag = int('0x1000', 16)
        LeaveMsg = leavePack.SerializeToString()
        leaveReq = struct.pack('!IH', Msg_len, Msg_flag) + LeaveMsg
        self.sock.sendall(leaveReq)
        print ("老师发起离开教室",self.userId)
        self.isLogin = False
        self.heartThread.join()
        self.readThread.join()

    # 更改直播状态
    def do_changeStatus(self, liveStatus):
        changeMsg = self.joinObj.pack_statusChange(self.joinObj.join_token, liveStatus)
        self.sock.sendall(changeMsg)

    # 获取直播配置
    def do_getLiveconfig(self):
        get_live_config_msg = self.joinObj.pack_getLiveconfig(self.token)
        self.sock.sendall(get_live_config_msg)

    # 聊天
    def do_chat(self):
        if self.isLogin == True:
            if (self.joinObj.isForbidden == False) and (self.joinObj.chatDisabled == False) and (
                    self.joinObj.groupChatDisabled == False):
                self.teaChat.content = "6666"
                chatMsg = self.teaChat.pack_teaChat(self.token)
                self.sock.sendall(chatMsg)
            else:
                print("当前已开启禁言")

    ### 发起及结束抢答
    def do_contest(self):
        startMsg = self.contestObj.pack_startContest(self.joinObj.join_token)
        self.sock.sendall(startMsg)
        time.sleep(10)
        stopMsg = self.contestObj.pack_stopContest(self.joinObj.join_token)
        self.sock.sendall(stopMsg)

    ### 发起答题及结束答题
    def do_vote(self, voteType, interval):
        voteStartMsg = self.voteObj.pack_voteStart(self.joinObj.join_token, voteType)
        self.sock.sendall(voteStartMsg)
        # 设置发起时间
        self.voteObj.start_req_time = int(round(time.time() * 1000))
        # 设置响应时间间隔为0，以判断是否无响应
        self.voteObj.vote_start_duration = 0
        #print("###发题开始时间###：", self.voteObj.start_req_time)
        # 设置等待间隔
        if isinstance(interval,int):
            time.sleep(interval)
            self.stop_vote()
        else:
            pass

    def stop_vote(self):
        voteStopMsg = self.voteObj.pack_voteStop(self.joinObj.join_token, self.voteObj.questionId)
        self.sock.sendall(voteStopMsg)
        # 设置结束时间
        self.voteObj.stop_req_time = int(round(time.time() * 1000))
        # 设置结束响应时间间隔为0，以判断是否无响应
        self.voteObj.vote_stop_duration = 0
        #print("###结束答题时间###：", self.voteObj.stop_req_time)

    ### 发起语音题及结束语音题
    def do_voiceRead(self, sampleText):
        voiceStartMsg = self.voiceObj.pack_VoiceStart(self.joinObj.join_token, sampleText)
        self.sock.sendall(voiceStartMsg)
        time.sleep(25)
        ### 查询语音答题统计
        # print ("#########语音答题统计开始########")
        # for level in range(1, 6):
        #     queryMsg = self.voiceObj.pack_VoiceQuery(self.joinObj.join_token, level)
        #     self.sock.sendall(queryMsg)
        #     time.sleep(1)
        voiceStopMsg = self.voiceObj.pack_VoiceStop(self.joinObj.join_token)
        self.sock.sendall(voiceStopMsg)
        time.sleep(5)


    ### 发起朗读题及结束朗读题
    def do_readSentence(self, text, max_record_time):
        readStartMsg = self.readSentenceObj.pack_startRead(self.joinObj.join_token, text, max_record_time)
        self.sock.sendall(readStartMsg)
        time.sleep(40)
        ### 轮询朗读题结果
        print("#########轮询朗读题结果########")
        read_query_msg = self.readSentenceObj.pack_readQuery(self.joinObj.join_token)
        self.sock.sendall(read_query_msg)
        time.sleep(5)
        readStopMsg = self.readSentenceObj.pack_stopRead(self.joinObj.join_token)
        self.sock.sendall(readStopMsg)

    ### 发全体奖励或单体奖励
    def do_reward(self, min, max):
        rewardEveryoneMsg = self.rewardObj.pack_rewardEveryone(self.joinObj.join_token, min, max)
        self.sock.sendall(rewardEveryoneMsg)
        time.sleep(5)

    ### 公告
    def do_notice(self, notice_content, notice_url):
        noticePublishMsg = self.noticeObj.pack_publishNotice(self.joinObj.join_token, notice_content, notice_url)
        self.sock.sendall(noticePublishMsg)
        # time.sleep(60)
        # noticeDeleteMsg = noticeObj.pack_deleteNotice(self.joinObj.join_token)
        # self.sock.sendall(noticeDeleteMsg)

    ### 获取用户信息列表
    def do_getuserList(self, page_num, page_size):
        userlistMsg = self.userListObj.pack_getuserList(self.joinObj.join_token, page_num, page_size)
        self.sock.sendall(userlistMsg)
        time.sleep(2)

    ### 关闭或开启聊天
    def do_chatOnoff(self):
        chatOnoff_msg = self.controlObj.pack_chatOnoff(self.joinObj.join_token)
        self.sock.sendall(chatOnoff_msg)
        time.sleep(2)

    ### 互动课件
    def do_coursewareExercise(self):
        courseware_config_msg = self.coursewareObj.pack_coursewareConfigReq(self.joinObj.join_token)
        self.sock.sendall(courseware_config_msg)
        time.sleep(3)
        for courseware_config in self.coursewareObj.current_used_config_info:
            for page_index in range(0, courseware_config.page_count):
                if courseware_config.page_list[page_index].has_question == True:
                    courseware_id = courseware_config.courseware_id
                    courseware_url = self.reactive_host + courseware_config.base_url + \
                                     courseware_config.page_list[page_index].page_name + '/' + 'index.html'
                    questions_count = courseware_config.page_list[page_index].question_count
                    courseware_questions = courseware_config.page_list[page_index].courseware_questions
                    page_num = page_index + 1
                    countdown_seconds = random.randint(1,300)
                    print (courseware_id)
                    print (courseware_url)
                    print (self.online_number)
                    print (courseware_questions)
                    print (page_num)
                    courseware_exercise_start = self.coursewareObj.pack_CoursewareExerciseStart(self.token,
                                                                                                courseware_id,
                                                                                                courseware_url,
                                                                                                questions_count,
                                                                                                self.online_number,
                                                                                                courseware_questions,
                                                                                                page_num,
                                                                                                countdown_seconds)
                    self.sock.sendall(courseware_exercise_start)
                    time.sleep(40)
                    self.courseware_exercise_id = self.coursewareObj.courseware_exercise_id
                    # 结束互动题
                    courseware_exercise_stop = self.coursewareObj.pack_CoursewareExerciseStop(self.token,
                                                                                              self.courseware_exercise_id)
                    self.sock.sendall(courseware_exercise_stop)
                    time.sleep(3)

    ### 云测语音
    def cloudTest_voice(self, sampleText):
        while self.isLogin:
            try:
                for text in sampleText:
                    voiceStartMsg = self.voiceObj.pack_VoiceStart(self.token, text)
                    self.sock.sendall(voiceStartMsg)
                    time.sleep(29)
                    voiceStopMsg = self.voiceObj.pack_VoiceStop(self.token)
                    self.sock.sendall(voiceStopMsg)
                    time.sleep(1)
            except Exception as err:
                print ("cloudTest:",err)
                break


if __name__ == '__main__':
    while True:
        try:
            # liveID = input("请输入直播ID: ")
            # tea_UID = input("请输入老师ID: ")
            liveID="5f51b59fd11c7b447c8ed8f1"
            tea_UID="123"
            if re.match("^[0-9a-z]+$", liveID) and re.match("^[0-9a-z]+$", tea_UID):
                break
        except Exception as e:
            print("输入有误， 重新输入！")
            time.sleep(3)
            t = os.system('cls')

    # 创建老师对象
    teacher_a = Teacher(liveID, tea_UID, user_type, nickname, roomID,msn_ip)
    # sampleText1 = "ear dressers"
    # sampleText2 = "playground"
    # sampleText3 = "washed the dishes"
    # sampleText4 = "snowy"
    # sampleText5 = "chocolate"
    # sampleText6 = "Colour it blue."
    # sampleText7 = "Did you do anything else?"
    # sampleText8 = "Everyone stars laughing because Matt's costume's so funny."
    # sampleText9 = "He is excited to play in the snow."
    # sampleText10= "Is there a library in your school? Yes, there is. No, there isn't.On the farm, it is time for bed.She often plants flowers in the garden."
    # sampleTextList = [sampleText1, sampleText2, sampleText3, sampleText4, sampleText5,
    #                   sampleText6, sampleText7, sampleText8, sampleText9, sampleText10]

    try:
        globalvar._init()
        globalvar.set_value(tea_UID, {'uid': tea_UID,'user_type':3,'msn_ip':msn_ip})
        teacher_a.do_join()
        time.sleep(2)
        ## 发送老师聊天
        # teacher_a.do_chat()
        ## 开始上课

        teacher_a.do_changeStatus(logical_pb2.LIVE_STATUS_START)
            #
        for i in range(40):    
            teacher_a.do_vote(logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE,3)
            time.sleep(3)

        # 启动云测发语音线程
        # sampleText = "Hi David, Guess what? I'm writing to you from Beijing! It's my first summer holiday abroad and here I am, in China! I'm going to learn Chinese for two weeks at a summer camp. Then my parents are going to join me here. We're going on a tour around the country. It's going to be exciting! We're going to visit the Great Wall and the Palace Museum in Beijing. Then we're going to be in Xi'an form July twenty fourth to twenty seventh. My dad says he's going to take lots of photos of the Terracotta Warriors. After that, we're going to Jiuzhaigou. It's famous for its beautiful mountains and clear lakes. Our last stop on the trip is Sanya. My mum's going to spend a lot of time on the beach, but, I'm going to swim in the sea every day. I hope we will have a good time."
        # cloud_test = threading.Thread(target=teacher_a.cloudTest_voice, args=(sampleTextList,),
        #                               name='Thread_cloud_test')
        # cloud_test.start()
        time.sleep(10)
        # ## 下课
        # teacher_a.do_changeStatus(logical_pb2.LIVE_STATUS_STOP)
        teacher_a.do_leave()
        # # 等待云测线程退出
        # cloud_test.join()
    except Exception as err:
        print("主线程:", err)
        teacher_a.isLogin = False
    # teacher_a.do_coursewareExercise()

    # sampleText = "Hi David, Guess what? I'm writing to you from Beijing! It's my first summer holiday abroad and here I am, in China! I'm going to learn Chinese for two weeks at a summer camp. Then my parents are going to join me here. We're going on a tour around the country. It's going to be exciting! We're going to visit the Great Wall and the Palace Museum in Beijing. Then we're going to be in Xi'an form July twenty fourth to twenty seventh. My dad says he's going to take lots of photos of the Terracotta Warriors. After that, we're going to Jiuzhaigou. It's famous for its beautiful mountains and clear lakes. Our last stop on the trip is Sanya. My mum's going to spend a lot of time on the beach, but, I'm going to swim in the sea every day. I hope we will have a good time."
    # while True:
    #     teacher_a.do_voiceRead(sampleText)

    ## 投票答题
    # teacher_a.do_vote(logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE)
    # time.sleep(1)
    ## 循环发送答题
    # while True:
    #     teacher_a.do_vote(logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE)
    #     time.sleep(3)

    ## 创建获取用户列表对象
    # userListObj = TeacherLogic.userListClass(tea_UID)
    # page_num = 1
    # page_size = 15
    # tea1.do_getuserList(userListObj, page_num, page_size)
    # time.sleep(60)
    # ## 下课
    # tea1.do_changeStatus(logical_pb2.LIVE_STATUS_STOP)
    ## 创建公告对象
    # noticeObj = TeacherLogic.noticeClass(tea1.userId)
    # notice_content = u"测试公告测试公告测试公告测试公告测试公告测试公告测试公告测试公告测试公告测试公告"
    # notice_link = "http://www.163.com"
    # tea1.do_notice(noticeObj, notice_content, notice_link)

    ## 创建聊天控制对象
    # chatcontrolObj = TeacherLogic.chatcontrolClass(tea1.userId)
    # chatcontrolObj.operation = 1
    # tea1.do_chatOnoff(chatcontrolObj)
    # time.sleep(15)
    # chatcontrolObj.operation = 0
    # tea1.do_chatOnoff(chatcontrolObj)

    ## 创建抢答题对象
    # contestObj = TeacherLogic.contestClass(tea1.userId)
    # tea1.do_contest(contestObj)

    # tea1.do_vote(voteObj, logical_pb2.SIGNLE_RIGHT_MULTIPLE_CHOICE)
    # time.sleep(1)
    # tea1.do_vote(voteObj, logical_pb2.MULTIPLE_CHOICE)
    # time.sleep(1)
    # tea1.do_vote(voteObj, logical_pb2.NO_RIGHT_CHOICE)
    # time.sleep(1)
    # tea1.do_vote(voteObj, logical_pb2.NO_RIGHT_CHOICE_MULTI)
    # time.sleep(1)
    # tea1.do_vote(voteObj, logical_pb2.NO_RIGHT_SURVEY)
    # time.sleep(1)
    #
    # ## 创建语音打分题对象
    # voiceObj = TeacherLogic.voiceReadClass(tea1.userId)
    # sampleText = "Never underestimate your power to change yourself!!"
    # sampleText = "Hi David, Guess what? I'm writing to you from Beijing! It's my first summer holiday abroad and here I am, in China! I'm going to learn Chinese for two weeks at a summer camp. Then my parents are going to join me here. We're going on a tour around the country. It's going to be exciting! We're going to visit the Great Wall and the Palace Museum in Beijing. Then we're going to be in Xi'an form July twenty fourth to twenty seventh. My dad says he's going to take lots of photos of the Terracotta Warriors. After that, we're going to Jiuzhaigou. It's famous for its beautiful mountains and clear lakes. Our last stop on the trip is Sanya. My mum's going to spend a lot of time on the beach, but, I'm going to swim in the sea every day. I hope we will have a good time."
    # tea1.do_voiceRead(voiceObj, sampleText)
    # time.sleep(1)

    ## 创建朗读题对象
    # readSentenceObj = TeacherLogic.readSentenceClass(tea1.userId)
    # text = u"凡事应该多想几种方案，没毛病。凡事应该多想几种方案，没毛病，凡事应该多想几种方案，没毛病"
    # max_record_time = 10000  ## 毫秒
    # tea1.do_readSentence(readSentenceObj, text, max_record_time)

    ## 创建发送奖励对象
    # rewardObj = TeacherLogic.rewardClass(tea1.userId)
    # max_reward = 5
    # min_reward = 1
    # tea1.do_reward(rewardObj, min_reward, max_reward)
    # tea1.do_reward(rewardObj, min_reward, max_reward)
    # tea1.do_reward(rewardObj, min_reward, max_reward)