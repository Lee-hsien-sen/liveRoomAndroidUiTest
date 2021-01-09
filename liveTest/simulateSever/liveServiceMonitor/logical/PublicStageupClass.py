# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 公开课学生上台
class PublicStageupClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.stage_id = ""

    # 公开课连麦逻辑函数
    def publicClassStageupLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.PUBLIC_CLASS_START_STAGE_UP_BROADCAST:
                start_handsup = recData.logical_frame.public_class_start_stage_up_broadcast
                print("收到连麦上台广播：", start_handsup.stage_id)
                self.stage_id = start_handsup.stage_id
                return 1042
            elif recData.head_frame.msg_type == msg_type_pb2.PUBLIC_CLASS_HANDS_UP_RES:
                print("学生已举手成功！")
                return 1051
            elif recData.head_frame.msg_type == msg_type_pb2.PUBLIC_CLASS_STOP_STAGE_UP_BROADCAST:
                print("连麦结束！")
                return 1102
            elif recData.head_frame.msg_type == msg_type_pb2.PUBLIC_CLASS_PICK_HANDS_UP_USER_TO_STAGE_P2P:
                print("收到老师指定上台")
                p2p_user_stageup = recData.logical_frame.public_class_pick_hands_up_user_to_stage_p2p
                self.teacher_id = p2p_user_stageup.teacher_id
                self.channel_teacher_id = p2p_user_stageup.channel_teacher_id
                return 1072
            elif recData.head_frame.msg_type == msg_type_pb2.PUBLIC_CLASS_USER_STAGE_UP_RES:
                print("学生上台成功！")
                return 1081
            elif recData.head_frame.msg_type == msg_type_pb2.PUBLIC_CLASS_USER_STAGE_UP_BROADCAST:
                print("收到学生上台广播")
                user_stage_up_broadcast = recData.logical_frame.public_class_user_stage_up_broadcast
                print("本次Stage_id：", user_stage_up_broadcast.stage_id)
                print("用户频道id：", user_stage_up_broadcast.channel_user_id)
                print("用户信息：", user_stage_up_broadcast.user_info)
                return 1082
            elif recData.head_frame.msg_type == msg_type_pb2.PUBLIC_CLASS_LET_USER_STAGE_DOWN_BROADCAST:
                user_stage_down_broadcast = recData.logical_frame.public_class_let_user_stage_down_broadcast
                if user_stage_down_broadcast.user_id == self.userId:
                    print("老师让我下台：", user_stage_down_broadcast.user_id)
                return 1092
        else:
            pass

    # 公开课学生举手封包函数
    def pack_publicClassHandsup(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.PUBLIC_CLASS_HANDS_UP_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 102000017
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报奖励请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.public_class_hands_up_req
        reqBody.stage_id = self.stage_id

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        handsupMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        finalMessage = struct.pack('!IH', Msg_len, Msg_flag) + handsupMessage
        return finalMessage

    # 公开课学生上台封包函数
    def pack_publicUserStageup(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.PUBLIC_CLASS_USER_STAGE_UP_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 102000017
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报奖励请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.public_class_user_stage_up_req
        reqBody.stage_id = self.stage_id
        reqBody.channel_user_id = random.randint(12345678,87654321)
        # reqBody.channel_user_id = self.userId
        reqBody.teacher_id = self.teacher_id

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        stageupMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        finalMessage = struct.pack('!IH', Msg_len, Msg_flag) + stageupMessage
        return finalMessage