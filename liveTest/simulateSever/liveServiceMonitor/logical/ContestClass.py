# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 抢答题 #
class ContestClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.token = ""

    # 抢答题逻辑函数
    def contestLogic(self, recData):
        ## 处理抢答题广播消息
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.OPEN_CONTEST_BROADCAST:
                print ("收到抢答题：", recData.logical_frame.contest_open_res.question_id,
                    recData.logical_frame.contest_open_res.wait_time)
                self.questionId = recData.logical_frame.contest_open_res.question_id
                self.waitTime = 3
                return True
            elif recData.head_frame.msg_type == msg_type_pb2.SUBMIT_CONTEST_RES:
                print ("抢答完成!-", recData.logical_frame.contest_submit_res.question_id)
                return False
            elif recData.head_frame.msg_type == msg_type_pb2.CLOSE_CONTEST_BROADCAST:
                print ("结束抢答-", recData.logical_frame.contest_close_broadcast.question_id)
                return False
        else:
            pass

    # 提交抢答题封包函数
    def pack_submitContest(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.SUBMIT_CONTEST_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0
        reqCommFrame.version = 101000012
       #reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        ## 客户端系统和版本信息
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报语音答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.submit_contest
        reqBody.question_id = self.questionId

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        voiceMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        reportMessage = struct.pack('!IH', Msg_len, Msg_flag) + voiceMessage
        return reportMessage