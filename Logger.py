#coding:utf-8

import os
import sys
import logging

# 暂时不使用级别
# format_dict = {
#    1 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
#    2 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
#    3 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
#    4 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
#    5 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# }

# 只有继承object才有__new__的方法
class Logger(object):
    __instance = None
    __exename = None
    __init_flage = False

    def __new__(cls, *args, **kw): # __new__无法避免触发__init__()
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kw)
        return cls.__instance
    
    '''
        指定保存日志的文件路径，日志级别，以及调用文件
        将日志存入到指定的文件中
    '''
    def __init__(self):
        if self.__init_flage:
            return None

        self.__getexename()

        # 创建一个logger
        self.logger = logging.getLogger(self.__exename)
        self.logger.setLevel(logging.DEBUG)
        
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler('%s.log'%self.__exename)
        fh.setLevel(logging.DEBUG)
        
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.__startexe()
        self.logger.addHandler(ch)

    def __startexe(self):
        self.__init_flage = True
        self.logger.info('<========== start %s ==========>'%self.__exename)

    def __getexename(self):
        self.__exename = sys.argv[0].split('\\')[-1].split('.')[0]

    def getlogs(self):
        return self.logger

def GetLog():
    return Logger().getlogs()