from utils.buffer_ops import write_img, write_text
import socket as skt
import math
import time
import os


# ! CLASS BOILERPLATE
class UDPClient():
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF):
        self.sckt = skt.socket(sckt_family, sckt_type)
        self.sckt.bind(sckt_binding) # Binding this address to the client
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
    

    def check_file(self, f_name):
        return os.path.exists(f_name)


    def run(self, server_address):
            content = ''
            while not self.stop:
                if not self.init_trans:
                    print('[CLIENT] Waiting for data...')

                    try:
                        data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                        print(origin, '>', data)
                    except:
                        os.system('cls')
                        continue # recvfrom will timeout if it does not receive something


                    print('[CLIENT] Data received...')
                    
                    data = data.decode() # From bytes to str
                    state, content = data.split(':') # content = img or text

                    transmit = content and self.check_file(f'./samples/{content}')
                    
                    if not transmit:
                        print(f'[CLIENT] {content} not found...')
                        self.sckt.sendto(f"ERROR:not_found".encode(), server_address)
                        time.sleep(0.0001)

                    self.init_trans = 1 if state == "READY" and transmit else 0 # Start transmission when client is ready
                    self.stop = 1 if state == "STOP" else 0  # Stop socket

                else:
                    f_type = content.split('.')[-1]
                    f_name = f'./samples/{content}'
                    save_path = f'./received/received_back_{content}'

                    total_pckts = self.get_packet_amout(f_name)


                    # Sending files
                    file_buff = open(f_name, 'rb') # Reading binary file

                    self.sckt.sendto(f"START:{total_pckts}".encode(), server_address)
                    time.sleep(0.0001)

                    pckt = 1
                    bytes = 0
                    while True:
                        bytes = file_buff.read(self.MAX_BUFF)
                        if bytes == b"": break

                        print(f"packet {pckt}/{total_pckts}")
                        self.sckt.sendto(bytes, server_address)
                        pckt += 1
                        time.sleep(0.0001)

                    print(f'[CLIENT] Done. {pckt} packets were sent.')
                    self.init_trans = 0

                    time.sleep(0.0001)

                    # Receiving packets back
                    print('[CLIENT] Receiving packets back...')
                    packets = []
                    while len(packets) < total_pckts:
                        try:
                            print(f'[CLIENT] Waiting for packet #{len(packets)}')
                            data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                            packets.append(data)
                            if len(packets) >= total_pckts: break
                        except:
                            continue # Avoid timeout errors

                    
                    # Writing collected packages
                    if f_type == 'txt' and len(packets) == total_pckts:
                        write_text(save_path, packets)
                    elif (f_type == 'png' or f_type == 'jpg') and len(packets) == total_pckts:
                        write_img(save_path, packets)


            self.close()


    def close(self):
        self.sckt.close()


if __name__ == '__main__':
    # main()
    MAX_BUFF_SIZE = 1024 # Bytes

    addr_bind = ('127.0.0.1', 8080)
    addr_target = ('127.0.0.1', 7070)

    server = UDPClient(skt.AF_INET, skt.SOCK_DGRAM, addr_bind, MAX_BUFF_SIZE)
    server.run(addr_target)