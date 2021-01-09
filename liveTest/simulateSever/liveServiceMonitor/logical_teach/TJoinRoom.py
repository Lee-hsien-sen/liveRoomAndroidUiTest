# _*_ coding:utf-8 _*_

import socket
import time
from commons.liveServiceMonitor.kodec import msg_type_pb2, logical_pb2
from commons.liveServiceMonitor.public import addMd5
from commons.liveServiceMonitor.public import IPConver
import struct
import random
import platform
from commons.liveServiceMonitor.public import globalvar
#from commons.liveServiceMonitor.public.logger import logger


#测试环境常量
app_secret = '4911898908f9d03ae7bf913f2ae16cb1'
app_id = '58eee6ac19b005fec0d848ce'

#正式环境常量
# app_secret = 'ea4958b53cd9da924e1223252d5d215b'
# app_id = '59a91c3237d3d8d28516801c'

#### 加入直播间
class JoinRoom(object):
    def __init__(self, liveId, userId, nickName, userType, roomIndex, app_id, app_secret):
        self.liveId = liveId
        self.userId = userId
        self.nickName = nickName
        self.userType = userType
        self.roomIndex = roomIndex
        self.appId = app_id
        self.appSecret = app_secret
        self.join_token = ""
        self.isForbidden = False
        self.chatDisabled = False
        self.groupChatDisabled = False
        # 新增加入房间请求、加入房间响应时间
        self.join_req_time = 0
        self.join_res_time = 0
        # 新增重新加入房间请求&响应时间
        self.rejoin_req_time = 0
        self.rejoin_res_time = 0
        # 初始化响应时间间隔
        self.join_duration = 0
        self.rejoin_duration = 0

    # 组建join请求
    def pack_joinReq(self):
        reqPack = logical_pb2.RequestPackage()
        commFrame = reqPack.head_frame
        commFrame.msg_type = msg_type_pb2.JOIN_ROOM_REQ
        commFrame.msg_no = 'wk_test_' + str(random.randint(1, 99999))  # 暂时采用随机数
        commFrame.msg_from_user_id = self.userId  # 12976231 老师ID
        commFrame.msg_to_user_id = ""
        commFrame.device_type = 0  ## 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        commFrame.version = 101001301
        # commFrame.timestamp = int(time.time() * 1000)
        commFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))

        ## 客户端系统和版本信息
        commFrame.client_info.os_name = platform.system()
        commFrame.client_info.os_version = platform.win32_ver()[0]
        commFrame.client_info.client_version = "wkai2133"
        commFrame.extended_fields['from'] = 'multiuser_test'

        # 设置请求包是否压缩标志，0 不压缩，1 压缩
        msg_flag = int('0x0000', 16)

        join_Room_message = logical_pb2.RequestMessage()
        joinRoom = join_Room_message.join_room
        joinRoom.nickname = self.nickName
        joinRoom.user_id = self.userId
        joinRoom.avatar_url = 'https://cdn.17xueba.com//pro/server/image/2018/01/20180122134340183387.png'
        joinRoom.live_id = self.liveId
        joinRoom.user_type = self.userType  # 可选值 1学生，2助教，3老师
        joinRoom.room_index = self.roomIndex
        joinRoom.timestamp = int(time.time() * 1000)
        joinRoom.app_id = self.appId

        # 将所有参数赋值给字典变量，计算签名
        para_dict = dict()
        para_dict['nickname'] = joinRoom.nickname
        para_dict['user_id'] = joinRoom.user_id
        para_dict['avatar_url'] = joinRoom.avatar_url
        para_dict['live_id'] = joinRoom.live_id
        para_dict['user_type'] = joinRoom.user_type
        para_dict['room_index'] = joinRoom.room_index
        para_dict['timestamp'] = joinRoom.timestamp
        para_dict['app_id'] = joinRoom.app_id
        joinRoom.sign = addMd5.addSign(para_dict, self.appSecret)

        # 对RequestPackage请求数据包进行序列化
        reqPack.logical_frame = join_Room_message.SerializeToString()
        joinReqPack = reqPack.SerializeToString()

        # 计算请求封包的长度
        msg_len = reqPack.ByteSize() + 2
        joinReq_message = struct.pack('!IH', msg_len, msg_flag) + joinReqPack
        return joinReq_message

    # 组建re_join请求
    def pack_rejoin(self, token):
        reqPack = logical_pb2.RequestPackage()
        commFrame = reqPack.head_frame
        commFrame.msg_type = msg_type_pb2.RE_JOIN_REQ
        commFrame.msg_no = 'wk_test_' + str(random.randint(1, 99999))  # 暂时采用随机数
        commFrame.msg_from_user_id = self.userId
        commFrame.msg_to_user_id = ""
        commFrame.device_type = 0
        commFrame.version = 101000012
        # commFrame.timestamp = int(time.time() * 1000)
        commFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        commFrame.client_info.os_name = "windows"
        commFrame.client_info.client_version = "wkai2133"
        commFrame.extended_fields['from'] = 'multiuser_test'

        # 设置请求包是否压缩标志，0 不压缩，1 压缩
        msg_flag = int('0x0000', 16)

        rejoin_message = logical_pb2.RequestMessage()
        rejoin_message.token = token
        joinRoom = rejoin_message.re_join

        # 对RequestPackage请求数据包进行序列化
        reqPack.logical_frame = rejoin_message.SerializeToString()
        rejoin_pack = reqPack.SerializeToString()

        # 计算请求封包的长度
        msg_len = reqPack.ByteSize() + 2
        final_message = struct.pack('!IH', msg_len, msg_flag) + rejoin_pack
        return final_message

    # 更改直播状态封包
    def pack_statusChange(self, token, liveStatus):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.LIVE_STATUS_CHANGE_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.live_status_change
        reqBody.status = liveStatus

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        reqMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        changeMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqMessage
        return changeMessage

    # 获取直播配置信息封包
    def pack_getLiveconfig(self, token):
        reqPack = logical_pb2.RequestPackage()
        reqCommFrame = reqPack.head_frame
        reqCommFrame.msg_type = msg_type_pb2.GET_LIVE_CONFIG_REQ
        reqCommFrame.msg_no = 'wk_tt_' + str(random.randint(1, 99999))  # 采用随机数
        reqCommFrame.msg_from_user_id = self.userId
        reqCommFrame.msg_to_user_id = ""
        reqCommFrame.device_type = 0  ### 设备类型，0 pc 1 ios 2 android 3 手机网页 4 pc网页
        reqCommFrame.version = 101000012
        # reqCommFrame.timestamp = int(time.time() * 1000)
        reqCommFrame.ip = IPConver.ip2int(socket.gethostbyname(socket.gethostname()))
        reqCommFrame.client_info.os_name = "windows"
        reqCommFrame.client_info.client_version = "wkai2133"
        reqCommFrame.extended_fields['from'] = 'multiuser_test'

        # 构造请求逻辑帧
        req_message = logical_pb2.RequestMessage()
        req_message.token = token
        reqBody = req_message.get_live_config

        # 对答题请求数据包进行序列化
        reqPack.logical_frame = req_message.SerializeToString()
        reqMessage = reqPack.SerializeToString()

        Msg_flag = int('0x0000', 16)
        # 计算请求封包的长度
        Msg_len = reqPack.ByteSize() + 2
        getconfigMessage = struct.pack('!IH', Msg_len, Msg_flag) + reqMessage
        return getconfigMessage

    def joinLogic(self, resData):
        if resData.result_frame.code == 0:
            if resData.head_frame.msg_type == msg_type_pb2.JOIN_ROOM_RES:
                # 设置加入教室响应时间戳
                self.join_res_time = int(time.time() * 1000)
                # 计算加入教室响应时间
                self.join_duration = self.join_res_time - self.join_req_time
                # 将老师加入房间时间添加到全局字典变量
                #globalvar.set_value(self.userId,{'teacher_join_duration': self.join_duration})
                globalvar.update_value(self.userId, {'teacher_join_duration': self.join_duration})
                print("老师加入教室(join_room)成功！")
                print('老师:{}, 加入教室响应耗时（毫秒）: {}'.format(self.userId, self.join_duration))
                #logger.info('老师:{}, 加入教室响应耗时（毫秒）: {}'.format(self.userId, self.join_duration))
                print("直播状态：", resData.logical_frame.join_room.live_status)
                self.join_token = resData.logical_frame.join_room.token
                self.isForbidden = resData.logical_frame.join_room.is_forbidden
                self.chatDisabled = resData.logical_frame.join_room.chat_disabled
                self.groupChatDisabled = resData.logical_frame.join_room.group_chat_disabled
                return self.join_token
            elif resData.head_frame.msg_type == msg_type_pb2.RE_JOIN_RES:
                # 设置重新加入教室响应时间
                self.rejoin_res_time = int(time.time() * 1000)
                # 计算加入教室响应时间
                self.rejoin_duration = self.rejoin_res_time - self.rejoin_req_time
                # 将老师加入房间时间添加到全局字典变量
                # globalvar.set_value(self.userId,{'teacher_join_duration': self.join_duration})
                globalvar.update_value(self.userId, {'re_join_duration': self.rejoin_duration})
                print("老师重新加入教室(re_join)成功！")
                print('老师:{}, 重新加入教室响应耗时（毫秒）: {}'.format(self.userId, self.rejoin_duration))
                #logger.info('老师:{}, 重新加入教室响应耗时（毫秒）: {}'.format(self.userId, self.rejoin_duration))
                print("直播状态：", resData.logical_frame.join_room.live_status)
                self.join_token = resData.logical_frame.re_join.token
                self.isForbidden = resData.logical_frame.re_join.is_forbidden
                self.chatDisabled = resData.logical_frame.re_join.chat_disabled
                self.groupChatDisabled = resData.logical_frame.re_join.group_chat_disabled
                return self.join_token
            # 获取直播配置
            elif resData.head_frame.msg_type == msg_type_pb2.GET_LIVE_CONFIG_RES:
                self.live_config = resData.logical_frame.get_live_config_res
        else:
            print(resData.result_frame.code, resData.result_frame.msg)
