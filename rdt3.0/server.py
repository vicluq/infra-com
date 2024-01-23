from packet import Packet
import threading
import socket as skt
import logging
import random
import os


logging.basicConfig()
logger = logging.getLogger('SERVER')


class RDTServer:
      def __init__(self, sckt_family, sckt_type, sckt_binding, sckt_timeout, MAX_BUFF) -> None:
            self.sckt = skt.socket(sckt_family, sckt_type)
            self.sckt.bind(sckt_binding) # Binding this address to the server
            self.sckt.settimeout(sckt_timeout)
            self.LOSS_PROB = 0.05 # Packet loss prob

            if self.sckt is None:
                  raise "Socket not available."

            self.MAX_BUFF: int = MAX_BUFF
            self.clients: dict = {}
            self.active_conn = 0

            self.ACK_OK = 'ok'
            self.ACK_NOT_OK = 'not_ok'
 
      def listen(self):
            try:
                  self.sckt.listen()
                  while True:
                        client, addr = self.sckt.accept() # Await for connection
                        self.clients[addr] = client
                        thread = threading.Thread(target=self.serve_client, args=[client, addr])
                        self.active_conn += 1
                        thread.start()
                        logger.info(f'New connection > {client}@{addr} | Total = {self.active_conn}')

            except Exception as err:
                  logger.warn(err)

      
      def wait_for_pckt_req(self, client: skt.socket) -> Packet:
            max_timeouts = 2
            
            while max_timeouts:
                  try:
                        pckt_req = client.recv(self.MAX_BUFF)
                        if pckt_req:
                              p = Packet(received=pckt_req)
                              logger.info('Packet Received.')
                              return p
                  except skt.timeout:
                        max_timeouts -= 1
            
            return 0 # timeout
            

      def send_data(self, client: skt.socket, pckt: Packet):
            max_timeouts = 2
            while max_timeouts:
                  if random.random() > self.LOSS_PROB:
                        client.send(pckt.__dump__())
                  else:
                        logger.warn(f'Packet was lost {pckt.packet.get('seq_num')}')

                  try:
                        resp = client.recv(self.MAX_BUFF) # Receive the ack 'ok' or 'not ok' pckt
                        
                        if not resp:
                              logger.info(f"Client disconnected.")
                              return 0

                        rcv_packt = Packet(received=resp)
                        if rcv_packt.packet.get('ack') == self.ACK_OK:
                              return 1 # Success
                        else:
                              logger.warn('Not acknowledged, attempting to resend packet.') # Not ok
                        
                  except skt.timeout:
                        logger.warn('Client timeout.')
                        max_timeouts -= 1

            return 0
      

      def is_file(self, file):
            return os.path.exists(file)
      

      def serve_client(self, client: skt.socket, addr):
            req_packet = self.wait_for_pckt_req(client)

            if not req_packet: return 3 # Client timed out

            if self.is_file(req_packet.packet.get('file')):
                  f_buff = open(req_packet.packet.get('file'))
                  pckt = Packet(status='file_found')
                  seq_count = 0
                  data_buff = f_buff.read(self.MAX_BUFF)
                  while True:
                        pkt = Packet(data_buff, seq_num=seq_count)
                        
                        if not self.send_data(client, pkt):
                              logger.warn('Errors on sending packet, client disconnected.')
                              client.close()
                              self.clients.pop(addr)
                              break
                        
                        logger.info(f'Packet {seq_count + 1} was sent.')
                        seq_count += 1
                        data_buff = f_buff.read(self.MAX_BUFF)
            else:
                  pckt = Packet(status='not_found')
                  client.send(pckt.__dump__())

            client.close()
            self.clients.pop(addr)
            self.active_conn -= 1


      def stop(self):
            for k in self.clients.keys():
                  self.clients[k].close()
            self.clients = {}
            self.active_conn = 0
            self.sckt.close()