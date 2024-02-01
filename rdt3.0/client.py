from packet import Packet
import socket as skt
import logging
import random
import time
import os

logging.basicConfig(level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger('CLIENT')

class RDTClient():
      def __init__(self, sckt_family, sckt_type, server_address, MAX_BUFF) -> None:
            self.sckt = skt.socket(sckt_family, sckt_type)
            self.server = server_address
            self.CORRUPT_PROB = 0.05

            if self.sckt is None:
                  raise "Socket not available."

            self.MAX_BUFF = MAX_BUFF * 3 # Multiply by 2 because of the metadata
            self.ACK_OK = 'ok'
            self.ACK_NOT_OK = 'not_ok'
      

      def _ack(self, p: Packet, ack):
            pkt = Packet(ack=ack, seq_num=p.packet.get('seq_num'))
            self.sckt.send(pkt.__dump__())

      def connect(self):
            self.sckt.connect(self.server)


      def request_pkt(self, file_name, CLIENT_TIMEOUT = 2):
            self.sckt.settimeout(CLIENT_TIMEOUT)
            logger.info(f'Connected > Server {self.server}')  

            # Request for file
            max_timeouts = 2
            while max_timeouts:
                  pkt = Packet(file_name=file_name)
                  self.sckt.send(pkt.__dump__())
                  
                  try:
                        resp = self.sckt.recv(self.MAX_BUFF)
                        resp = Packet(received=resp)

                        if not resp:
                              logger.warning(f'Connection with {self.server} was terminated.')
                              break
                        
                        print(resp.packet.get('status'))

                        if resp.packet.get('status') == 'not_found':
                              logger.warning(f'{file_name} not found.')
                              break
                        elif resp.packet.get('status') == 'file_found':
                              logger.info(f'{file_name} found.')
                              self._receive_file(file_name.split('/')[-1])
                              break

                  except skt.timeout:
                        logger.warning('Server timeout.')
                        max_timeouts -= 1                        


      def _receive_file(self, file_name):
            self.sckt.settimeout(None) # Avoid errors on client side

            # Open buffer to be written
            f_buff = open(f'./received/{file_name}', mode='wb')

            # Packet capture loop
            while True:
                  try:
                        resp = self.sckt.recv(self.MAX_BUFF)

                        if not resp:
                              logger.warning('Disconnected from server.')
                              break

                        # Check if is corrupt according to prob
                        pkt = Packet(received=resp) 
                        
                        if random.random() <= self.CORRUPT_PROB:
                              logger.warning(f'Packet {pkt.packet.get("seq_num") + 1} was corrupted...')
                              self._ack(pkt, self.ACK_NOT_OK)
                        else:
                              logger.info(f'Packet #{pkt.packet.get("seq_num") + 1} received and is ok.')
                              f_buff.write(pkt.packet.get('data'))
                              self._ack(pkt, self.ACK_OK)

                  except Exception as err:
                        logger.error(err)
                        break
            
            self.sckt.close()
            f_buff.close()      


if __name__ == '__main__':
      MAX_BUFF_SIZE = 1024
      server_addr = ('localhost', 8000)
      for file in os.listdir('./samples'):
            client = RDTClient(skt.AF_INET, skt.SOCK_STREAM, server_addr, MAX_BUFF_SIZE)
            client.connect()
            client.request_pkt(f'./samples/{file}')