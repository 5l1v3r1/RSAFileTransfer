# coding:utf-8
from classes.compressor import *

COMPRESS_NONE = 0
COMPRESS_GZIP = 1


class UnknownCompressorException(Exception):
    pass


class Compressor:
    def __init__(self):
        self.compressors = {
            COMPRESS_NONE: CompressBase,
            COMPRESS_GZIP: CompressGZIP
        }

    def compress(self, method, data):
        if method not in self.compressors:
            raise UnknownCompressorException()
        return self.compressors[method].compress(data)

    def decompress(self, method, data):
        if method not in self.compressors:
            raise UnknownCompressorException()
        return self.compressors[method].decompress(data)
