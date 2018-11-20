# coding:utf-8

import struct
import time

from classes import BinStream

FILE_CONTROL_COMMAND = 1


class BaseMsg:
    def __init__(self):
        self.cmd = 0
        self.param = 0
        self.ts = int(time.time())

    def Serialize(self, stream: BinStream):
        stream.seek(0)
        stream.write(struct.pack('<bbi', self.cmd, self.param, self.ts))
        return stream.getvalue()

    def Deserialize(self, stream: BinStream):
        stream.seek(0)
        self.cmd, self.param, self.ts = struct.unpack('<bbi', stream.read(6))
        return self
