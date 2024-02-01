from packet import Packet
import threading
import socket as skt
import logging
import random
import os


logging.basicConfig(level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger('SERVER')


class RDTServer:
      def __init__(self, sckt_family, sckt_type, sckt_binding, sckt_timeout, MAX_BUFF) -> None:
            self.sckt = skt.socket(sckt_family, sckt_type)
            self.sckt.bind(sckt_binding) # Binding this address to the server
            self.LOSS_PROB = 0.05 # Packet loss prob
            self.TIMEOUT = sckt_timeout
            
            if self.sckt is None:
                  raise "Socket not available."

            self.MAX_BUFF: int = MAX_BUFF
            self.active_conn = 0

            self.ACK_OK = 'ok'
            self.ACK_NOT_OK = 'not_ok'
 
      def listen(self):
            try:
                  self.sckt.listen()
                  while True:
                        client, addr = self.sckt.accept() # Await for connection
                        client.settimeout(self.TIMEOUT)
                        print(client)
                        thread = threading.Thread(target=self.serve_client, args=[client, addr])
                        self.active_conn += 1
                        thread.start()
                        
                        logger.info(f'New connection @ {addr} | Total Conn = {self.active_conn}')

            except Exception as err:
                  logger.error(err)
            except KeyboardInterrupt:
                  exit(1)

      
      def wait_for_pckt_req(self, client: skt.socket) -> Packet:
            client.settimeout(self.TIMEOUT)
            max_timeouts = 2
            
            while max_timeouts:
                  try:
                        pckt_req = client.recv(self.MAX_BUFF)
                        if pckt_req:
                              p = Packet(received=pckt_req)
                              logger.info(f'Client Packet Received.')
                              return p
                  except skt.timeout:
                        max_timeouts -= 1
            
            return 0 # timeout
            

      def send_data(self, client: skt.socket, pckt: Packet):
            max_timeouts = 2
            max_retry = 3

            while max_timeouts:
                  if random.random() > self.LOSS_PROB:
                        client.send(pckt.__dump__())
                  elif max_retry:
                        logger.warning(f'Packet was lost {pckt.packet.get('seq_num') + 1}')
                        max_retry -= 1

                  try:
                        resp = client.recv(self.MAX_BUFF) # Receive the ack 'ok' or 'not ok' pckt
                        
                        if not resp:
                              logger.info(f"Client disconnected.")
                              return 0

                        rcv_packt = Packet(received=resp)
                        if rcv_packt.packet.get('ack') == self.ACK_OK:
                              logger.info(f'Packet #{pckt.packet.get('seq_num') + 1} ack = "ok"')
                              return 1 # Success
                        elif max_retry:
                              max_retry -= 1
                              logger.warning(f'Packet #{pckt.packet.get('seq_num') + 1} not acknowledged, attempting to resend packet.') # Not ok
                        
                  except skt.timeout:
                        logger.warning(f'Client timeout.')
                        max_timeouts -= 1

            return 0 # Not successfull (timeout or ack not ok)
      

      def is_file(self, file):
            return os.path.exists(file)
      

      def serve_client(self, client: skt.socket, addr):
            req_packet = self.wait_for_pckt_req(client)

            if not req_packet: return 3 # Client timed out

            if self.is_file(req_packet.packet.get('file_name')):
                  pckt = Packet(status='file_found')
                  client.send(pckt.__dump__())

                  f_buff = open(req_packet.packet.get('file_name'), mode='rb')
                  
                  logger.info(f'Ready to send file...')
                  seq_count = 0
                  data_buff = f_buff.read(self.MAX_BUFF)

                  while data_buff:
                        pkt = Packet(data_buff, seq_num=seq_count)
                        
                        if not self.send_data(client, pkt):
                              logger.warning('Errors on sending packet, client disconnected.')
                              client.close()
                              break
                        seq_count += 1
                        data_buff = f_buff.read(self.MAX_BUFF)
                  
                  logger.info(f'All data was sent, disconnecting client.')
                  f_buff.close()
            else:
                  logger.info(f'File not found, disconnecting client.')
                  pckt = Packet(status='not_found')
                  client.send(pckt.__dump__())

            client.close()


      def stop(self):
            self.active_conn = 0
            self.sckt.close()


if __name__ == '__main__':
      MAX_BUFF_SIZE = 1024
      server_addr = ('localhost', 8000)
      SERVER_TIMOUT = 2
      server = RDTServer(skt.AF_INET, skt.SOCK_STREAM, server_addr, SERVER_TIMOUT, MAX_BUFF_SIZE)

      server.listen()