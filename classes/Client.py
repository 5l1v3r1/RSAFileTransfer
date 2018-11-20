# coding:utf-8
import socket

from message import *
from .BinaryStream import BinStream
from .Compressor import Compressor
from .RSAEncryptor import RSAEncryptor


class Client:
    def __init__(self, clients, conn: socket.socket):
        self.clients = clients
        self.conn = conn
        self.data_len = 4
        self.head = True
        self.data_buff = b''
        self.encryptor = RSAEncryptor()
        self.encryptor.new_key()
        self.compressor = Compressor()
        self.first_start = True

    def close(self):
        # self.conn.shutdown(socket.SHUT_RDWR)
        print('%s:%d Exit' % self.conn.getpeername())
        self.clients.del_client(self.conn)
        self.conn.close()

    def read(self):
        if self.head and len(self.data_buff) == 4:
            self.data_len = struct.unpack('<i', self.data_buff)[0]
            self.data_buff = b''
            self.head = False
        else:
            if len(self.data_buff) < self.data_len:
                self.data_buff += self.conn.recv(1)
            else:
                return True
        return False

    def recv(self):
        try:
            if not self.read():
                return
            self.data_len = 4
            data = self.data_buff
            self.data_buff = b''
            self.head = True
            if data:
                if self.first_start:
                    self.send(self.encryptor.dump_der_public_key())
                    self.encryptor.load_der_public_key(data)
                    self.first_start = False
                else:
                    self.handle_msg(BinStream(data))
        except ConnectionResetError as e:
            self.close()

    def send(self, data):
        data = self.wrap_data(data)
        MSGLEN = len(data)
        total_sent = 0
        while total_sent < MSGLEN:
            sent = self.conn.send(data[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent
        self.conn.send(self.wrap_data(b''))

    def handle_msg(self, data):
        msg = BaseMsg().Deserialize(data)
        if msg.cmd == FILE_CONTROL_COMMAND:
            if msg.param == FILE_SEND_DATA:
                msg = SendFileMsg().Deserialize(data)
                self.encryptor.rsa_verify(msg.signature, msg.data)
                decompress_data = self.compressor.decompress(msg.compress_method, msg.data)

                with open(msg.filename, 'wb') as fp:
                    _file_content = self.encryptor.rsa_decrypt(decompress_data)
                    fp.write(_file_content)
                    print('Recv', msg.filename, len(msg.data))

                self.send(ReturnFileMsg().Serialize(BinStream()))

            elif msg.param == FILE_RET_OK:
                print('Recv OK')
            elif msg.param == FILE_RET_FAILED:
                msg = ReturnFileMsg().Deserialize(data)
                print('Recv Failed', msg.reason)
            else:
                print('UNKNOWN PARAM:', msg.param)

        else:
            print('UNKNOWN COMMAND:', msg.cmd)

    @staticmethod
    def wrap_data(data):
        return struct.pack('<i', len(data)) + data
