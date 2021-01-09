# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 海星奖励
class RewardClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.teacher_id = ""

    # 奖励海星逻辑函数
    def rewardLogic(self, recData):
        if recData.result_frame.code == 0:
            if recData.head_frame.msg_type == msg_type_pb2.REWARD_EVERYONE_BROADCAST:
                reward_everyone = recData.logical_frame.reward_everyone_broadcast
                print("收到全体奖励：")
                self.teacher_id = reward_everyone.teacher_id
                self.max_reward = reward_everyone.max_reward
                self.min_reward = reward_everyone.min_reward
                return True
            elif recData.head_frame.msg_type == msg_type_pb2.REWARD_REPORT_RES:
                print("上报奖励结果成功！")
                return False
            elif recData.head_frame.msg_type == msg_type_pb2.REWARD_INDIVIDUAL_BROADCAST:
                reward_individual = recData.logical_frame.reward_individual_broadcast
                self.count = reward_individual.count
                if reward_individual.to_user_id != self.userId:
                    print("%s老师发送给%s[%d]颗海星" % (reward_individual.teacher_nickname,
                                                 reward_individual.to_user_nickname, reward_individual.count))
                else:
                    print("%s老师发送给我[%d]颗海星" % (reward_individual.teacher_nickname,reward_individual.count))
                return False
            elif recData.head_frame.msg_type == msg_type_pb2.REWARD_INDIVIDUAL_P2P:
                pass
                return False
        else:
            pass

    # 上报奖励结果封包
    def pack_rewardReport(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.REWARD_REPORT_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101013017
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造上报奖励请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.reward_report
        reqBody.count = random.randint(self.min_reward, self.max_reward)
        print("获得奖励数：", reqBody.count)
        reqBody.teacher_id = self.teacher_id

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        rewardMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        reportMessage = struct.pack('!IH', Msg_len, Msg_flag) + rewardMessage
        return reportMessage