# coding:utf-8
import socket

from classes import BinStream
from message import SendFileMsg
from .Client import Client

EVENT_READ = (1 << 0)
EVENT_WRITE = (1 << 1)


class ClientExistException(Exception):
    def __init__(self):
        super(ClientExistException, self).__init__()


class ClientNotExistException(Exception):
    def __init__(self):
        super(ClientNotExistException, self).__init__()


class ClientList:
    def __init__(self, server):
        self.server = server
        self.clients = {}

    def __getitem__(self, item):
        if isinstance(item, str):
            key = str
        elif isinstance(item, socket.socket):
            key = '%s:%d' % item.getpeername()
        else:
            key = ''
        if key in self.clients:
            return self.clients[key]
        else:
            return None

    def add_client(self, conn: socket.socket):
        addr = conn.getpeername()
        if addr in self.clients.keys():
            raise ClientExistException()

        client = Client(self, conn)

        self.server.add_handler(conn.fileno(), client.recv, EVENT_READ)
        self.clients[addr] = client

    def del_client(self, conn: socket.socket):
        addr = conn.getpeername()
        if addr not in self.clients.keys():
            raise ClientNotExistException()

        self.server.remove_handler(conn.fileno())
        del self.clients[addr]

    def get_client(self, conn: socket.socket):
        addr = conn.getpeername()
        if addr not in self.clients.keys():
            raise ClientNotExistException()

        return self.clients[addr]

    def send_to(self, conn: socket.socket, msg):
        conn.send(msg)

    def send_all(self, msg):
        for conn in self.clients:
            if conn._closed:
                continue
            conn.send(msg)

    def send_file(self, filename, filedata):
        for client in self.clients.values():
            if client.conn._closed:
                continue
            en_data = client.encryptor.rsa_encrypt(filedata)
            t = SendFileMsg()
            t.filename = filename.encode()
            t.data = en_data
            t.compress_method = 0
            client.send(t.Serialize(BinStream()))
