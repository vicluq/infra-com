from client.main import RDTClient
import socket as skt
import argparse
import asyncio

parser = argparse.ArgumentParser()
parser.add_argument('--port', '-p')

args = parser.parse_args()

MAX_BUFF_SIZE = 1024
server_addr = ('127.0.0.1', 8888)
client_addr = ('127.0.0.1', int(args.port))
SERVER_TIMOUT = 2
server = RDTClient(skt.AF_INET, skt.SOCK_DGRAM, client_addr, server_addr, MAX_BUFF_SIZE)

asyncio.get_event_loop().run_until_complete(asyncio.gather(server.send_command(), server.receive()))