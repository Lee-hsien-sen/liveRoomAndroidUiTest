# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 测试环境常量 #
# app_secret = '4911898908f9d03ae7bf913f2ae16cb1'
# app_id = '58eee6ac19b005fec0d848ce'

#正式环境常量#
app_secret = 'ea4958b53cd9da924e1223252d5d215b'
app_id = '59a91c3237d3d8d28516801c'

# 离开房间
class LeaveClass(object):
    def __init__(self, liveId, userId, userType, roomIndex):
        self.liveId = liveId
        self.userId = userId
        self.userType = userType
        self.roomIndex = roomIndex
        self.appId = app_id
        self.appSecret = app_secret
        self.join_token = ""

    def pack_leaveReq(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.LEAVE_ROOM_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 9999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId  # 12976231 老师ID
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造聊天请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.leave_room
        reqBody.reason = logical_pb2.LeaveReason
        reqBody.errmsg= ""

        # 对聊天请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        leaveReqMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        leaveReqMessage = struct.pack('!IH', Msg_len, Msg_flag) + leaveReqMessage
        return leaveReqMessage
