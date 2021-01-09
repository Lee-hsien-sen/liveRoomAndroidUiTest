# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random
import platform

#### 抢答题
class ContestClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.token = ""

    def contestLogic(self, recData):
        ## 处理抢答题广播消息
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.OPEN_CONTEST_RES:
                print ("开始抢答响应：", recData.logical_frame.contest_open_res.question_id,
                    recData.logical_frame.contest_open_res.wait_time)
                self.questionId = recData.logical_frame.contest_open_res.question_id
                self.waitTime = recData.logical_frame.contest_open_res.wait_time
            elif recData.head_frame.msg_type == msg_type_pb2.CLOSE_CONTEST_RES:
                print ("结束抢答响应：", self.questionId)
            else:
                pass
        else:
            print (recData.result_frame.code, recData.result_frame.msg)

    def pack_startContest(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.OPEN_CONTEST_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0   ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        ## 客户端系统和版本信息
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报语音答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.open_contest
        reqBody.wait_time = 3  ## 单位秒

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Message = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        ContestMessage = struct.pack('!IH', Msg_len, Msg_flag) + Message
        return ContestMessage

    ### 封装结束抢答
    def pack_stopContest(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.CLOSE_CONTEST_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0   ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        ## 客户端系统和版本信息
        reqCommFrame.client_info.os_name = platform.system()
        reqCommFrame.client_info.os_version = platform.win32_ver()[0]
        reqCommFrame.client_info.client_version = "1.1.13.1"
        reqCommFrame.client_info.browser_name = ""
        reqCommFrame.client_info.browser_version = ""
        reqCommFrame.client_info.brand_name = ""
        reqCommFrame.client_info.browser_ua = ""

        # 构造上报语音答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.close_contest
        reqBody.question_id = self.questionId  ## 单位秒

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Message = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        stopMessage = struct.pack('!IH', Msg_len, Msg_flag) + Message
        return stopMessage