# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 投票选择题
class DoubleTeacherRushReward(object):
    def __init__(self, teacher_id):
        self.teacher_id = teacher_id
        self.rush_reward_id = ""
        self.token = ""

    # 刷海星逻辑处理函数
    def rushrewardLogic(self, recData):
        # 判断消息返回code是否为0
        if recData.result_frame.code == 0:
            # 收到抢海星活动广播
            if recData.head_frame.msg_type == msg_type_pb2.GEN_RUSH_REWARD_BROADCAST:
                # 设置刷海星开关
                self.rush_switch = True
                print (recData.logical_frame.gen_rush_reward_broadcast)
                # 抢海星活动id
                self.rush_reward_id = recData.logical_frame.gen_rush_reward_broadcast.rush_reward_id

                # 可以抢到海星的总人数
                self.total_reward_students = \
                    recData.logical_frame.gen_rush_reward_broadcast.reward_detail.total_reward_students
                # 已抢到海星的人数
                self.taken_reward_students = \
                    recData.logical_frame.gen_rush_reward_broadcast.reward_detail.taken_reward_students
                print('可以抢到海星的总人数:{}，已经抢到海星的人数:{}'.format(
                    recData.logical_frame.gen_rush_reward_broadcast.reward_detail.total_reward_students,
                    recData.logical_frame.gen_rush_reward_broadcast.reward_detail.taken_reward_students))
                return 2112
            #
            elif recData.head_frame.msg_type == msg_type_pb2.RUSH_REWARD_NO_FINISH_P2P:
                #print (recData.logical_frame.rush_reward_no_finish_p2p.no_finish_rush_reward_list)
                # 设置刷海星开关
                self.rush_switch = True
                no_finish_rush_reward = recData.logical_frame.rush_reward_no_finish_p2p.no_finish_rush_reward_list
                if no_finish_rush_reward:
                    self.rush_reward_id = no_finish_rush_reward[0].rush_reward_id
                    return 2220
            # 学生抢海星的响应
            elif recData.head_frame.msg_type == msg_type_pb2.DO_RUSH_REWARD_RES:
                # 抢到海星数量
                self.rush_reward_taken = recData.logical_frame.do_rush_reward_res.rush_reward_taken
                print ("学生 {} 抢到 {} 颗海星".format(recData.logical_frame.do_rush_reward_res.student_id,
                                           self.rush_reward_taken))
                self.nickname = recData.logical_frame.do_rush_reward_res.nickname
                self.avatar_url = recData.logical_frame.do_rush_reward_res.avatar_url
                self.total_reward_students = recData.logical_frame.do_rush_reward_res.reward_detail.total_reward_students
                self.taken_reward_students = recData.logical_frame.do_rush_reward_res.reward_detail.taken_reward_students
                return 2121
            # 学生抢海星请求全局广播
            elif recData.head_frame.msg_type == msg_type_pb2.DO_RUSH_REWARD_BROADCAST:
                print ('可以抢到海星的总人数:{}，已经抢到海星的人数:{}'.format(
                    recData.logical_frame.do_rush_reward_broadcast.reward_detail.total_reward_students,
                    recData.logical_frame.do_rush_reward_broadcast.reward_detail.taken_reward_students))
                return 2122
            # 停止抢海星广播
            elif recData.head_frame.msg_type == msg_type_pb2.STOP_RUSH_REWARD_BROADCAST:
                # 设置刷海星开关
                self.rush_switch = False
                print("老师停止抢海星活动--{}".format(recData.logical_frame.stop_rush_reward_broadcast.rush_reward_id))
                return 2182
        else:
            print ("抢海星失败：", recData.result_frame.code, recData.result_frame.msg)

    # 抢海星封包函数
    def pack_rushReward(self, token, stu_id):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.DO_RUSH_REWARD_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 9999))  # 采用随机数
        reqCommFrame.msg_from_user_id = ""
        reqCommFrame.device_type = 0
        reqCommFrame.version = 1
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'double_teacher_test'
        reqCommFrame.extended_fields['zylive_hand_device_user_id'] = stu_id

        # 构造请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.do_rush_reward_req
        reqBody.rush_reward_id = self.rush_reward_id

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        rushMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        rushrewardMessage = struct.pack('!IH', Msg_len, Msg_flag) + rushMessage
        return rushrewardMessage
