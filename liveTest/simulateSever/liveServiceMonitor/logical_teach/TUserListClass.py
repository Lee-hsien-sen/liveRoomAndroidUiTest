# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random

#### 获取用户列表逻辑
class UserListClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.token = ""

    def getuserlistLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.GET_USER_LIST_RES:
                print ("用户列表：", recData.logical_frame.get_user_list.users)
                print ("总用户数：", recData.logical_frame.get_user_list.total_num)
                print ("总页码：", recData.logical_frame.get_user_list.total_page)
                print ("当前页码数：", recData.logical_frame.get_user_list.current_page)
            else:
                pass
        else:
            pass

    def pack_getuserList(self, token, page_num, page_size):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.GET_USER_LIST_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报朗读题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.get_user_list
        reqBody.page_num = page_num
        reqBody.page_size = page_size

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        userList_message = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        getMessage = struct.pack('!IH', Msg_len, Msg_flag) + userList_message
        return getMessage