# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random
from public import globalvar
from public.logger import logger

# 聊天
class ChatClass(object):
    def __init__(self, userId, user_group, token):
        self.userId = userId
        self.user_group = user_group
        self.token = token
        self.content = ""
        # 新增聊天请求开始时间、聊天响应时间
        self.chat_req_time = 0
        self.chat_res_time = 0

    def pack_stuChat(self, token, is_mvp, continue_right_num):
        # 构造学生聊天req消息
        chatPack = logical_pb2.RequestPackage()
        chatCommFrame = chatPack.head_frame
        chatCommFrame.msg_type = msg_type_pb2.STUDENT_CHAT_REQ
        chatCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 9999))  # 采用随机数
        chatCommFrame.msg_from_user_id = self.userId  # 12976231 老师ID
        chatCommFrame.msg_to_user_id = ""
        chatCommFrame.device_type = 0
        chatCommFrame.version = 101000012
        #chatCommFrame.timestamp = int(time.time() * 1000)
        chatCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        chatCommFrame.client_info.os_name = "windows"
        chatCommFrame.client_info.client_version = "wkai2133"
        chatCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造聊天请求逻辑帧
        chat_message = logical_pb2.RequestMessage()
        chat_message.token = token
        chat_reqMsg = chat_message.chat
        chat_reqMsg.chat_id = random.randint(1, 9999)
        chat_reqMsg.content = self.content
        chat_reqMsg.to = self.user_group
        chat_reqMsg.is_mvp = is_mvp
        chat_reqMsg.continue_right_num = continue_right_num

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
                # 收到聊天响应时间戳
                self.chat_res_time = int(time.time()*1000)
                # 计算聊天响应时间
                self.chat_duration = self.chat_res_time - self.chat_req_time
                #
                #globalvar.set_value(self.userId, 'student_chat_duration', self.chat_duration)
                globalvar.update_value(self.userId, {'student_chat_duration': self.chat_duration})
                #print("收到学生聊天响应：", resData.logical_frame.chat_res.chat_id)
                print('用户:{}, 聊天响应耗时（毫秒）: {}'.format(self.userId, self.chat_duration))
                logger.info('用户:{}, 聊天响应耗时（毫秒）: {}'.format(self.userId, self.chat_duration))
            elif resData.head_frame.msg_type == msg_type_pb2.STUDENT_CHAT_BROADCAST:
                print("收到一条 %s 发送的聊天消息, 内容为:  %s " %
                      (resData.logical_frame.chat_broadcast.nickname, resData.logical_frame.chat_broadcast.content))
                # print(resData.logical_frame.chat_broadcast.user_id, resData.logical_frame.chat_broadcast.user_type,
                #       resData.logical_frame.chat_broadcast.avatar_url, resData.logical_frame.chat_broadcast.device_type)
            elif resData.head_frame.msg_type == msg_type_pb2.CHAT_RES:
                print("Yes，收到老师聊天逻辑消息：", resData.logical_frame.chat_res.chat_id)
            elif resData.head_frame.msg_type == msg_type_pb2.CHAT_BROADCAST:
                print("收到一条 %s 老师发送的聊天消息, 内容为:  %s " %
                      (resData.logical_frame.chat_broadcast.nickname, resData.logical_frame.chat_broadcast.content))
                print(resData.logical_frame.chat_broadcast.user_id, resData.logical_frame.chat_broadcast.user_type,
                      resData.logical_frame.chat_broadcast.avatar_url, resData.logical_frame.chat_broadcast.device_type)
        else:
            print(resData.result_frame.code, resData.result_frame.msg)
