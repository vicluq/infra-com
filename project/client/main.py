from packet import Packet
import socket as skt
import logging
import asyncio
import random
import time
import os

logging.basicConfig(level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger('CLIENT')

class RDTClient():
      def __init__(self, sckt_family, sckt_type, client_address, server_address, MAX_BUFF) -> None:
            self.sckt = skt.socket(sckt_family, sckt_type)
            self.sckt.bind(client_address)
            self.sckt.setblocking(False)

            self.server_address = server_address

            if self.sckt is None:
                  raise "Socket not available."

            self.MAX_BUFF = MAX_BUFF * 3 # Multiply by 2 because of the metadata
            self.ACK_OK = 'ok'
            self.ACK_NOT_OK = 'not_ok'

            self.close = 0


      async def _ack(self, p: Packet, ack):
            loop = asyncio.get_event_loop()
            pkt = Packet(ack=ack, seq_num=p.packet.get('seq_num'))
            await loop.sock_sendto(self.sckt, pkt.__dump__(), self.server_address)


      async def receive(self):
            self.sckt.settimeout(None)
            loop = asyncio.get_event_loop()
            buf = []
            while True:
                  try:
                        received, addr = await loop.sock_recvfrom(self.sckt, self.MAX_BUFF)

                        p = Packet(received=received)
                        if p.packet['total'] == p.packet['seq_num']:
                              self.sckt.settimeout(None) # Done receiving
                              buf.append(p.packet['data'])
                              buf = b''.join(buf).decode()
                              print(buf)
                              buf = [] # Reset
                        else:
                              self.sckt.settimeout(2) # Start receving
                              buf.append(p.packet['data'])
                              logger.info(f'Received pkt #{p.packet['seq_num']} out of {p.packet['total']}')
                        
                        await self._ack(p, self.ACK_OK)
                  except skt.timeout:
                        await self._ack(p, self.ACK_NOT_OK)
                        continue


      async def send_command(self):
            loop = asyncio.get_event_loop()
            while True:
                  command = await asyncio.get_event_loop().run_in_executor(
                        None,
                        input,
                  )

                  print(f"Sent > {command} to {self.server_address}")
                  await loop.sock_sendto(self.sckt, 
                                         Packet(msg=command.encode()).__dump__(), 
                                         self.server_address)
