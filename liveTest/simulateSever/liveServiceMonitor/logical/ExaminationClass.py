# _*_ coding:utf-8 _*_

import socket
import time
from kodec import msg_type_pb2, logical_pb2
from public import IPConver
import struct
import random
import json

# 题库
class ExaminationClass(object):
    def __init__(self, userId):
        self.userId = userId
        self.examination_id = ""
        self.teacher_id = ""

    # 题库作答逻辑函数
    def examinationLogic(self, recData):
        if recData.result_frame.code == 0:
            # 收到推题广播
            if recData.head_frame.msg_type == msg_type_pb2.START_EXAMINATION_BROADCAST:
                start_examination = recData.logical_frame.start_examination_broadcast
                self.examination_id = start_examination.examination_id
                self.examination = json.loads(start_examination.examination)
                self.teacher_id = start_examination.teacher_id
                self.examination_start_time = start_examination.examination_start_time
                self.examination_type = start_examination.examination_type
                self.question_index_list = list(start_examination.question_index_list)

                # 1 单选小题，4 填空小题，5 判断小题，7 连线小题，8 归类小题，9 排序小题，10 选词填空
                self.question_type_list = list(start_examination.question_type_list)
                print("examination_id:", self.examination_id)
                # print("examination:", self.examination)
                # index = 1
                # for question in self.examination:
                #     print("question-"+str(index), question)
                #     index = index+1
                print("teacher_id:", self.teacher_id)
                print("examination_start_time:", self.examination_start_time)
                print("examination_type:", self.examination_type)
                print("question_index_list:", self.question_index_list)
                print("question_type_list:", self.question_type_list)
                return 1342
            # 停止推题
            elif recData.head_frame.msg_type == msg_type_pb2.STOP_EXAMINATION_BROADCAST:
                print("停止推题：",recData.logical_frame.stop_examination_broadcast.examination_id)
                return 1402
            # 上报答题结果
            elif recData.head_frame.msg_type == msg_type_pb2.REPORT_EXAMINATION_RESULT_RES:
                result_res = recData.logical_frame.report_examination_result_res
                print("上报答题结果成功, examination_id: %s; question_index: %d; reward_count: %d"
                      % (result_res.examination_id,result_res.question_index,result_res.reward_count))
                return 1421
            # 完成答卷
            elif recData.head_frame.msg_type == msg_type_pb2.STUDENT_COMPLETE_EXAMINATION_RES:
                print("完成试卷答题")
                return 1431
            #  查询当前是否有未完成题库试卷答题在进行中
            elif recData.head_frame.msg_type == msg_type_pb2.CHECK_EXAMINATION_STATUS_RES:
                check_res = recData.logical_frame.check_examination_status_res
                if not check_res.examination_id:
                    pass
                else:
                    self.examination_id = check_res.examination_id
                    return 1471
            # 根据 id 查询题库试卷详情信息
            elif recData.head_frame.msg_type == msg_type_pb2.GET_EXAMINATION_BY_ID_RES:
                get_examination_by_id = recData.logical_frame.get_examination_by_id_res
                self.examination_id = get_examination_by_id.examination_id
                self.examination = json.loads(get_examination_by_id.examination)
                self.teacher_id = get_examination_by_id.teacher_id
                self.examination_start_time = get_examination_by_id.examination_start_time
                self.examination_type = get_examination_by_id.examination_type
                self.question_index_list = list(get_examination_by_id.question_index_list)
                # 1 单选小题，4 填空小题，5 判断小题，7 连线小题，8 归类小题，9 排序小题，10 选词填空, 16 主观作业题
                self.question_type_list = list(get_examination_by_id.question_type_list)
                self.examination_answers = get_examination_by_id.examination_answers
                # print("examination:", self.examination)
                print("examination_id:", self.examination_id)
                print("teacher_id:", self.teacher_id)
                print("question_index_list:", self.question_index_list)
                print("question_type_list:", self.question_type_list)
                return 1481
        else:
            print ("试卷处理报错：", recData.result_frame.code, recData.result_frame.msg)

    # 上报题库答题结果封包
    def pack_Examinationresult(self, token, question_index, result, examination_options, examination_answer):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.REPORT_EXAMINATION_RESULT_REQ
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
        reqBody = req_message.report_examination_result_req
        reqBody.examination_id = self.examination_id
        reqBody.question_index = question_index
        reqBody.is_right = result
        for option in examination_options:
            reqBody.examination_options.append(option)
        reqBody.teacher_id = self.teacher_id
        reqBody.examination_answer = examination_answer
        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        resultMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return resultMessage

    # 学生完成试卷封包函数
    def pack_completeExamination(self, token, answer,score):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.STUDENT_COMPLETE_EXAMINATION_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.student_complete_examination_req
        reqBody.examination_id = self.examination_id
        reqBody.examination_answer = answer
        reqBody.examination_score = score
        reqBody.examination_start_time = self.examination_start_time

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        completeMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return completeMessage

    # 查询当前是否有未完成题库试卷答题在进行中
    def pack_checkExaminationstatus(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.CHECK_EXAMINATION_STATUS_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.check_examination_status_req

        # 对请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        checkMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return checkMessage

    # 根据id查询题库试卷详情信息封包
    def pack_getExaminationbyid(self, token, examination_id):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.GET_EXAMINATION_BY_ID_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 4
        reqCommFrame.version = 101000012
        reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        # 构造答题请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.get_examination_by_id_req
        reqBody.examination_id = examination_id

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        getexamMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqPack.SerializeToString()
        return getexamMessage