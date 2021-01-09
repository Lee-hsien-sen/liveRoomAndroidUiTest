# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random

#### 朗读题
class ReadSentenceClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.token = ""

    def readLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.READ_SENTENCE_START_RES:
                print ("成功发送朗读题：", recData.logical_frame.read_sentence_start_res.question_id)
                self.questionId = recData.logical_frame.read_sentence_start_res.question_id
            elif recData.head_frame.msg_type == msg_type_pb2.READ_SENTENCE_STOP_RES:
                print("停止朗读题：", self.questionId)
            elif recData.head_frame.msg_type == msg_type_pb2.READ_SENTENCE_QUERY_RES:
                print ("###############")
                print ("答题人数：", recData.logical_frame.read_sentence_query_res.submit_number)
                print ("朗读结果信息列表：", recData.logical_frame.read_sentence_query_res.result_analysis)
                print ("###############")
        else:
            pass

    ### 开始朗读题封包
    def pack_startRead(self, token, text, max_time):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.READ_SENTENCE_START_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报朗读题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.read_sentence_start
        self.text = text
        self.max_record_time = max_time
        reqBody.text = text
        reqBody.max_record_time = max_time  ## 毫秒

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        readMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        startMessage = struct.pack('!IH', Msg_len, Msg_flag) + readMessage
        return startMessage

    ### 停止朗读题封包
    def pack_stopRead(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.READ_SENTENCE_STOP_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报朗读题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.read_sentence_stop
        reqBody.question_id = self.questionId

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        readMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        stopMessage = struct.pack('!IH', Msg_len, Msg_flag) + readMessage
        return stopMessage

    ### 轮询朗读题结果
    def pack_readQuery(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.READ_SENTENCE_QUERY_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造轮询朗读题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.read_sentence_query
        reqBody.question_id = self.questionId

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        req_msg = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        queryMessage = struct.pack('!IH', Msg_len, Msg_flag) + req_msg
        return queryMessage