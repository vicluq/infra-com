import socket as skt
from PIL import Image, ImageFile
from io import BytesIO
import os


# ! CLASS BOILERPLATE
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


    def run(self, server_address):
        msgs = ['READY:all_too_well.txt', 'READY:intercin_copos.png', 'STOP:None']
        state, content = None, None

        try:
            for msg in msgs:
                f_name = msg.split(':')
                f_type = f_name[1].split('.')[-1]

                self.sckt.sendto(msg.encode(), server_address)

                if 'STOP' in msg: 
                    self.close() # Close client after sending all mesages.
                    break

                while not state:
                    try:
                        data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                        print(state, content)
                        state, content = data.decode().split(':')
                    except Exception as err:
                        continue # recvfrom will timeout if it does not receive something

                if state == 'START':
                    total_packets = int(content)
                    print(f'TOTAL PACKETS TO RECEIVE: {total_packets}')
                    save_path = f'./received/{f_name[1]}'
                    
                    # Collecting packages
                    packets = []
                    while len(packets) < total_packets:
                        try:
                            print(f'Waiting for packet #{len(packets)}')
                            data, origin = self.sckt.recvfrom(self.MAX_BUFF)
                            packets.append(data)
                            if len(packets) >= total_packets: break
                        except:
                            continue # Avoid timeout errors

                    
                    # Writing collected packages
                    if f_type == 'txt' and len(packets) == total_packets:
                        f_write = open(save_path, "wb")
                        
                        for p in packets:
                            f_write.write(p)
                            
                        print(f'{f_name[1]} was written.')
                        
                        f_write.close()

                    elif (f_type == 'png' or f_type == 'jpg') and len(packets) == total_packets:
                        img = ImageFile.Parser()
                        print('Parsing image...')
                        for p in packets:
                            img.feed(p)
                            
                        im = img.close()
                        im.save(save_path)
                        

                        print(f'{f_name[1]} was written.')

                    state = ''
                elif state == 'ERROR':
                    print(content)
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

    server = UDPClient(skt.AF_INET, skt.SOCK_DGRAM, addr_bind, MAX_BUFF_SIZE)
    server.run(addr_target)