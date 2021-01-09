#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2, kodec_pb2
from logical import JoinroomClass
from logical import VoteClass
from logical import VoiceReadClass
from logical import AwardClass
from logical import CoursewareClass
from logical import ChatClass
from logical import ContestClass
from logical import ExaminationClass
from logical import NobookExperimentation
from logical import PublicStageupClass
from logical import ReadSentenceClass
from logical import RewardClass
import struct
import random
import gzip
import threading
from bitarray import bitarray
import requests
from concurrent.futures import ThreadPoolExecutor
import xlrd
import os
import json
import configparser
import logging
from copy import deepcopy
#
# log_file = os.getcwd() + '\log\\record-' + time.strftime("%Y-%m-%d", time.localtime()) + '.log'
# logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

# 学生端基本信息
client_ip = socket.gethostbyname(socket.gethostname())

# 测试环境常量 #
app_id = '58eee6ac19b005fec0d848ce'
app_secret = '4911898908f9d03ae7bf913f2ae16cb1'

roomID = 1399
stu_UID = "257005"
tea_UID = "12976231"
user_type = 1  # 可选值 1学生，2助教，3老师 4 监课 5 超级管理员
join_token = ""
isForbidden = False
chatDisabled = False
groupChatDisabled = False
onlineNum = 0
msn_ip = ''
pool = ThreadPoolExecutor(50)

# 获取聊天数据列表
chat_exec = xlrd.open_workbook(os.getcwd() + '\chat.xlsx')
chat_sheet = chat_exec.sheet_by_index(0)
num_rows = chat_sheet.nrows

# 初始化Config对象，读取ini配置文件
conf = configparser.ConfigParser()
conf.read(os.getcwd() + '\config.ini')
setting = int(conf.get("switch", "setting"))
if setting == 1:
    app_id = conf.get("switch", "app_id_test")
    app_secret = conf.get("switch", "app_secret_test")
    msn_ip = conf.get("msn", "test_ip")
elif setting == 3:
    app_id = conf.get("switch", "app_id_test")
    app_secret = conf.get("switch", "app_secret_test")
    msn_ip = conf.get("msn", "debug_ip")
elif setting == 2:
    app_id = conf.get("switch", "app_id_prod")
    app_secret = conf.get("switch", "app_secret_prod")
# 华北
elif setting == 41:
    app_id = conf.get("switch", "app_id_prod")
    app_secret = conf.get("switch", "app_secret_prod")
    msn_ip = conf.get("msn", "ip_north")
# 华南
elif setting == 42:
    app_id = conf.get("switch", "app_id_prod")
    app_secret = conf.get("switch", "app_secret_prod")
    msn_ip = conf.get("msn", "ip_south")
# 华东
elif setting == 43:
    app_id = conf.get("switch", "app_id_prod")
    app_secret = conf.get("switch", "app_secret_prod")
    msn_ip = conf.get("msn", "ip_east")
# 内网
elif setting == 45:
    app_id = conf.get("switch", "app_id_prod")
    app_secret = conf.get("switch", "app_secret_prod")
    msn_ip = conf.get("msn", "ip_intranet")


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

