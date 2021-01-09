# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import IPConver
import struct
import random

#### 互动课件类
class CoursewareClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.courseware_id = ""
        self.courseware_exercise_id = ""
        self.current_used_config_info = list()

    # 互动题逻辑函数
    def coursewareExerciselogic(self, recData):
        if recData.result_frame.code == 0:
            # 收到获取互动课件配置信息响应
            if recData.head_frame.msg_type == msg_type_pb2.COURSEWARE_CONFIG_RES:
                courseware_config_res = recData.logical_frame.courseware_config_res
                for courseware_config in courseware_config_res.courseware_config:
                    if courseware_config.is_current_used == True:
                        # print("courseware_config:", courseware_config)
                        self.current_used_config_info.append(courseware_config)
                return 1631
            # 收到推题成功响应
            elif recData.head_frame.msg_type == msg_type_pb2.COURSEWARE_EXERCISE_START_RES:
                print("发布互动题成功：",recData.logical_frame.courseware_exercise_start_res.courseware_exercise_id)
                self.courseware_exercise_id = recData.logical_frame.courseware_exercise_start_res.courseware_exercise_id
                return 1641
            # 结束互动课件响应
            elif recData.head_frame.msg_type == msg_type_pb2.COURSEWARE_EXERCISE_STOP_RES:
                print("停止互动课件推题：", self.courseware_exercise_id)
                return 1661
        else:
            print ("互动题处理报错：", recData.result_frame.code, recData.result_frame.msg)

    # 获取互动课件配置信息
    def pack_coursewareConfigReq(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.COURSEWARE_CONFIG_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 999999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.courseware_config_req

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        configMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return configMessage

    # 互动课件老师推题
    def pack_CoursewareExerciseStart(self, token, courseware_id,courseware_url,questions_count,
                                     online_user_count,courseware_questions,page_num,countdown_seconds):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.COURSEWARE_EXERCISE_START_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造查询请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.courseware_exercise_start_req
        reqBody.courseware_id = courseware_id
        reqBody.courseware_url = courseware_url
        reqBody.questions_count = questions_count
        reqBody.online_user_count = online_user_count
        for question in courseware_questions:
            # 对复合类型（message）,调用add方法初始化新实例,再对该实例中的每一个元素进行赋值
            new_data = reqBody.courseware_questions.add()
            for answer in question.right_answer:
                new_data.right_answer.append(answer)
            new_data.question_type = question.question_type
            new_data.submit_type = question.submit_type

        reqBody.page_num = page_num
        reqBody.countdown_seconds = countdown_seconds

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        startMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return startMessage

    # 互动课件老师停止推题
    def pack_CoursewareExerciseStop(self, token, courseware_exercise_id):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.COURSEWARE_EXERCISE_STOP_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0 ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造查询请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.courseware_exercise_stop_req
        reqBody.courseware_exercise_id = courseware_exercise_id

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        exerciseStopMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return exerciseStopMessage
