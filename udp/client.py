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
            msgs = ['START:all_too_well.txt', 'START:intercin_copos.png', 'STOP:None:0']
            for msg in msgs:
                if 'STOP' in msg:
                    self.sckt.sendto(msg.encode(), server_address)
                    self.close() # Close client after sending all mesages.
                    break

                f_name = msg.split(':')[1]
                f_type = f_name.split('.')[-1]

                f_path = f'./samples/{f_name}'
                save_path = f'./received/received_back_{f_name}'
                total_pckts = self.get_packet_amout(f_path)

                # Communicate transmition init to server
                self.sckt.sendto(f'{msg}:{total_pckts}'.encode(), server_address)
                time.sleep(0.0001)


                # Sending files
                file_buff = open(f_path, 'rb') # Reading binary file

                pckt = 1
                bytes = 0
                while True:
                    bytes = file_buff.read(self.MAX_BUFF)
                    if bytes == b"": break

                    print(f"[CLIENT] sent packet {pckt}/{total_pckts}")
                    self.sckt.sendto(bytes, server_address)
                    pckt += 1
                    time.sleep(0.0001)

                print(f'[CLIENT] Done. {pckt} packets were sent.')


                # Receiving packets back
                state, file, pckts = '', '', ''
                while not state:
                    try:
                        data, _ = self.sckt.recvfrom(self.MAX_BUFF)
                        state, file, pckts = data.decode().split(':')
                    except:
                        continue
                
                if state == 'START':
                    print('[CLIENT] Receiving packets back...')
                    total_pckts = int(pckts)
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
                    if (f_type == 'txt' or f_type == 'pdf') and len(packets) == total_pckts:
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