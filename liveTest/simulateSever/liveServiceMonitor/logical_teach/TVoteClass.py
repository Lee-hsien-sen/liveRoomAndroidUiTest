# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random
from commons.liveServiceMonitor.public import globalvar
from tools.logger import logger

#### 选择投票题
class VoteClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.teaId = ""
        self.type = 0
        #新增开始请求、开始响应、结束请求和结束响应时间变量
        self.start_req_time = 0
        self.start_res_time = 0
        self.stop_req_time = 0
        self.stop_res_time = 0

    def voteLogic(self, recData):
        if recData.result_frame.code == 0:
            # 判断是否开始答题响应
            if recData.head_frame.msg_type == msg_type_pb2.VOTE_START_RES:
                # 获取赋值题目ID
                self.questionId = recData.logical_frame.vote_start_res.question_id
                # 设置收到开始响应时间
                self.start_res_time = int(round(time.time() * 1000))
                # 计算发起答题响应时间
                self.vote_start_duration = self.start_res_time - self.start_req_time
                #
                globalvar.update_value(self.userId, {'vote_start_duration':self.vote_start_duration})
                print ("成功发起答题: ", recData.logical_frame.vote_start_res.question_id)
                print("###发起答题耗时（毫秒）###：", self.vote_start_duration)
                #logger.info('老师:{}, 发起答题耗时（毫秒）: {}'.format(self.userId, self.vote_start_duration))
            # 判断是否结束答题响应
            elif recData.head_frame.msg_type == msg_type_pb2.VOTE_STOP_RES:
                # 设置收到结束响应时间
                self.stop_res_time = int(round(time.time() * 1000))
                # 计算结束答题响应时间
                self.vote_stop_duration = self.stop_res_time - self.stop_req_time
                globalvar.update_value(self.userId, {'vote_stop_duration': self.vote_stop_duration})
                print ("结束答题: ", recData.logical_frame.vote_stop_res.result_analysis)
                print("###答题结束耗时（毫秒）###：", self.vote_stop_duration)
                print ("回答正确用户：", recData.logical_frame.vote_stop_res.right_users)
                #logger.info('老师:{}, 答题结束耗时（毫秒）: {}'.format(self.userId, self.vote_stop_duration))
            else:
                pass
        else:
            print ("发起答题失败：", recData.result_frame.code, recData.result_frame.msg)

    #### 发起答题封包
    def pack_voteStart(self, token, vote_type):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.VOTE_START_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.vote_start

        if vote_type == logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE:
            self.type = vote_type
            reqBody.type = self.type
            nameList = ['A', 'B', 'C', 'D']
            for element in nameList:
                option = reqBody.options_array.add()
                option.option_name = element
                option.description = ""
                if option.option_name == 'A':
                    option.is_right = True
                else:
                    option.is_right = False
            reqBody.vote_description = ""
            #reqBody.options_array[0].is_right = True
        elif vote_type == logical_pb2.SIGNLE_RIGHT_MULTIPLE_CHOICE:
            self.type = vote_type
            reqBody.type = self.type
            nameList = ['A', 'B', 'C', 'D', 'E', 'F']
            for element in nameList:
                option = reqBody.options_array.add()
                option.option_name = element
                option.description = ""
                if option.option_name == 'B':
                    option.is_right = True
                else:
                    option.is_right = False
            reqBody.vote_description = ""
        elif vote_type == logical_pb2.MULTIPLE_CHOICE:
            self.type = vote_type
            reqBody.type = self.type
            nameList = ['A', 'B', 'C', 'D', 'E', 'F']
            for element in nameList:
                option = reqBody.options_array.add()
                option.option_name = element
                option.description = ""
            reqBody.options_array[0].is_right = True
            reqBody.options_array[1].is_right = True
            reqBody.options_array[2].is_right = True
            reqBody.vote_description = ""
        elif vote_type == logical_pb2.NO_RIGHT_CHOICE:
            self.type = vote_type
            reqBody.type = self.type
            nameList = ['A', 'B', 'C', 'D', 'E']
            for element in nameList:
                option = reqBody.options_array.add()
                option.option_name = element
                option.description = ""
                option.is_right = False
            reqBody.vote_description = ""
        elif vote_type == logical_pb2.NO_RIGHT_CHOICE_MULTI:
            self.type = vote_type
            reqBody.type = self.type
            nameList = ['A', 'B', 'C', 'D', 'E', 'F']
            for element in nameList:
                option = reqBody.options_array.add()
                option.option_name = element
                option.description = ""
                option.is_right = False
            reqBody.vote_description = ""
        elif vote_type == logical_pb2.NO_RIGHT_SURVEY:
            self.type = vote_type
            reqBody.type = self.type
            nameList = ['yes', 'no']
            for element in nameList:
                option = reqBody.options_array.add()
                option.option_name = element
                option.description = ""
                option.is_right = False
            reqBody.vote_description = u"上课能够听懂吗"
        else:
            pass

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        voteMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        VotestartMessage = struct.pack('!IH', Msg_len, Msg_flag) + voteMessage
        return VotestartMessage

    #### 停止答题封包
    def pack_voteStop(self, token, question_id):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.VOTE_STOP_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101001301
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.vote_stop
        reqBody.question_id = question_id
        reqBody.type = self.type

        # 对结束答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Message = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        StopMessage = struct.pack('!IH', Msg_len, Msg_flag) + Message
        return StopMessage