# coding:utf-8

from .BaseMsg import BaseMsg, FILE_CONTROL_COMMAND

FILE_SEND_DATA = 1
FILE_DELETE = 2
FILE_LIST = 3

FILE_RET_OK = 4
FILE_RET_FAILED = 5


class FileMsg(BaseMsg):
    def __init__(self):
        super(FileMsg, self).__init__()
        self.cmd = FILE_CONTROL_COMMAND
