from packet import Packet
import socket as skt
import logging
import os


logging.basicConfig()
logger = logging.getLogger('CLIENT')

class RDTClient():
      def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF) -> None:
            self.sckt = skt.socket(sckt_family, sckt_type)
            self.server = sckt_binding

            if self.sckt is None:
                  raise "Socket not available."

            self.MAX_BUFF: int = MAX_BUFF * 2 # Multiply by 2 because of the metadata
            self.ACK_OK = 'ok'
            self.ACK_NOT_OK = 'not_ok'
      

      def _ack(self):
            ...


      def request_pkt(self, file_name, CLIENT_TIMEOUT):
            self.sckt.connect(self.server)
            self.sckt.settimeout(CLIENT_TIMEOUT)
            logger.info(f'Connected > Server {self.server}')  

            # Request for file
            max_timeouts = 2
            while max_timeouts:
                  pkt = Packet(file=file_name)
                  self.sckt.send(pkt.__dump__())
                  try:
                        resp = self.sckt.recv(self.MAX_BUFF)
                        if not resp:
                              logger.warning(f'Connection with {self.server} was terminated.')
                              break
                        
                        pkt = Packet(received=resp)

                        if pkt.packet.get('status') == 'not_found':
                              logger.warn(f'{file_name} not found.')
                              break
                        elif pkt.packet.get('status') == 'file_found':
                              self.receive_file(file_name)
                              break

                  except skt.timeout:
                        logger.warn('Server timeout.')
                        max_timeouts -= 1                        


      def receive_file(self, file_name):
            self.sckt.settimeout(None) # Avoid errors on client side

            # Open buffer to be written

            # Packet capture loop
                  # Timeout policy

      