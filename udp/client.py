import socket as skt
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


    def run(self, server_address):
        msgs = ['READY:all_too_well.txt', 'STOP']
        try:
            for msg in msgs:
                f_name = msg.split(':')
                self.sckt.sendto(msg, server_address)
                time.sleep(0.002)

                data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                state, content = data.decode().split(':')

                if state == 'START':
                    total_packets = content
                    f_write = open(f'./received/{f_name[1]}', "wb")
                    
                    packets = []
                    for _ in range(total_packets):
                        data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                        packets.append(data)
                        time.sleep(0.0005)
                    
                    if len(packets) == total_packets:
                        for p in packets:
                            f_write.write(p)

                        f_write.close()

                    time.sleep(0.01)
                
                elif state == 'ERROR':
                    print(content)
                    time.sleep(0.01)
                    continue


            self.close()
        except Exception as err:
            print(err)


    def close(self):
        self.sckt.close()
