# -*- coding:utf-8 -*-
# @Time : 2020/9/26  下午
# @Author: zeng.li
from testCase.action import Action


class JionRoom(Action):


    """
    *@  ui元素
    *
    * @Author: zeng.li
    """

    def jion_room(self):
        """加入直播间"""
        self.click_text("学习")



    """
    *
    * @中层方法
   
    """

    def input_username(self):
        '''输入用户名'''
        self.click_button(self.username_loc)
        self.clear_key(self.username_loc)
        self.send_keys(self.username_loc,'13770873187')
