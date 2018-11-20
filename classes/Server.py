import os
import selectors
import socket
from threading import Thread

from .ClientList import ClientList


class Server(Thread):
    def __init__(self):
        super(Server, self).__init__()
        self._sock = socket.socket()
        self._selector = selectors.DefaultSelector()
        self.client_list = ClientList(self)

    def run(self):
        sock = self._sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        sock.setblocking(0)
        sock.bind(('', 8000))
        sock.listen(100)

        selector = self._selector
        self.add_handler(sock.fileno(), self._accept, selectors.EVENT_READ)

        while True:
            events = selector.select(1)
            for key, event in events:
                handler, param = key.data
                if param:
                    print(param)
                    handler(**param)
                else:
                    handler()

    def _accept(self):
        for i in range(100):
            try:
                conn, address = self._sock.accept()
            except OSError:
                break
            else:
                conn.setblocking(0)
                print('%s:%d Enter' % address)
                self.client_list.add_client(conn)

    def add_handler(self, fd, handler, event, data=None):
        self._selector.register(fd, event, (handler, data))

    def remove_handler(self, fd):
        self._selector.unregister(fd)

    def send_file(self, filename):
        filename = os.path.basename(filename)
        filepath = 'files/' + filename
        if not os.path.exists(filepath):
            print('%s not exists' % filename)
            return

        self.client_list.send_file(filename, open(filepath, 'rb').read())
