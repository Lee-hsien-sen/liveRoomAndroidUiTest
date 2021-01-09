# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random

####关闭开启聊天
class ChatControlClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.token = ""
        self.operation = 0

    def chatcontrolLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.CHAT_CONTROL_RES:
                if self.operation == 0:
                    print ("开启聊天成功!")
                elif self.operation == 1:
                    print ("关闭聊天成功!")
            else:
                pass
        else:
            pass

    def pack_chatOnoff(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.CHAT_CONTROL_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造控制聊天请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.chat_control
        reqBody.operation = self.operation

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        control_message = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        chatOnoff_msg = struct.pack('!IH', Msg_len, Msg_flag) + control_message
        return chatOnoff_msg