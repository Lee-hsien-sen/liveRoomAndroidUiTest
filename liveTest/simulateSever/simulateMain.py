import threading
import os
import time
import sys
from simulateSever.liveServiceMonitor.kodec import logical_pb2
from simulateSever.liveServiceMonitor.teacher import Teacher
from simulateSever.liveServiceMonitor.public import globalvar
import simulateSever.student.method as studentmethod



if __name__ == '__main__':

    roomID = 34361
    nickname = "直播测试"
    user_type = 3  # 可选值 1学生，2助教，3老师 4 监课 5 超级管理员
    msn_ip = "10.200.241.44"
    # 5f6b05c9b1d3056655577709 5f714ee253ffbd39c9e6e10c
    liveID = "5f6b05c9b1d3056655577709"
    tea_UID = "123"
    teacher_a = Teacher.Teacher(liveID, tea_UID, user_type, nickname, roomID, msn_ip)

    globalvar._init()
    globalvar.set_value(tea_UID, {'uid': tea_UID, 'user_type': user_type, 'msn_ip': msn_ip})
    teacher_a.do_join()
    time.sleep(2)
    teacher_a.do_changeStatus(logical_pb2.LIVE_STATUS_START)
    stu = studentmethod.Method(live_id=liveID)
    num = 3
    stu.openstudentend(num)
    while True:
        index = input("本次执行的操作： 1：连对后错 2：连错 3：退出")
        index = int(index)
        if index == 1:
            num1 = int(input('几连对后错'))
            for j in range(num1):
                teacher_a.do_vote(logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE, "等待")
                time.sleep(1)
                for i in range(num):
                    stu.driver.switch_to.window(stu.windows[stu.userList[i][1]+'_'+stu.userList[i][0]])
                    stu.hasChangeFrame
                    stu.closeMVPbutton()
                    stu.ansChoiceQ()
                teacher_a.stop_vote()
                # for i in range(num):
                #     stu.driver.switch_to.window(stu.windows[stu.userList[i][1]+'_'+stu.userList[i][0]])
                #     stu.hasChangeFrame
                #     stu.sendChat('我是'+str(j+1)+'连对')
            teacher_a.do_vote(logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE, "等待")
            for i in range(num):
                stu.driver.switch_to.window(stu.windows[stu.userList[i][1]+'_'+stu.userList[i][0]])
                stu.hasChangeFrame
                stu.closeMVPbutton()
                stu.ansChoiceQ(isright=False)
            teacher_a.stop_vote()
            # for i in range(num):
            #     stu.driver.switch_to.window(stu.windows[stu.userList[i][1]+'_'+stu.userList[i][0]])
            #     stu.closeMVPbutton()
            #     stu.sendChat('我是5连对后错的')
        elif index == 2:
            num1 = int(input('连错'))
            for j in range(num1):
                teacher_a.do_vote(logical_pb2.SIGNLE_RIGHT_FOUR_CHOICE, "等待")
                for i in range(num):
                    stu.driver.switch_to.window(stu.windows[stu.userList[i][1]+'_'+stu.userList[i][0]])
                    stu.hasChangeFrame
                    stu.closeMVPbutton()
                    stu.ansChoiceQ(isright=False)
                teacher_a.stop_vote()
        else:
            sys.exit(0)

    time.sleep(10)

    teacher_a.do_leave()
