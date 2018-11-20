# coding:utf-8
import socket

from classes import BinStream
from classes import RSAEncryptor
from classes.Compressor import Compressor
from message import *


def wrap_data(data):
    return struct.pack('<i', len(data)) + data


class Client:
    def __init__(self):
        self.conn = socket.socket()
        self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.conn.connect(('127.0.0.1', 8000))

        self.encryptor = RSAEncryptor()
        self.encryptor.new_key()
        self.data_len = 4
        self.head = True
        self.data_buff = b''
        self.compressor = Compressor()
        self.first_start = True

    def read(self):
        if self.head and len(self.data_buff) == 4:
            self.data_len = struct.unpack('<i', self.data_buff)[0]
            self.data_buff = b''
            self.head = False
        else:
            if len(self.data_buff) < self.data_len:
                data = self.conn.recv(1)
                if data:
                    self.data_buff += data
            else:
                return True
        return False

    def recv(self):
        while True:
            if self.read():
                self.data_len = 4
                data = self.data_buff
                self.data_buff = b''
                self.head = True

                if data:
                    if self.first_start:
                        self.encryptor.load_der_public_key(data)
                        self.first_start = False
                        print('Initialization Success')
                    else:
                        self.handle_msg(BinStream(data))

    def handle_msg(self, data):
        msg = BaseMsg().Deserialize(data)
        if msg.cmd == FILE_CONTROL_COMMAND:
            if msg.param == FILE_SEND_DATA:
                msg = SendFileMsg().Deserialize(data)
                decompress_data = self.compressor.decompress(msg.compress_method, msg.data)

                with open(msg.filename.decode() + '_recv', 'wb') as fp:
                    _file_content = self.encryptor.rsa_decrypt(decompress_data)
                    fp.write(_file_content)
                    print('Recv', msg.filename.decode(), len(msg.data))

            elif msg.param == FILE_RET_OK:
                print('Recv OK')
                exit()
            elif msg.param == FILE_RET_FAILED:
                msg = ReturnFileMsg().Deserialize(data)
                print('Recv Failed', msg.reason)
                exit()
            else:
                print('UNKNOWN PARAM:', msg.param)

        else:
            print('UNKNOWN COMMAND:', msg.cmd)

    def send(self, data):
        data = wrap_data(data)
        total_sent = 0
        while total_sent < len(data):
            sent = self.conn.send(data[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent
        self.conn.send(wrap_data(b''))

    def send_file(self, filename, filedata):
        en_data = self.encryptor.rsa_encrypt(filedata)
        t = SendFileMsg()
        t.filename = filename.encode()
        t.data = en_data
        t.compress_method = 0

        self.send(t.Serialize(BinStream()))


client = Client()
client.send(client.encryptor.dump_der_public_key())
client.recv()