class Student(object):
    def __init__(self, live_id, user_id, nick_name, user_type, room_index):
        self.liveId = live_id
        self.userId = user_id
        self.nickName = nick_name
        self.userType = user_type
        self.roomIndex = room_index
        self.isForbidden = False
        self.chatDisabled = False
        self.groupChatDisabled = False
        self.isLogin = False
        self.event = threading.Event()
        # 新增是否互动属性
        self.interaciton = True
        # 是否mvp
        self.is_mvp = False
        # 连对次数
        self.continue_right_num = 0

        # # 创建joinRoom对象
        # self.joinObj = LogicalClass.JoinroomClass(self.liveId, self.userId, self.nickName,
        #                                           self.userType, self.roomIndex, app_id, app_secret)
        # # 创建聊天对象
        # self.chatObj = LogicalClass.ChatClass(self.userId, self.roomIndex, self.joinObj.join_token)
        # # 创建抢答题对象
        # self.contestObj = LogicalClass.contestClass(self.userId)
        # # 创建投票&答题器对象
        # self.voteObj = LogicalClass.VoteClass(self.userId)
        # # 创建语音打分对象
        # self.voiceObj = LogicalClass.voiceReadClass(self.userId)
        # # 创建朗读题对象
        # self.readSentenceObj = LogicalClass.readSentenceClass(self.userId)
        # # 创建特殊奖励对象
        # self.awardObj = LogicalClass.AwardClass(self.userId)
        # # 创建海星奖励对象
        # self.rewardObj = LogicalClass.RewardClass(self.userId)
        # # 创建公开课上台对象
        # self.publicStageupObj = LogicalClass.PublicStageupClass(self.userId)
        # # 创建试卷答题对象
        # self.examinationobj = LogicalClass.ExaminationClass(self.userId)
        # # 创建nobook实验对象
        # self.experimentationobj = LogicalClass.NobookExperimentation(self.userId)
        # # 创建互动课件对象
        # self.coursewareObj = LogicalClass.CoursewareClass(self.userId)

        # 创建joinRoom对象
        self.joinObj = JoinroomClass.JoinroomClass(self.liveId, self.userId, self.nickName,
                                                  self.userType, self.roomIndex, app_id, app_secret)
        # 创建聊天对象
        self.chatObj = ChatClass.ChatClass(self.userId, self.roomIndex, self.joinObj.join_token)
        # 创建抢答题对象
        self.contestObj = ContestClass.ContestClass(self.userId)
        # 创建投票&答题器对象
        self.voteObj = VoteClass.VoteClass(self.userId)
        # 创建语音打分对象
        self.voiceObj = VoiceReadClass.VoiceReadClass(self.userId)
        # 创建朗读题对象
        self.readSentenceObj = ReadSentenceClass.ReadSentenceClass(self.userId)
        # 创建特殊奖励对象
        self.awardObj = AwardClass.AwardClass(self.userId)
        # 创建海星奖励对象
        self.rewardObj = RewardClass.RewardClass(self.userId)
        # 创建公开课上台对象
        self.publicStageupObj = PublicStageupClass.PublicStageupClass(self.userId)
        # 创建试卷答题对象
        self.examinationobj = ExaminationClass.ExaminationClass(self.userId)
        # 创建nobook实验对象
        self.experimentationobj = NobookExperimentation.NobookExperimentation(self.userId)
        # 创建互动课件对象
        self.coursewareObj = CoursewareClass.CoursewareClass(self.userId)

    # 客户端接收socket数据
    def readSockData(self, event):
        while True:
            try:
                # 每次先读取4个字节，解析出数据的长度，再获取对应长度的data
                size = 4
                dataLen = self.sock.recv(size)
                if dataLen:
                    size = struct.unpack('!I', dataLen)[0]
                    dataPack=b''
                    # 按照size大小完整读取数据包，再解析，逻辑服务数据会分片传输
                    while len(dataPack) < size:
                        packet = self.sock.recv(size - len(dataPack))
                        if not packet:
                            pass
                        dataPack += packet
                    self.dataParser(dataPack, size)
            except BlockingIOError as e:
                print("BlockingIOError：", e)
                break
            except BrokenPipeError as e:
                print("BrokenPipeError：", e)
                break
            except ConnectionAbortedError as e:
                print("ConnectionAbortedError：", e)
                self.isLogin = False
                self.heartThread.join()
                self.do_rejoin()
            except ConnectionRefusedError as e:
                print("ConnectionRefusedError：", e)
                break
            except ConnectionResetError as e:
                print("ConnectionResetError：", e)
                self.isLogin = False
                self.heartThread.join()
                self.do_rejoin()
            except EOFError as e:
                print("EOFError: ", e)
            except OSError as e:
                print("OSError: ", e)

    # 数据包拆分解析函数
    def dataParser(self, data, data_len):
        try:
            # 将数据初始化为字节数组
            dataArray = bytearray(data)
            # 从第3个字节开始取出并赋值body数据
            body = dataArray[2: data_len + 2]
            HeadByte = bitarray()
            HeadByte.frombytes((dataArray[0].to_bytes(1, byteorder='little')))
            dataType = HeadByte[1:4]  # 取出第一个字节的2到4bit位

            # 判断消息体是否需要解压缩
            MsgBody = b''
            if (HeadByte[0] == 0):
                # 不需要解压缩
                MsgBody = body
            elif (HeadByte[0] == 1):
                # 需要解压缩处理
                MsgBody = gzip.decompress(body)

            # 判断消息的类型，分别存放
            message = b''
            if dataType == bitarray('000'):
                message = logical_pb2.ResponsePackage()
                # 对message反序列化
                message.ParseFromString(MsgBody)
            elif dataType == bitarray('001'):
                message = kodec_pb2.Cmd()
                # 对message反序列化
                message.ParseFromString(MsgBody)
            elif dataType == bitarray('010'):
                message = kodec_pb2.Ack()
                # 对message反序列化
                message.ParseFromString(MsgBody)
            else:
                print("不支持消息类型")
            logicData = {'bagId': dataType, 'bagData': message}
            self.messageHandling(logicData)

            return {'bagId': dataType, 'bagData': message}
        except Exception as e:
            print (e)


    # 消息归类&引导处理函数
    def messageHandling(self, LogicData):
        try:
            global onlineNum
            if LogicData["bagId"] == bitarray('001'):  # Cmd包
                # 处理心跳返回
                if LogicData["bagData"].tp == LogicData["bagData"].PONG:
                    HeartContent = LogicData["bagData"].Pong()
                    HeartContent.ParseFromString(LogicData["bagData"].d)
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
        except Exception as e:
            print (e)


    # 逻辑服务分发函数
    def doLogical(self, resMsg):
        try:
            # 处理加入直播间(join & rejoin)
            if resMsg.head_frame.msg_type in [msg_type_pb2.JOIN_ROOM_RES, msg_type_pb2.RE_JOIN_RES]:
                self.token = self.joinObj.joinLogic(resMsg)
                # 设置登录成功
                if self.token:
                    self.isLogin = True
                    self.isForbidden = self.joinObj.isForbidden
                    self.chatDisabled = self.joinObj.chatDisabled
                    self.groupChatDisabled = self.joinObj.groupChatDisabled
                    # 开启心跳线程
                    self.heartThread = threading.Thread(target=self.heartLink, args=(self.event,), name='Thread-heart')
                    self.heartThread.start()
                    # 查询当前是否有未完成题库试卷答题在进行中
                    check_examination_msg = self.examinationobj.pack_checkExaminationstatus(self.token)
                    self.sock.sendall(check_examination_msg)

                    # 查询当前是否有未完成的实验
                    check_experimentation_msg = self.experimentationobj.pack_nobookExperimentationstatus(self.token)
                    self.sock.sendall(check_experimentation_msg)

                    # 学生查询是否有未完成互动课件练习
                    check_courseware_exercise_msg = self.coursewareObj.pack_checkExercisestatus(self.token)
                    self.sock.sendall(check_courseware_exercise_msg)
            # 到课奖励
            elif resMsg.head_frame.msg_type in [msg_type_pb2.COME_TO_CLASS_REWARD_P2P]:
                if resMsg.logical_frame.come2class_reward_p2p.is_ontime:
                    print("按时上课，奖励%d海星" % (resMsg.logical_frame.come2class_reward_p2p.reward_count))
                else:
                    print("迟到，奖励%d海星" % (resMsg.logical_frame.come2class_reward_p2p.reward_count))
            ### 处理特殊奖励逻辑
            elif resMsg.head_frame.msg_type in [msg_type_pb2.SEND_SPECIAL_AWARD_BROADCAST,
                                                msg_type_pb2.SPECIAL_AWARD_REPORT_RES]:
                self.do_specialAward(resMsg)

            ### 处理海星奖励逻辑
            elif resMsg.head_frame.msg_type in [msg_type_pb2.REWARD_EVERYONE_BROADCAST, msg_type_pb2.REWARD_REPORT_RES,
                                                msg_type_pb2.REWARD_INDIVIDUAL_BROADCAST,
                                                msg_type_pb2.REWARD_INDIVIDUAL_P2P]:
                self.do_reward(resMsg)

            ### 处理全体禁言逻辑
            elif resMsg.head_frame.msg_type == msg_type_pb2.CHAT_CONTROL_BROADCAST:
                if resMsg.logical_frame.chat_control_broadcast.operation == 1:
                    self.chatDisabled = True
                    print("聊天已关闭")
                else:
                    self.chatDisabled = False
                    print("聊天已打开")

            ### 处理中奖名单逻辑
            elif resMsg.head_frame.msg_type == msg_type_pb2.LOTTERY_BROADCAST:
                lottery_user_list = resMsg.logical_frame.lottery_broadcast.user_list
                if self.joinObj.userId in lottery_user_list:
                    print("恭喜你中奖了：", self.joinObj.userId)

            ### 处理MVP&连对逻辑
            elif resMsg.head_frame.msg_type in [msg_type_pb2.CONTINUE_RIGHT_P2P,
                                                msg_type_pb2.MVP_BROADCAST,
                                                msg_type_pb2.PUSH_USER_AND_GROUP_INFO_P2P]:
                if resMsg.head_frame.msg_type == msg_type_pb2.CONTINUE_RIGHT_P2P:
                    self.continue_right_num = resMsg.logical_frame.continue_right_p2p.continue_right_num
                elif resMsg.head_frame.msg_type == msg_type_pb2.MVP_BROADCAST:
                    if self.userId == resMsg.logical_frame.mvp_broadcast.user_id:
                        self.is_mvp = True
                        print("我是MVP：", self.userId)
                    else:
                        self.is_mvp = False
                else:
                    self.continue_right_num = resMsg.logical_frame.user_data_group_info_p2p.continue_right_num
                    if self.userId == resMsg.logical_frame.user_data_group_info_p2p.mvp_user_id:
                        self.is_mvp = True
                        print("我是MVP：", self.userId)
                    else:
                        self.is_mvp = False

            ### 处理互动答题相关
            else:
                # 判断学生是否可以参与互动
                if self.interaciton == True:
                    # 处理学生聊天逻辑
                    if resMsg.head_frame.msg_type in [msg_type_pb2.STUDENT_CHAT_RES,
                                                      msg_type_pb2.STUDENT_CHAT_BROADCAST,
                                                      msg_type_pb2.CHAT_RES, msg_type_pb2.CHAT_BROADCAST]:
                        pass
                    # 处理答题投票逻辑
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.VOTE_START_BROADCAST,
                                                        msg_type_pb2.VOTE_START_NEW_BROADCAST,
                                                        msg_type_pb2.VOTE_STOP_BROADCAST, msg_type_pb2.SUBMIT_VOTE_RES,
                                                        msg_type_pb2.VOTE_NO_FINISH_P2P]:
                        pool.submit(self.do_vote, resMsg)
                    ### 处理语音答题逻辑
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.VOICE_READ_START_BROADCAST,
                                                        msg_type_pb2.VOICE_NO_FINISH_P2P,
                                                        msg_type_pb2.VOICE_READ_STOP_BROADCAST,
                                                        msg_type_pb2.VOICE_READ_REPORT_RES]:
                        self.do_voice(resMsg)

                    ### 处理朗读题逻辑 ###
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.READ_SENTENCE_START_BROADCAST,
                                                        msg_type_pb2.SENTENCE_NO_FINISH_P2P,
                                                        msg_type_pb2.READ_SENTENCE_STOP_BROADCAST,
                                                        msg_type_pb2.READ_SENTENCE_SUBMIT_RES]:
                        self.do_readSentence(resMsg)

                    ### 处理抢答题逻辑
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.OPEN_CONTEST_BROADCAST,
                                                        msg_type_pb2.SUBMIT_CONTEST_RES,
                                                        msg_type_pb2.CLOSE_CONTEST_BROADCAST]:
                        self.do_contest(resMsg)

                    ### 处理公开课学生举手逻辑
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.PUBLIC_CLASS_START_STAGE_UP_BROADCAST,
                                                        msg_type_pb2.PUBLIC_CLASS_HANDS_UP_RES,
                                                        msg_type_pb2.PUBLIC_CLASS_STOP_STAGE_UP_BROADCAST,
                                                        msg_type_pb2.PUBLIC_CLASS_PICK_HANDS_UP_USER_TO_STAGE_P2P,
                                                        msg_type_pb2.PUBLIC_CLASS_USER_STAGE_UP_BROADCAST,
                                                        msg_type_pb2.PUBLIC_CLASS_USER_STAGE_UP_RES,
                                                        msg_type_pb2.PUBLIC_CLASS_LET_USER_STAGE_DOWN_BROADCAST]:
                        self.do_publicStageup(resMsg)

                    ### 处理推题答题逻辑
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.START_EXAMINATION_BROADCAST,
                                                        msg_type_pb2.STOP_EXAMINATION_BROADCAST,
                                                        msg_type_pb2.REPORT_EXAMINATION_RESULT_RES,
                                                        msg_type_pb2.STUDENT_COMPLETE_EXAMINATION_RES,
                                                        msg_type_pb2.CHECK_EXAMINATION_STATUS_RES,
                                                        msg_type_pb2.GET_EXAMINATION_BY_ID_RES, ]:
                        examination_logic_result = self.examinationobj.examinationLogic(resMsg)
                        if examination_logic_result == 1342:
                            pool.submit(self.do_examination)
                        # 检测有未完成试卷
                        elif examination_logic_result == 1471:
                            get_examination_by_id = self.examinationobj.pack_getExaminationbyid(self.joinObj.join_token,
                                                                                                self.examinationobj.examination_id)
                            self.sock.sendall(get_examination_by_id)
                        elif examination_logic_result == 1481:
                            pool.submit(self.do_examination)

                    ### 处理推送实验逻辑
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.PUSH_LIVE_NOBOOK_EXPERIMENTATION_BROADCAST,
                                                        msg_type_pb2.STOP_LIVE_NOBOOK_EXPERIMENTATION_BROADCAST,
                                                        msg_type_pb2.COMMIT_LIVE_NOBOOK_EXPERIMENTATION_RES,
                                                        msg_type_pb2.CHECK_NOBOOK_EXPERIMENTATION_STATUS_RES, ]:
                        nobook_logic_result = self.experimentationobj.nobookLogic(resMsg)
                        if nobook_logic_result == 1502 or nobook_logic_result == 1551:
                            pool.submit(self.do_experimentation)

                    ### 处理互动课件逻辑
                    elif resMsg.head_frame.msg_type in [msg_type_pb2.COURSEWARE_EXERCISE_START_BROADCAST,
                                                        msg_type_pb2.COURSEWARE_QUESTION_REPORT_RES,
                                                        msg_type_pb2.COURSEWARE_EXERCISE_STOP_BROADCAST,
                                                        msg_type_pb2.CHECK_COURSEWARE_EXERCISE_STATUS_RES]:
                        courseware_logic_result = self.coursewareObj.coursewareExerciselogic(resMsg)
                        if courseware_logic_result == 1632 or courseware_logic_result == 1691:
                            pool.submit(self.do_coursewareExercise)
                    else:
                        print("其他代码：", resMsg.head_frame.msg_type, resMsg.result_frame.code, resMsg.result_frame.msg)
        except Exception as e:
            print (e)

    # 心跳函数,每15秒发送一次
    def heartLink(self, event):
        while self.isLogin:
            try:
                # 构造心跳包
                heartPack = kodec_pb2.Cmd()
                heartPack.tp = kodec_pb2.Cmd.PING
                heartPack.ct = int(time.time() * 1000)
                #
                msg_ping = heartPack.Ping()
                msg_ping.groupId = str(self.roomIndex)
                heartPack.d = msg_ping.SerializeToString()

                heartMsg_len = heartPack.ByteSize() + 2
                heartMsg_flag = int('0x1000', 16)
                heartMsg = heartPack.SerializeToString()
                heartBeat = struct.pack('!IH', heartMsg_len, heartMsg_flag) + heartMsg
                self.sock.send(heartBeat)
                time.sleep(15)
            except Exception as err:
                print(u"网络不稳定重连中（心跳）：", err)
                if not event.is_set():
                    event.wait()

    # 加入房间
    def do_join(self):
        try:
            # 创建新的tcp socket连接
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            # 与MSN建立连接
            if setting == 1 or setting == 3:
                ### 连接测试环境 或 开发环境
                # self.sock.connect_ex(('10.200.241.44', 8114))
                self.sock.connect_ex((msn_ip, 8114))
                self.sock.getpeername()
                print("连接成功", self.sock.getpeername())
                logging.info("连接成功")
                self.readThread = threading.Thread(target=self.readSockData, args=(self.event,), name='Thread-read')
                self.readThread.start()
            elif setting == 2:
                ### 连接正式环境
                msnIp = getMsnIp()
                if self.sock.connect_ex((msnIp[0], 8114)) == 0:
                    self.sock.getpeername()
                    print("连接成功", self.sock.getpeername())
                    self.readThread = threading.Thread(target=self.readSockData, args=(self.event,), name='Thread-read')
                    self.readThread.start()
                else:
                    self.sock.connect_ex((msnIp[1], 8114))
                    self.sock.getpeername()
                    print("连接成功", self.sock.getpeername())
                    self.readThread = threading.Thread(target=self.readSockData, args=(self.event,), name='Thread-read')
                    self.readThread.start()
            else:
                if self.sock.connect_ex((msn_ip, 8114)) == 0:
                    self.sock.getpeername()
                    print("连接成功", self.sock.getpeername())
                    self.readThread = threading.Thread(target=self.readSockData, args=(self.event,), name='Thread-read')
                    self.readThread.start()

            self.joinReqMessage = self.joinObj.pack_joinReq()
            # 发送加入房间请求
            self.sock.sendall(self.joinReqMessage)
            # self.heartThread = threading.Thread(target=self.heartLink, args=(self.event,), name='Thread-heart')
            # self.heartThread.start()
        except Exception as err:
            print(err)


    # 重新加入房间
    def do_rejoin(self):
        try:
            while True:
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if self.sock.connect_ex((msn_ip, 8114)) == 0:
                    print("重连成功", self.sock.getpeername())
                    time.sleep(2)
                    # 重新加入房间
                    self.rejoin_msg = self.joinObj.pack_rejoin(self.token)
                    self.sock.sendall(self.rejoin_msg)
                    self.event.set()
                    break
                else:
                    time.sleep(5)
        except Exception as err:
            print(err)

    # 学生聊天
    def do_chat(self, join_token):
        try:
            #rows_index = random.randint(0, num_rows-1)
            while True:
                for rows_index in range(num_rows):
                    if (self.isForbidden == False) and (self.chatDisabled == False) and (
                            self.groupChatDisabled == False):
                        self.chatObj.content = str(chat_sheet.cell(rows_index, 2).value)
                        chatMsg = self.chatObj.pack_stuChat(join_token, self.is_mvp, self.continue_right_num)
                        self.sock.sendall(chatMsg)
                        time.sleep(1)
                    else:
                        pass
        except Exception as e:
            print("网络不稳定重连中（发聊天）：", e)
            if not self.event.is_set():
                self.event.wait()

    # 主动离开房间
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

    # 学生抢答
    def do_contest(self, res_msg):
        if self.contestObj.contestLogic(res_msg):
            contestMsg = self.contestObj.pack_submitContest(self.joinObj.join_token)
            time_used = random.uniform(0, 3)
            print("用时：", round(time_used, 3))
            time.sleep(self.contestObj.waitTime + round(time_used, 3))
            self.sock.sendall(contestMsg)

    # 学生语音打分
    def do_voice(self, res_msg):
        if self.voiceObj.voiceLogic(res_msg):
            code = 0
            voiceUrl = "http://edu.hivoice.cn:9088/WebAudio-1.0-SNAPSHOT/audio/play/a8807827-1f90-4822-897e-0a753657987b/1536224044229310397/sh"
            level = random.sample([1, 2, 3, 4, 5], 1)[0]
            voice_duration = random.randint(1000, 15000)
            voiceMsg = self.voiceObj.pack_submitVoice(self.joinObj.join_token, code, voiceUrl, level, voice_duration)
            time.sleep(random.randint(1,5))
            self.sock.sendall(voiceMsg)

    # 学生作答朗读题
    def do_readSentence(self, res_msg):
        if self.readSentenceObj.readLogic(res_msg):
            # audioUrl = "http://ppt.test.17zuoye.net/playback/commonfile/20181011/ea47eb33fe934f08906c5eb22c3d4321.mp3"
            audioUrl = "/playback/commonfile/20181011/ea47eb33fe934f08906c5eb22c3d4321.mp3"
            readMsg = self.readSentenceObj.pack_submitRead(self.joinObj.join_token, audioUrl)
            time_read = random.randint(1, self.readSentenceObj.maxRecordTime // 1000)
            time.sleep(time_read)
            self.sock.sendall(readMsg)

    # 学生提交投票
    def do_vote(self, res_msg):
        if self.voteObj.voteLogic(res_msg):
            submitOptions = ""
            if self.voteObj.type == logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE:
                print(u"少于4个选项单选题，请输入答案：")
                # submitOptions = ['A']
                submitOptions = random.sample(self.voteObj.choice, 1)
                print(submitOptions)
            elif self.voteObj.type == logical_pb2.SIGNLE_RIGHT_MULTIPLE_CHOICE:
                print(u"大于4个选项单选题，请输入答案：")
                # submitOptions = ['E']
                submitOptions = random.sample(self.voteObj.choice, 1)
                print(submitOptions)
            elif self.voteObj.type == logical_pb2.MULTIPLE_CHOICE:
                print(u"不定项选择题，请输入答案：")
                count = random.randint(1, len(self.voteObj.choice))
                submitOptions = random.sample(self.voteObj.choice, count)
                submitOptions.sort()
                print(submitOptions)
            elif self.voteObj.type == logical_pb2.NO_RIGHT_CHOICE:
                print(u"单选投票，请输入答案：")
                # submitOptions = ['A']
                submitOptions = random.sample(self.voteObj.choice, 1)
                print(submitOptions)
            elif self.voteObj.type == logical_pb2.NO_RIGHT_CHOICE_MULTI:
                print(u"多选投票，请输入答案：")
                # submitOptions = ['A', 'B']
                count = random.randint(1, len(self.voteObj.choice))
                submitOptions = random.sample(self.voteObj.choice, count)
                submitOptions.sort()
                print(submitOptions)
            # 处理快速调查类型
            elif self.voteObj.type == logical_pb2.NO_RIGHT_SURVEY:
                print(u"快速调查，内容为：", self.voteObj.vote_description)
                print(u"\n请输入答案：")
                submitOptions = random.sample(self.voteObj.choice, 1)
                print(submitOptions)
            else:
                print(u"未知题型！")
            voteMsg = self.voteObj.pack_submitVote(self.joinObj.join_token, submitOptions)
            time.sleep(random.randint(1,3))
            self.sock.sendall(voteMsg)
            # 设置答题开始时间
            self.voteObj.start_req_time = int(time.time() * 1000)

    # 特殊奖励
    def do_specialAward(self,res_msg):
        if self.awardObj.specialAwardLogic(res_msg):
            reportMsg = self.awardObj.pack_specialAwardReport(self.joinObj.join_token)
            time.sleep(1)
            self.sock.sendall(reportMsg)

    # 收海星奖励
    def do_reward(self, res_msg):
        if self.rewardObj.rewardLogic(res_msg):
            reward_report = self.rewardObj.pack_rewardReport(self.joinObj.join_token)
            time.sleep(1)
            self.sock.sendall(reward_report)

    # 学生连麦
    def do_publicStageup(self, res_msg):
        stageup_flag = self.publicStageupObj.publicClassStageupLogic(res_msg)
        # 收到公开课发起学生上台广播
        if stageup_flag == 1042:
            handsupMsg = self.publicStageupObj.pack_publicClassHandsup(self.joinObj.join_token)
            handup_time = random.randint(1, 15)
            time.sleep(handup_time)
            self.sock.sendall(handsupMsg)
        # 公开课老师指定学生上台p2p
        elif stageup_flag == 1072:
            stageupMsg = self.publicStageupObj.pack_publicUserStageup(self.joinObj.join_token)
            time.sleep(1)
            self.sock.sendall(stageupMsg)
        # 公开课老师停止学生上台广播
        elif stageup_flag == 1102:
            pass

    # 学生作答试卷
    def do_examination(self):
        final_examination_answer = list()
        correct_count = 0
        for question_index in self.examinationobj.question_index_list:
            question_options = ['0', '1', '2', '3']
            question_type_index = self.examinationobj.question_index_list.index(question_index)
            question_type = self.examinationobj.examination[question_type_index]['questionTypeNum']
            correct_answers = self.examinationobj.examination[question_type_index]['answers'][0]
            examination_answer = {
                'answers':[
                    [
                        {
                            'answer':'3',
                            'subAnswers':[

                            ],
                            'richTexts':None,
                            'scorePercentage':1,
                            'classification':'',
                            'knowledgePoints':None,
                            'knowledgePointsNew':[

                            ],
                            'testMethods':[

                            ],
                            'solutionMethods':[

                            ],
                            'classificationListenUrl':None,
                            'variantId':None,
                            'top10':None,
                            'stepNum':0,
                            'variants':[

                            ],
                            'groupId':0,
                            'shiftNum':0
                        }
                    ]
                ],
                'master':False,
                'subMaster':[
                    [
                        False
                    ]
                ],
                'userAnswers':[
                    [
                        '1'
                    ]
                ],
                'pointList':[
                    None
                ],
                'hintIntervention':True
            }
            print ("########", question_type, correct_answers)
            if question_type == 1:
                question_options.remove(correct_answers[0])
            # 设置上报参数is_right，examination_options
            is_right = random.choice([True, False])
            submit_options = random.sample(question_options, 1)
            if is_right == True:
                correct_count = correct_count + 1
                submit_options = correct_answers
                examination_answer['answers'][0][0]['answer'] = submit_options[0]
                examination_answer['master'] = True
                examination_answer['subMaster'] = [[True]]
                examination_answer['userAnswers'] = [submit_options]
            else:
                examination_answer['answers'][0][0]['answer'] = submit_options[0]
                examination_answer['master'] = False
                examination_answer['subMaster'] = [[False]]
                examination_answer['userAnswers'] = [submit_options]
            # 构造提交单道题答案的数据包
            result_msg = self.examinationobj.pack_Examinationresult(self.joinObj.join_token,
                                                                    question_index, is_right,
                                                                    submit_options,
                                                                    json.dumps(examination_answer))
            # 提交单题答案
            self.sock.sendall(result_msg)
            final_examination_answer.append(deepcopy(examination_answer))
            time.sleep(random.randint(1,10))
        # 设置最终提交答案并发送
        final_examination_answer = json.dumps(final_examination_answer)
        score = int(round((correct_count / len(self.examinationobj.question_index_list)), 2) * 100)
        complete_msg = self.examinationobj.pack_completeExamination(self.joinObj.join_token, final_examination_answer, score)
        time.sleep(random.randint(1, 20))
        self.sock.sendall(complete_msg)

    # 学生做nobook实验
    def do_experimentation(self):
        current_experimentation_id = self.experimentationobj.experimentation_id
        commit_msg = self.experimentationobj.pack_commitNobook(self.joinObj.join_token,
                                                               current_experimentation_id)
        if self.experimentationobj.nobook_over == False:
            time.sleep(random.randint(1, 60))
            if (self.experimentationobj.nobook_over == False) and \
                    (self.experimentationobj.experimentation_id == current_experimentation_id):
                self.sock.sendall(commit_msg)

    # 学生做互动课件题
    def do_coursewareExercise(self):
        # 根据互动题个数循环作答
        for question_index in range(self.coursewareObj.questions_count):
            courseware_exercise_id = self.coursewareObj.courseware_exercise_id
            right_answers = self.coursewareObj.courseware_questions[question_index].right_answer
            courseware_question_type = self.coursewareObj.courseware_questions[question_index].question_type
            submit_type = self.coursewareObj.courseware_questions[question_index].submit_type
            print (submit_type, right_answers)
            # if question_index == (questions_count - 1):
            #     time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
            # 引导类
            if submit_type == logical_pb2.COURSEWARE_EXERCISE_SUBMIT_GUIDE:
                # 拖拽分类/拖拽拼图
                if courseware_question_type == "DRAG_PUZZLE" or courseware_question_type == "DRAG_CLASSIFY":
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = []
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1,40))
                    if self.coursewareObj.exercise_over == True:
                        break
                    # time.sleep(random.randint(1,self.coursewareObj.countdown_seconds))
                    self.sock.sendall(question_report_msg)
                # 连线
                elif courseware_question_type == "LINES":
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1,40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 选文/选图（引导类）
                elif courseware_question_type == "MULTIPLE":
                    wrong_answer_history = ['A', 'B', 'C', 'D']
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 4)
                    if len(right_answers) < 2:
                        wrong_answer_history.remove(right_answers[0])
                        wrong_answer_history = random.sample(wrong_answer_history, retry_times-1)
                    elif len(right_answers) < 4 and len(right_answers) >= 2:
                        for option in right_answers:
                            wrong_answer_history.remove(option)
                        if retry_times == 1:
                            wrong_answer_history = []
                        else:
                            wrong_answer_history = random.sample(wrong_answer_history, 1)
                    else:
                        wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1,40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 消消卡(2期)
                elif courseware_question_type == "CARD_MEMORY":
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 动图匹配(2期)
                elif courseware_question_type == "DRAG_ANIMATION":
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 句子排序(2期)
                elif courseware_question_type == "WORD_SORT":
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 听音排序(2期)
                elif courseware_question_type == "LISTEN_SORT":
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 两两匹配(3期)
                elif courseware_question_type == "TWO_MATCH":
                    print ("两两匹配")
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 50))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 点击变图(3期)
                elif courseware_question_type == "CLICK_CHANGE":
                    print("点击变图")
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    courseware_exercise_answers = right_answers
                    retry_times = random.randint(1, 10)
                    wrong_answer_history = []
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 50))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)

            # 提交类
            elif submit_type == logical_pb2.COURSEWARE_EXERCISE_SUBMIT_COMMIT:
                answer_options = ['A', 'B', 'C', 'D']
                retry_times = 1
                wrong_answer_history = []
                # 选文/选图
                if courseware_question_type == "MULTIPLE":
                    courseware_exercise_answers = random.sample(answer_options, len(right_answers))
                    if courseware_exercise_answers == right_answers:
                        complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT
                    else:
                        complete_level = logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1,40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 数学填空
                elif courseware_question_type == "FILLBLANK":
                    # 若填空的答案选项是1个
                    if len(right_answers) <= 1:
                        complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                        logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                        if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                            courseware_exercise_answers = right_answers
                        else:
                            courseware_exercise_answers = random.sample(answer_options, len(right_answers))
                        # 封装互动题答案消息
                        question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                               courseware_exercise_id,
                                                                                               question_index,
                                                                                               courseware_exercise_answers,
                                                                                               right_answers,courseware_question_type,
                                                                                               complete_level,
                                                                                               submit_type,
                                                                                               retry_times,
                                                                                               wrong_answer_history)
                        time.sleep(random.randint(1, 40))
                        # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                        if self.coursewareObj.exercise_over == True:
                            break
                        self.sock.sendall(question_report_msg)
                    # 若填空的答案选项大于1个
                    else:
                        complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                        logical_pb2.COURSEWARE_COMPLETE_PARTIAL_RIGHT,
                                                        logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                        if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                            courseware_exercise_answers = right_answers
                        elif complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG:
                            courseware_exercise_answers = random.sample(answer_options, len(right_answers))
                        else:
                            courseware_exercise_answers = [right_answers[0]] + \
                                                          random.sample(answer_options, len(right_answers)-1)
                        # 封装互动题答案消息
                        question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                               courseware_exercise_id,
                                                                                               question_index,
                                                                                               courseware_exercise_answers,
                                                                                               right_answers,
                                                                                               courseware_question_type,
                                                                                               complete_level,
                                                                                               submit_type,
                                                                                               retry_times,
                                                                                               wrong_answer_history)
                        time.sleep(random.randint(1,40))
                        # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                        if self.coursewareObj.exercise_over == True:
                            break
                        self.sock.sendall(question_report_msg)
                # 排排序(2期)
                elif courseware_question_type == "DRAG_SORT":
                    complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_PARTIAL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                    if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                        courseware_exercise_answers = right_answers
                    elif complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG:
                        courseware_exercise_answers = right_answers
                        courseware_exercise_answers.sort(reverse=True)
                    else:
                        temp_answers = list(right_answers)
                        temp_answers.remove(right_answers[0])
                        temp_answers.sort()
                        courseware_exercise_answers = [right_answers[0]] + temp_answers

                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 裁纸模板(3期)-操作类
                elif courseware_question_type == "CUT_PAPER":
                    print("裁纸模板")
                    complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                    if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                        courseware_exercise_answers = right_answers
                    else:
                        courseware_exercise_answers = ['w']

                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 50))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 分类拖拽(3期)-操作类
                elif courseware_question_type == "DRAG_CLASSIFY":
                    print("分类拖拽-操作类")
                    complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                    if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                        courseware_exercise_answers = right_answers
                    else:
                        courseware_exercise_answers = ['w']

                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 50))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 拖拽拼图(3期)
                elif courseware_question_type == "DRAG_PUZZLE":
                    print("拖拽拼图-3期")
                    complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                    if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                        courseware_exercise_answers = right_answers
                    else:
                        courseware_exercise_answers = ['w']

                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 50))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 连线(3期)
                elif courseware_question_type == "LINES":
                    print("连线3期")
                    complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_PARTIAL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                    if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                        courseware_exercise_answers = right_answers
                    elif complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG:
                        courseware_exercise_answers = right_answers
                        courseware_exercise_answers.sort(reverse=True)
                    else:
                        courseware_exercise_answers = right_answers

                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 50))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 提交类-两辆匹配(3期)
                elif courseware_question_type == "TWO_MATCH":
                    print("提交类-两辆匹配")
                    complete_level = random.choice([logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_PARTIAL_RIGHT,
                                                    logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG])
                    if complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_RIGHT:
                        courseware_exercise_answers = right_answers
                    elif complete_level == logical_pb2.COURSEWARE_COMPLETE_ALL_WRONG:
                        courseware_exercise_answers = right_answers
                        courseware_exercise_answers.sort(reverse=True)
                    else:
                        courseware_exercise_answers = right_answers

                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
                # 打飞机-3期
                elif courseware_question_type == "HIT_PLANE":
                    pass
                # 初中选择-3期
                elif courseware_question_type == "MULTIPLE_JUNIOR":
                    pass

            # 统计类
            elif submit_type == logical_pb2.COURSEWARE_EXERCISE_SUBMIT_STATISTICS:
                answer_options = ['A', 'B', 'C', 'D', 'E', 'F']
                retry_times = 1
                wrong_answer_history = []
                # 选文/选图
                if courseware_question_type == "MULTIPLE":
                    complete_level = logical_pb2.COURSEWARE_COMPLETE_OTHER
                    # 从选项中随机选取答案
                    courseware_exercise_answers = random.sample(answer_options, 1)
                    # 封装互动题答案消息
                    question_report_msg = self.coursewareObj.pack_coursewareQuestionReport(self.token,
                                                                                           courseware_exercise_id,
                                                                                           question_index,
                                                                                           courseware_exercise_answers,
                                                                                           right_answers,
                                                                                           courseware_question_type,
                                                                                           complete_level,
                                                                                           submit_type,
                                                                                           retry_times,
                                                                                           wrong_answer_history)
                    time.sleep(random.randint(1, 40))
                    # time.sleep(random.randint(1, self.coursewareObj.countdown_seconds))
                    if self.coursewareObj.exercise_over == True:
                        break
                    self.sock.sendall(question_report_msg)
            # 语音类
            elif submit_type == logical_pb2.COURSEWARE_EXERCISE_SUBMIT_VOICE:
                pass
            else:
                # 若类型为COURSEWARE_EXERCISE_SUBMIT_OTHER
                pass
