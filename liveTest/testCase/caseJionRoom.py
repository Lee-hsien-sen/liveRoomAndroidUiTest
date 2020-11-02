# -*- coding:utf-8 -*-
# @Time : 2020/9/26  下午
# @Author: zeng.li

import unittest
from pages.JionRoomPage import JionRoom


class CaseJionRoom(JionRoom,unittest.TestCase):

    def test_case_login(self):
        pass


    def test_case_B(self):
        # self.wd.find_element_by_id("bbad86fd-191b-4c87-a6d6-67613417577b").click()
        print('run B')


    def test_case_A(self):
        print('run A')

    def test_case_C(self):
        print('run C')

