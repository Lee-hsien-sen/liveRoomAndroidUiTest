# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 自定义奖励 #
class AwardClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.token = ""
        self.special_award_id = ""

    # 自定义奖励逻辑函数
    def specialAwardLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.SEND_SPECIAL_AWARD_BROADCAST:
                print("收到特殊奖励：", recData.logical_frame.send_special_award_broadcast.special_award_id,
                      recData.logical_frame.send_special_award_broadcast.award)
                special_award = recData.logical_frame.send_special_award_broadcast.award
                self.special_award_id = recData.logical_frame.send_special_award_broadcast.special_award_id
                self.type = special_award.type
                self.commodity_id = special_award.commodity_id
                self.src_url = special_award.src_url
                self.award_name = special_award.award_name
                self.teacher_id = recData.logical_frame.send_special_award_broadcast.teacher_id
                return True
            elif recData.head_frame.msg_type == msg_type_pb2.SPECIAL_AWARD_REPORT_RES:
                print("领取上报成功")
                return False
        else:
            pass

    # 收到自定义奖励上报封包
    def pack_specialAwardReport(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.SPECIAL_AWARD_REPORT_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        #reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报朗读题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.special_award_report_req
        reqBody.special_award_id = self.special_award_id
        ##设置特殊奖励对象SpecialAward的参数值
        reqBody.award.type = self.type
        reqBody.award.commodity_id = self.commodity_id
        reqBody.award.src_url = self.src_url
        reqBody.award.award_name = self.award_name
        reqBody.teacher_id = self.teacher_id

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        awardMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        reportMessage = struct.pack('!IH', Msg_len, Msg_flag) + awardMessage
        return reportMessage