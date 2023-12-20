import socket as skt
from utils.buffer_ops import write_img, write_text
import os
import math
import time


# ! CLASS BOILERPLATE
class UDPServer:
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF) -> None:
        self.sckt = skt.socket(sckt_family, sckt_type)
        self.sckt.bind(sckt_binding) # Binding this address to the server
        self.sckt.settimeout(0.1)
        
        if self.sckt is None:
            raise "Socket not available."
        
        self.MAX_BUFF = MAX_BUFF
        self.init_trans = 0
        self.stop = 0

    def get_packet_amout(self, file):
        fsize = os.stat(file).st_size # Size in bytes
        total_packs = math.ceil(fsize/self.MAX_BUFF)
        return total_packs


    def run(self, client_address):
        state, content = None, None

        try:
            while not self.stop:
                print('===================================')
                print('[SERVER] Waiting for communication...')
                
                while not state:
                    try:
                        data, _ = self.sckt.recvfrom(self.MAX_BUFF)
                        print(state, content)
                        state, file, pckts = data.decode().split(':')
                    except Exception as err:
                        continue # recvfrom will timeout if it does not receive something
            

                if state == 'START':
                    f_type = file.split('.')[-1]
                    total_packets = int(pckts)
                    save_path = f'./received/{file}'
                    
                    # Collecting packages
                    packets = []
                    while len(packets) < total_packets:
                        try:
                            print(f'[SERVER] Waiting for packet #{len(packets)}')
                            data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                            packets.append(data)
                            if len(packets) >= total_packets: break
                        except:
                            continue # Avoid timeout errors

                    
                    # Writing collected packages
                    if f_type == 'txt' and len(packets) == total_packets:
                        write_text(save_path, packets)
                    elif (f_type == 'png' or f_type == 'jpg') and len(packets) == total_packets:
                        write_img(save_path, packets)
                    

                    # Sending back file
                    file_buff = open(save_path, 'rb') # Reading binary file

                    pckt = 1
                    bytes = 0
                    total_packets = self.get_packet_amout(save_path)

                    self.sckt.sendto(f"START:{file}:{total_packets}".encode(), client_address)
                    time.sleep(0.0001)

                    while True:
                        bytes = file_buff.read(self.MAX_BUFF)
                        if bytes == b"": break

                        print(f"[SERVER] packet {pckt}/{total_packets}")
                        self.sckt.sendto(bytes, client_address)
                        pckt += 1
                        time.sleep(0.0001)

                    print(f'[SERVER] Done. {pckt} packets were sent.')
                    
                    state = '' # Reset state for next round
                
                elif state == 'ERROR':
                    print(content)
                    state = ''
                    continue

                elif state == 'STOP':
                    state = ''
                    continue


            self.close()
        except Exception as err:
            print(err)


    def close(self):
        self.sckt.close()


if __name__ == '__main__':
    # main()
    MAX_BUFF_SIZE = 1024 # Bytes

    addr_target = ('127.0.0.1', 8080) # Server address
    addr_bind = ('127.0.0.1', 7070)

    server = UDPServer(skt.AF_INET, skt.SOCK_DGRAM, addr_bind, MAX_BUFF_SIZE)
    server.run(addr_target)