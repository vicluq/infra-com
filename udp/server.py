import socket as skt
import math
import time
import os

# SocketKind ref: https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.sockettype?view=net-8.0

def get_packet_amout(file, max_buff_size):
    fsize = os.stat(file).st_size # Size in bytes
    total_packs = math.ceil(fsize/max_buff_size)
    return total_packs


datagram_sckt = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
datagram_sckt.bind(('127.0.0.1', 8080)) # Binding this address to the server
datagram_sckt.settimeout(0.1)

if datagram_sckt is None:
    raise "Socket not available."


target_address = ('127.0.0.1', 7070) # Host, Port
MAX_BUFFER_SIZE = 1024 # Bytes

init = 0
stop = 0
cont_req = 'TEXT'
cont = {
    'IMG': '',
    'TEXT': './samples/all_too_well.txt'
}

# Communication
try:
    while not stop:
        if not init:
            data, origin = datagram_sckt.recvfrom(MAX_BUFFER_SIZE)
            data = data.decode() # From bytes to str

            state, content = data.split('_') # content = img or text

            init = 1 if state == "READY" else 0 # Start transmission when client is ready
            stop = 1 if state == "STOP" else 0  # Stop socket

            cont_req = content if content else 'TEXT'
        else:
            f_name = cont[cont_req]
            file_buff = open(f_name, 'rb') # Reading binary file
            total_pckts = get_packet_amout(f_name, MAX_BUFFER_SIZE)
            
            datagram_sckt.sendto(f"INFO:{total_pckts}", target_address)
            time.sleep(0.0001)

            pckt = 1
            while file_buff:
                print(f"packet {pckt}/{total_pckts}")
                datagram_sckt.sendto(file_buff.read(MAX_BUFFER_SIZE), target_address)
                pckt += 1
                time.sleep(0.0001)

            print('Done')
            init = 0
except Exception as err:
    print(err)