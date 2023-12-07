import socket as skt
import math
import time
import os

# SocketKind ref: https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.sockettype?view=net-8.0

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
    

    def check_file(self, f_name):
        return os.path.exists(f_name)


    def run(self, target_address):
        try:
            content = ''
            while not self.stop:
                if not self.init:
                    print('stand by...')
                    data, origin = self.sckt.recvfrom(self.MAX_BUFF)

                    if data:
                        print('Data received...')
                        data = data.decode() # From bytes to str
                        state, content = data.split(':') # content = img or text

                        transmit = content and self.check_file(f'./samples/{content}')
                        if not transmit:
                            print(f'{content} not found...')
                            self.sckt.sendto(f"ERROR:not_found", target_address)
                            time.sleep(0.0001)

                        self.init = 1 if state == "READY" and transmit else 0 # Start transmission when client is ready
                        self.stop = 1 if state == "STOP" else 0  # Stop socket

                else:
                    f_name = f'./samples/{content}'
                    file_buff = open(f_name, 'rb') # Reading binary file
                    total_pckts = self.get_packet_amout(f_name, self.MAX_BUFF)
                    
                    self.sckt.sendto(f"START:{total_pckts}", target_address)
                    time.sleep(0.0001)

                    pckt = 1
                    while file_buff:
                        print(f"packet {pckt}/{total_pckts}")
                        self.sckt.sendto(file_buff.read(self.MAX_BUFF), target_address)
                        pckt += 1
                        time.sleep(0.0001)

                    print(f'Done. {pckt} packets were sent.')
                    self.init = 0

            self.close()
        except Exception as err:
            print(err)


    def close(self):
        self.sckt.close()


if __name__ == '__main__':
    # main()
    MAX_BUFF_SIZE = 1024 # Bytes

    addr_bind = ('127.0.0.1', 8080)
    addr_target = ('127.0.0.1', 7070)

    server = UDPServer(skt.AF_INET, skt.SOCK_DGRAM, addr_bind, MAX_BUFF_SIZE)
    server.run(addr_target)