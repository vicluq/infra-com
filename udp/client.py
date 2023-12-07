import socket as skt
import math
import time
import os


class UDPClient:
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF) -> None:
        self.sckt = skt.socket(sckt_family, sckt_type)
        self.sckt.bind(sckt_binding) # Binding this address to the server
        self.sckt.settimeout(0.1)
        
        if self.sckt is None:
            raise "Socket not available."
        
        self.MAX_BUFF = MAX_BUFF
        self.init_trans = 0
        self.stop = 0


    def run(self, target_address):
        try:
            content = ''
            while not self.stop:
                if not self.init:
                    data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                    data = data.decode() # From bytes to str

                    state, content = data.split('_') # content = img or text
                    print(f"INCOMING:{state}>{content or 'none'}")

                    transmit = content and self.check_file(f'./samples/{content}')
                    if not transmit:
                        print(f"404:{content}")
                        self.sckt.sendto(f"404:{content}", target_address)
                        time.sleep(0.0001)

                    self.init = 1 if state == "READY" and transmit else 0 # Start transmission when client is ready
                    self.stop = 1 if state == "STOP" else 0  # Stop socket

                else:
                    f_name = f'./samples/{content}'
                    file_buff = open(f_name, 'rb') # Reading binary file
                    total_pckts = self.get_packet_amout(f_name, self.MAX_BUFF)
                    
                    self.sckt.sendto(f"INFO:{total_pckts}", target_address)
                    time.sleep(0.0001)

                    pckt = 1
                    while file_buff:
                        print(f"packet {pckt}/{total_pckts}")
                        self.sckt.sendto(file_buff.read(self.MAX_BUFF), target_address)
                        pckt += 1
                        time.sleep(0.0001)

                    print('Done')
                    self.init = 0

            self.close()
        except Exception as err:
            print(err)


    def close(self):
        self.sckt.close()