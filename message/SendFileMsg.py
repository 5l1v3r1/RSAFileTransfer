# coding:utf-8
from classes import BinStream
from .FileMsg import FileMsg, FILE_SEND_DATA


class SendFileMsg(FileMsg):
    def __init__(self):
        super(SendFileMsg, self).__init__()
        self.param = FILE_SEND_DATA
        self.compress_method = 0
        self.filename = b''
        self.data = b''

    def Serialize(self, stream: BinStream):
        super(SendFileMsg, self).Serialize(stream)
        stream.writeChar(self.compress_method)
        stream.writeString(self.filename)
        stream.writeString(self.data)
        return stream.getvalue()

    def Deserialize(self, stream: BinStream):
        super(SendFileMsg, self).Deserialize(stream)
        self.compress_method = stream.readChar()
        self.filename = stream.readString()
        self.data = stream.readString()
        return self
