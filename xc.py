# coding:utf-8
from classes.Server import Server

server = Server()
server.start()

while True:
    data = input('Send File: ')
    server.send_file(data)