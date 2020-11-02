# -*- coding:utf-8 -*-
# @Time : 2020/9/26  下午
# @Author: zeng.li

import os
import unittest
import time
from unittest.suite import TestSuite
from common import HTMLTestRunner
from common.logger import Logger

cur_path = os.path.dirname(os.path.realpath(__file__))
log = Logger()
class mainTest():
    def add_case(caseName='testCase', rule='case*.py'):
        '''
        作用：加载所有测试用例
        :param caseName:
        :param rule:
        :return:
        '''
        case_path = os.path.join(os.getcwd(), caseName)
        if not os.path.exists(case_path): os.mkdir(case_path)
        # 待执行用例的目录
        testcase = unittest.TestSuite()
        discover = unittest.defaultTestLoader.discover(case_path, pattern=rule, top_level_dir=None)
        # discover方法筛选出来的用例，循环添加到测试套件中
        print(discover)
        for test_suite in discover:
            for test_case in test_suite:
                print(test_case)
                # 添加用例到test_case
                testcase.addTests(test_case)
        return testcase


    def run_case(self, allcase, reportName='reports'):
        """
            作用：执行所有的用例，并把执行结果写入HTML测试报告中
            :param all_case:
            :param reportName:
            :return:
        """
        now = time.strftime('%Y_%m_%d_%H_%S')
        report_path = os.path.join(cur_path, reportName)
        if not os.path.exists(report_path):
                os.mkdir(report_path)
        report_abspath = os.path.join(report_path, now + '17网校直播Android测试报告.html')
        with open(report_abspath, 'wb') as fp:
            runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='17网校直播Android测试报告', description='用例执行情况')
            runner.run(allcase)


if __name__ == '__main__':
    allCase: TestSuite = mainTest.add_case()
    mainTest().run_case(allCase)