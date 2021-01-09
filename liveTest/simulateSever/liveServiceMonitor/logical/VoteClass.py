# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random
from public import globalvar
from public.logger import logger

# 投票选择题
class VoteClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.questionId = ""
        self.teaId = ""
        self.type = 0
        self.token = ""
        self.choice = list()
        self.rightOptions = list()
        # 新增答题开始请求、开始响应时间变量
        self.start_req_time = 0
        self.start_res_time = 0

    # 投票逻辑处理函数
    def voteLogic(self, recData):
        self.choice = []
        self.rightOptions = []
        if recData.result_frame.code == 0:
            # 处理4个选项单选广播
            if recData.head_frame.msg_type == msg_type_pb2.VOTE_START_BROADCAST:
                # 收到答题，赋值题目参数
                self.questionId = recData.logical_frame.vote_start_broadcast.question_id
                self.teaId = recData.logical_frame.vote_start_broadcast.teacher_id
                self.type = recData.logical_frame.vote_start_broadcast.type
                # 设置双师答题器倒计时
                if recData.logical_frame.vote_start_broadcast.t_minus:
                    self.t_minus = recData.logical_frame.vote_start_broadcast.t_minus
                # 设置双师选择题难度
                if recData.logical_frame.vote_start_broadcast.currency_channel_name:
                    self.currency_channel_name = recData.logical_frame.vote_start_broadcast.currency_channel_name

                for option in recData.logical_frame.vote_start_broadcast.options_array:
                    self.choice.append(option.option_name)
                    if option.is_right == True:
                        self.rightOptions.append(option.option_name)
                print(self.choice)
                print(self.rightOptions)
                return True
            # 处理单选大于4个、不定项选择、单项投票、不定项投票广播、快速调查题
            elif recData.head_frame.msg_type == msg_type_pb2.VOTE_START_NEW_BROADCAST:
                # 收到答题，赋值题目参数
                self.questionId = recData.logical_frame.vote_start_new_broadcast.question_id
                self.teaId = recData.logical_frame.vote_start_new_broadcast.teacher_id
                self.type = recData.logical_frame.vote_start_new_broadcast.type
                # 判断是否是快速调查，类型为6
                if self.type == logical_pb2.NO_RIGHT_SURVEY:
                    self.vote_description = recData.logical_frame.vote_start_new_broadcast.vote_description

                # 设置双师答题器倒计时
                if recData.logical_frame.vote_start_broadcast.t_minus:
                    self.t_minus = recData.logical_frame.vote_start_new_broadcast.t_minus
                # 设置双师选择题难度
                if recData.logical_frame.vote_start_broadcast.currency_channel_name:
                    self.currency_channel_name = recData.logical_frame.vote_start_new_broadcast.currency_channel_name

                for option in recData.logical_frame.vote_start_new_broadcast.options_array:
                    self.choice.append(option.option_name)
                    if option.is_right == True:
                        self.rightOptions.append(option.option_name)
                print(self.choice)
                print(self.rightOptions)
                return True
            # 提交答案后处理答题响应
            elif recData.head_frame.msg_type == msg_type_pb2.SUBMIT_VOTE_RES:
                # 设置答题响应时间
                self.start_res_time = int(time.time() * 1000)
                # 计算答题响应时间
                self.submit_duration = self.start_res_time - self.start_req_time
                globalvar.update_value(self.userId, {'vote_submit_duration': self.submit_duration})
                print('用户:{}  答题响应耗时（毫秒）: {}'.format(self.userId, self.submit_duration))
                logger.info('用户:{}  答题响应耗时（毫秒）: {}'.format(self.userId, self.submit_duration))
                # print (recData.logical_frame.vote_submit_res.reward_count,
                #        recData.logical_frame.vote_submit_res.type)
                self.type = recData.logical_frame.vote_submit_res.type
                if self.type in [logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE,
                                 logical_pb2.SIGNLE_RIGHT_MULTIPLE_CHOICE,
                                 logical_pb2.MULTIPLE_CHOICE,
                                 logical_pb2.OTHER]:
                    if recData.logical_frame.vote_submit_res.reward_count == 5:
                        print("回答正确！奖励5颗海星~")

                    else:
                        print("回答错误！请再接再厉~")

                else:
                    print("投票成功！")
                return False
            elif recData.head_frame.msg_type == msg_type_pb2.VOTE_STOP_BROADCAST:
                print("结束选择答题！")
                return False
        else:
            print ("答题失败：", recData.result_frame.code, recData.result_frame.msg)

    # 提交投票封包函数
    def pack_submitVote(self, token, submitOptions):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.SUBMIT_VOTE_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 9999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        #reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.submit_vote
        reqBody.question_id = self.questionId

        if len(submitOptions) != 0:
            for name in submitOptions:
                # reqBody.option_names.extend(name)
                reqBody.option_names.append(name)

            if submitOptions == self.rightOptions:
                reqBody.is_right = True
            else:
                reqBody.is_right = False
        else:
            print ("提交的选项为空！")

        reqBody.teacher_id = self.teaId
        reqBody.type = self.type

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        voteMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        submitVoteMessage = struct.pack('!IH', Msg_len, Msg_flag) + voteMessage
        return submitVoteMessage
