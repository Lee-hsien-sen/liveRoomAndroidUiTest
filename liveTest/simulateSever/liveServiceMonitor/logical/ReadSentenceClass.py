# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 朗读题
class ReadSentenceClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.token = ""

    # 朗读题逻辑函数
    def readLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.READ_SENTENCE_START_BROADCAST:
                print("收到朗读答题：", recData.logical_frame.read_sentence_start_broadcast.question_id,
                    recData.logical_frame.read_sentence_start_broadcast.text)
                self.questionId = recData.logical_frame.read_sentence_start_broadcast.question_id
                self.text = recData.logical_frame.read_sentence_start_broadcast.text
                self.maxRecordTime = recData.logical_frame.read_sentence_start_broadcast.max_record_time  ## 毫秒
                self.teacherId = recData.logical_frame.read_sentence_start_broadcast.teacher_id
                return True
            elif recData.head_frame.msg_type == msg_type_pb2.SENTENCE_NO_FINISH_P2P:
                print("未完成朗读答题：", recData.logical_frame.sentence_no_finish_p2p.question_id,
                      recData.logical_frame.sentence_no_finish_p2p.text)
                self.questionId = recData.logical_frame.sentence_no_finish_p2p.question_id
                self.text = recData.logical_frame.sentence_no_finish_p2p.text
                self.maxRecordTime = recData.logical_frame.sentence_no_finish_p2p.max_record_time  ## 毫秒
                self.teacherId = recData.logical_frame.sentence_no_finish_p2p.teacher_id
                return True
            elif recData.head_frame.msg_type == msg_type_pb2.READ_SENTENCE_STOP_BROADCAST:
                print ("停止朗读题：", recData.logical_frame.read_sentence_stop_broadcast.question_id)
                return False
            elif recData.head_frame.msg_type == msg_type_pb2.READ_SENTENCE_SUBMIT_RES:
                print ("提交朗读完成：", self.questionId)
                return False
    # 提交朗读题封包函数
    def pack_submitRead(self, token, audioUrl):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.READ_SENTENCE_SUBMIT_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报朗读题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.read_sentence_submit
        reqBody.question_id = self.questionId
        reqBody.text = self.text
        reqBody.record_time = 9000
        reqBody.audio_url = audioUrl
        reqBody.teacher_id = self.teacherId
        # reqBody.err_code = random.sample([0, 1, 2, 3, 4], 1)[0]
        reqBody.err_code = 0
        # reqBody.err_msg = "ok"
        if reqBody.err_code == 0:
            reqBody.err_msg = ""
        elif reqBody.err_code == 1:
            reqBody.err_msg = "录音时间过短"
            reqBody.record_time = 0
            reqBody.audio_url = ""
        elif reqBody.err_code == 2:
            reqBody.err_msg = "未授权录音功能"
            reqBody.record_time = 0
            reqBody.audio_url = ""
        elif reqBody.err_code == 3:
            reqBody.err_msg = "其他"
            reqBody.record_time = 0
            reqBody.audio_url = ""
        elif reqBody.err_code == 4:
            reqBody.err_msg = u"上传时网络错误"
            reqBody.record_time = 0
            reqBody.audio_url = ""

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        readMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        reportMessage = struct.pack('!IH', Msg_len, Msg_flag) + readMessage
        return reportMessage