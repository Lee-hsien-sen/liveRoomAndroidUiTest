# -*- coding:utf-8 -*-
# @Time : 2020/9/26  下午
# @Author: zeng.li

import os
import time
import logging
from logging import handlers

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def console(self, level, message):
        self.now = time.strftime('%Y_%m_%d')
        cur_path = os.path.dirname(os.path.realpath(__file__))
        log_path = os.path.join(os.path.dirname(cur_path), 'logs')
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        filename = os.path.join(log_path, self.now + '__17androidTest.log')
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')#设置日志格式
        self.logger.setLevel(self.level_relations.get('debug'))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when='D', backupCount=3, encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器

        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)

        if level == 'info':
            self.logger.info(message)
        elif level == 'debug':
            self.logger.debug(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)

        # 避免日志重复输出
        self.logger.removeHandler(sh)
        self.logger.removeHandler(th)
        sh.close()

    def info(self, message):
        self.console('info', message)

    def debug(self, message):
        self.console('debug', message)

    def warning(self, message):
        self.console('warning', message)

    def error(self, message):
        self.console('error', message)

