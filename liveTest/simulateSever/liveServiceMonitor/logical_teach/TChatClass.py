# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random

#### 聊天
class ChatClass(object):
    def __init__(self, userId, user_group, token):
        self.userId = userId
        self.user_group = user_group
        self.token = token
        self.content = ""

    def pack_teaChat(self, token):
        # 构造学生聊天req消息
        chatPack = logical_pb2.RequestPackage()
        chatCommFrame = chatPack.head_frame
        chatCommFrame.msg_type = msg_type_pb2.CHAT_REQ
        chatCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        chatCommFrame.msg_from_user_id = self.userId  # 12976231 老师ID
        chatCommFrame.msg_to_user_id = ""
        chatCommFrame.device_type = 0   ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        chatCommFrame.version = 101001301
        chatCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        chatCommFrame.client_info.os_name = "windows"
        chatCommFrame.client_info.client_version = "wkai2133"
        chatCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造聊天请求逻辑帧
        chat_message = logical_pb2.RequestMessage()
        chat_message.token = token
        chat_reqMsg = chat_message.chat
        #chat_reqMsg.chat_id = random.randint(1, 99999)
        chat_reqMsg.chat_id = 0
        chat_reqMsg.content = self.content
        # chat_reqMsg.to = self.user_group
        # chat_reqMsg.user_id = self.userId
        # chat_reqMsg.nickname = u'老师昵称1'
        # chat_reqMsg.avatar_url = 'https://cdn.17xueba.com//pro/server/image/2018/01/20180122134340183387.png'
        # chat_reqMsg.user_type = 3
        # chat_reqMsg.device_type = 0
        # chat_reqMsg.ip = ip2int(socket.gethostbyname(socket.gethostname()))
        # chat_reqMsg.adornment_url = 'https://static.17xueba.com/test/server/image/2018/08/20180809180753441799.png'

        # 对聊天请求数据包进行序列化
        chatPack.logical_frame = chat_message.SerializeToString()
        chat_ReqMessage = chatPack.SerializeToString()

        chatMsg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        chatMsg_len = chatPack.ByteSize() + 2
        chat_ReqMessage = struct.pack('!IH', chatMsg_len, chatMsg_flag) + chat_ReqMessage
        return chat_ReqMessage

    def chatLogic(self, resData):
        if resData.result_frame.code == 0:
            if resData.head_frame.msg_type == msg_type_pb2.STUDENT_CHAT_RES:
                print ("学生聊天响应：", resData.logical_frame.chat_res.chat_id)
            elif resData.head_frame.msg_type == msg_type_pb2.STUDENT_CHAT_BROADCAST:
                print ("收到一条 %s 发送的聊天消息, 内容为:  %s " %
                      (resData.logical_frame.chat_broadcast.nickname, resData.logical_frame.chat_broadcast.content))
            elif resData.head_frame.msg_type == msg_type_pb2.CHAT_RES:
                print ("老师发聊天成功：", resData.logical_frame.chat_res.chat_id)
            elif resData.head_frame.msg_type == msg_type_pb2.CHAT_BROADCAST:
                print("收到一条 %s 老师发送的聊天消息, 内容为:  %s " %
                      (resData.logical_frame.chat_broadcast.nickname, resData.logical_frame.chat_broadcast.content))
                print(resData.logical_frame.chat_broadcast.user_id, resData.logical_frame.chat_broadcast.user_type,
                      resData.logical_frame.chat_broadcast.avatar_url, resData.logical_frame.chat_broadcast.device_type)
        else:
            print (resData.result_frame.code, resData.result_frame.msg)
