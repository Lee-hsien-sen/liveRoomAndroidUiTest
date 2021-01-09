# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 语音跟读题
class VoiceReadClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.token = ""

    def voiceLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.VOICE_READ_START_BROADCAST:
                print("收到语音题: ", recData.logical_frame.voice_read_start_broadcast.question_id,
                    recData.logical_frame.voice_read_start_broadcast.sample_text)
                self.questionId = recData.logical_frame.voice_read_start_broadcast.question_id
                self.sampleText = recData.logical_frame.voice_read_start_broadcast.sample_text
                return True
            elif recData.head_frame.msg_type == msg_type_pb2.VOICE_NO_FINISH_P2P:
                print("未完成语音题：",recData.logical_frame.voice_no_finish_p2p.question_id,
                      recData.logical_frame.voice_no_finish_p2p.sample_text)
                self.questionId = recData.logical_frame.voice_no_finish_p2p.question_id
                self.sampleText = recData.logical_frame.voice_no_finish_p2p.sample_text
                return True
            elif recData.head_frame.msg_type == msg_type_pb2.VOICE_READ_STOP_BROADCAST:
                print("结束语音题：",recData.logical_frame.voice_read_stop_broadcast.question_id)
                return False
            elif recData.head_frame.msg_type == msg_type_pb2.VOICE_READ_REPORT_RES:
                print("完成语音答题：",recData.logical_frame.voice_read_report_res.question_id)
                return False
    # 上报语音打分封包函数
    def pack_submitVoice(self, token, code, voiceUrl, level, voice_duration):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.VOICE_READ_REPORT_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报语音答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.voice_read_report
        reqBody.question_id = self.questionId
        reqBody.code = code
        reqBody.message = "ok"
        reqBody.original_score = random.sample([1, 2, 3, 4, 5, 6, 7 , 8], 1)[0]
        reqBody.voice_url = voiceUrl
        reqBody.level = level
        reqBody.score = reqBody.level
        reqBody.voice_duration = voice_duration

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        voiceMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        reportMessage = struct.pack('!IH', Msg_len, Msg_flag) + voiceMessage
        return reportMessage
