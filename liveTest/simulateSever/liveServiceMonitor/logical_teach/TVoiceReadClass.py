# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random

#### 语音跟读题
class VoiceReadClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.token = ""

    def voiceLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.VOICE_READ_START_RES:
                print("开始语音题: ", recData.logical_frame.voice_read_start_res.question_id, self.sample_text)
                self.questionId = recData.logical_frame.voice_read_start_res.question_id
            elif recData.head_frame.msg_type == msg_type_pb2.VOICE_READ_STOP_RES :
                print("停止语音题：",recData.logical_frame.voice_read_stop_res.question_id)
            elif recData.head_frame.msg_type == msg_type_pb2.VOICE_READ_QUERY_RES:
                print ("语音答题人数: ", recData.logical_frame.voice_read_query_res.user_total)
                print ("级别人数统计: ", recData.logical_frame.voice_read_query_res.analysis_list)
                print ("优质语音答题用户列表: ", recData.logical_frame.voice_read_query_res.good_user_list)
            else:
                pass
        else:
            pass

    ### 开始语音跟读题
    def pack_VoiceStart(self, token, sampleText):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.VOICE_READ_START_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报语音答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.voice_read_start
        reqBody.sample_text = sampleText
        self.sample_text = sampleText

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        voiceMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        startMessage = struct.pack('!IH', Msg_len, Msg_flag) + voiceMessage
        return startMessage

    ### 查询语音打分统计
    def pack_VoiceQuery(self, token, level):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.VOICE_READ_QUERY_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip =  IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造查询语音统计请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.voice_read_query
        reqBody.question_id = self.questionId
        reqBody.level = level

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        voiceMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        queryMessage = struct.pack('!IH', Msg_len, Msg_flag) + voiceMessage
        return queryMessage

    ### 停止语音跟读题
    def pack_VoiceStop(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.VOICE_READ_STOP_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报语音答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.voice_read_stop
        reqBody.question_id = self.questionId

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        voiceMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        stopMessage = struct.pack('!IH', Msg_len, Msg_flag) + voiceMessage
        return stopMessage
