# coding:utf-8
import gzip

from .CompressBase import CompressBase


class CompressGZIP(CompressBase):
    @staticmethod
    def compress(data):
        return gzip.compress(data)

    @staticmethod
    def decompress(data):
        return gzip.decompress(data)
