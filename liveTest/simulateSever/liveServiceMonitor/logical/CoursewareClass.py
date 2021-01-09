# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random

# 互动课件
class CoursewareClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.courseware_id = ""
        self.courseware_exercise_id = ""

    # 互动题逻辑函数
    def coursewareExerciselogic(self, recData):
        if recData.result_frame.code == 0:
            # 收到互动课件推题广播
            if recData.head_frame.msg_type == msg_type_pb2.COURSEWARE_EXERCISE_START_BROADCAST:
                courseware_exercise_start = recData.logical_frame.courseware_exercise_start_broadcast
                self.courseware_exercise_id = courseware_exercise_start.courseware_exercise_id
                self.courseware_id = courseware_exercise_start.courseware_id
                self.courseware_url = courseware_exercise_start.courseware_url
                self.questions_count = courseware_exercise_start.questions_count
                self.page_num  = courseware_exercise_start.page_num
                self.courseware_questions = courseware_exercise_start.courseware_questions
                self.countdown_seconds = courseware_exercise_start.countdown_seconds
                self.courseware_exercise_start_time = courseware_exercise_start.courseware_exercise_start_time
                self.exercise_over = False
                print("courseware_exercise_id:", self.courseware_exercise_id)
                print("courseware_id:", self.courseware_id)
                print("courseware_url:", self.courseware_url)
                print("questions_count:", self.questions_count)
                print("page_num:", self.page_num)
                print("courseware_questions:", self.courseware_questions)
                print("countdown_seconds:", self.countdown_seconds)
                print("courseware_exercise_start_time:", self.courseware_exercise_start_time)
                return 1632
            # 收到互动课件停止推题广播
            elif recData.head_frame.msg_type == msg_type_pb2.COURSEWARE_EXERCISE_STOP_BROADCAST:
                print("结束互动题：",recData.logical_frame.courseware_exercise_stop_broadcast.courseware_exercise_id)
                self.exercise_over = True
                return 1662
            # 回答互动课件问题响应
            elif recData.head_frame.msg_type == msg_type_pb2.COURSEWARE_QUESTION_REPORT_RES:
                question_report_res = recData.logical_frame.courseware_question_report_res
                print("提交互动题成功, 获得海星数: %d" % (question_report_res.reward_count))
                return 1651
            # 查询是否有未完成互动课件练习
            elif recData.head_frame.msg_type == msg_type_pb2.CHECK_COURSEWARE_EXERCISE_STATUS_RES:
                check_courseware_exercise_status = recData.logical_frame.check_courseware_exercise_status_res
                self.courseware_exercise_id = check_courseware_exercise_status.courseware_exercise_id
                if self.courseware_exercise_id != "":
                    self.courseware_id = check_courseware_exercise_status.courseware_id
                    self.courseware_url = check_courseware_exercise_status.courseware_url
                    self.questions_count = check_courseware_exercise_status.questions_count
                    self.courseware_questions = check_courseware_exercise_status.courseware_questions
                    self.page_num = check_courseware_exercise_status.page_num
                    self.countdown_seconds = check_courseware_exercise_status.countdown_seconds
                    self.courseware_exercise_start_time = check_courseware_exercise_status.courseware_exercise_start_time
                    self.answered_questions = check_courseware_exercise_status.answered_questions
                    print (self.courseware_questions)
                    print (self.answered_questions)
                    self.exercise_over = False
                    return 1691
                else:
                    pass
        else:
            print ("互动题处理报错：", recData.result_frame.code, recData.result_frame.msg)

    # 学生提交互动题
    def pack_coursewareQuestionReport(self, token, courseware_exercise_id, question_index, courseware_exercise_answers,right_answers,
                                      courseware_question_type,complete_level, submit_type, retry_times, wrong_answer_history):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.COURSEWARE_QUESTION_REPORT_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        #reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.courseware_question_report_req
        reqBody.courseware_exercise_id = courseware_exercise_id
        reqBody.courseware_id = self.courseware_id
        reqBody.question_index = question_index

        for element in courseware_exercise_answers:
            reqBody.courseware_exercise_answers.append(element)

        for answer in right_answers:
            reqBody.courseware_exercise_right_answers.append(answer)
        reqBody.courseware_question_type = courseware_question_type
        reqBody.complete_level = complete_level
        reqBody.page_num = self.page_num
        reqBody.original_answer_json = ""
        # 设置重试次数和错误答案历史
        reqBody.retry_times = retry_times
        for wrong_answer in wrong_answer_history:
            reqBody.wrong_answer_history.append(wrong_answer)
        reqBody.submit_type = submit_type
        reqBody.courseware_exercise_start_time = self.courseware_exercise_start_time

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        reportMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return reportMessage

    # 封装查询是否有未完成互动课件练习
    def pack_checkExercisestatus(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.CHECK_COURSEWARE_EXERCISE_STATUS_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造查询请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.check_courseware_exercise_status_req

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        checkMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return checkMessage