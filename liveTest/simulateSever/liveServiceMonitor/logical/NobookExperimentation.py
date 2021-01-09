# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# Nobook实验
class NobookExperimentation(object):
    def __init__(self, userId):
        self.userId = userId
        self.experimentation_id = ""
        self.teacher_id = ""

    # Nobook实验逻辑函数
    def nobookLogic(self, recData):
        if recData.result_frame.code == 0:
            # 收到推送实验广播
            if recData.head_frame.msg_type == msg_type_pb2.PUSH_LIVE_NOBOOK_EXPERIMENTATION_BROADCAST:
                start_nobook_experimentation = recData.logical_frame.push_live_nobook_experimentation_broadcast
                self.experimentation_id = start_nobook_experimentation.experimentation_id
                self.experimentation_name = start_nobook_experimentation.experimentation_name
                self.experimentation_img = start_nobook_experimentation.experimentation_img
                self.experimentation_addr = start_nobook_experimentation.experimentation_addr
                self.start_time  = start_nobook_experimentation.start_time
                self.nobook_over = False
                print("experimentation_id:", self.experimentation_id)
                print("experimentation_name:", self.experimentation_name)
                print("experimentation_img:", self.experimentation_img)
                print("experimentation_addr:", self.experimentation_addr)
                print("start_time:", self.start_time)
                return 1502
            # 收到结束实验广播
            elif recData.head_frame.msg_type == msg_type_pb2.STOP_LIVE_NOBOOK_EXPERIMENTATION_BROADCAST:
                print("结束实验：",recData.logical_frame.stop_live_nobook_experimentation_broadcast.experimentation_id)
                self.nobook_over = True
                return 1512
            # 提交实验响应
            elif recData.head_frame.msg_type == msg_type_pb2.COMMIT_LIVE_NOBOOK_EXPERIMENTATION_RES:
                result_res = recData.logical_frame.commit_live_nobook_experimentation_res
                print("提交实验结果成功, experimentation_id: %s" % (result_res.experimentation_id))
                return 1521
            # 查询当前是否有未完成的实验
            elif recData.head_frame.msg_type == msg_type_pb2.CHECK_NOBOOK_EXPERIMENTATION_STATUS_RES:
                check_nobook_experimentation_status_res = recData.logical_frame.check_nobook_experimentation_status_res
                self.experimentation_id = check_nobook_experimentation_status_res.experimentation_id
                if self.experimentation_id != "":
                    self.experimentation_name = check_nobook_experimentation_status_res.experimentation_name
                    self.experimentation_img = check_nobook_experimentation_status_res.experimentation_img
                    self.experimentation_addr = check_nobook_experimentation_status_res.experimentation_addr
                    self.start_time = check_nobook_experimentation_status_res.start_time
                    self.nobook_over = False
                    print("experimentation_id:", self.experimentation_id)
                    print("experimentation_name:", self.experimentation_name)
                    print("experimentation_img:", self.experimentation_img)
                    print("experimentation_addr:", self.experimentation_addr)
                    print("start_time:", self.start_time)
                    return 1551
                else:
                    pass
        else:
            print ("实验处理报错：", recData.result_frame.code, recData.result_frame.msg)

    # 学生提交实验封包
    def pack_commitNobook(self, token, experimentation_id):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.COMMIT_LIVE_NOBOOK_EXPERIMENTATION_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.commit_live_nobook_experimentation_req
        reqBody.experimentation_id = experimentation_id

        # 对提交实验请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        commitnobookMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return commitnobookMessage

    # 查询当前是否有未完成实验封包
    def pack_nobookExperimentationstatus(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.CHECK_NOBOOK_EXPERIMENTATION_STATUS_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.check_nobook_experimentation_status_req

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        checkMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return checkMessage