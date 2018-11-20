# coding:utf-8
from classes import BinStream
from .FileMsg import FileMsg, FILE_RET_OK

FILE_REASON_NONE = 0
FILE_REASON_EXIST = 1
FILE_REASON_NO_SPACE = 2


class ReturnFileMsg(FileMsg):
    def __init__(self):
        super(ReturnFileMsg, self).__init__()
        self.param = FILE_RET_OK
        self.reason = FILE_REASON_NONE

    def Serialize(self, stream: BinStream):
        super(ReturnFileMsg, self).Serialize(stream)
        stream.writeChar(self.reason)
        return stream.getvalue()

    def Deserialize(self, stream: BinStream):
        super(ReturnFileMsg, self).Deserialize(stream)
        self.reason = stream.readChar()
        return self
