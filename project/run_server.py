from server.api import RDTServer
import socket as skt
import asyncio

MAX_BUFF_SIZE = 1024
server_addr = ('localhost', 8888)
SERVER_TIMOUT = 2
server = RDTServer(skt.AF_INET, skt.SOCK_DGRAM, server_addr, SERVER_TIMOUT, MAX_BUFF_SIZE)

asyncio.get_event_loop().run_until_complete(asyncio.gather(server.listen(), server.process_buffer()))