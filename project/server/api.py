from packet import Packet
from utils.print_data import show_reservations
import socket as skt
import asyncio
import logging
import math


logging.basicConfig(level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger('SERVER')


class RDTServer:
      def __init__(self, sckt_family, sckt_type, sckt_binding, sckt_timeout, MAX_BUFF) -> None:
            self.sckt = skt.socket(sckt_family, sckt_type)
            self.sckt.bind(sckt_binding) # Binding this address to the server
            self.sckt.setblocking(False) # Unblock I/O to use with async operations

            self.TIMEOUT = sckt_timeout
            
            if self.sckt is None:
                  raise Exception("Socket not available.")

            self.MAX_BUFF: int = MAX_BUFF * 3

            self.ACK_OK = 'ok'
            self.ACK_NOT_OK = 'not_ok'
            self.acking = False

            self.connections = {}
            self.reservations: dict[str, str] = {}
            self.buffer = asyncio.Queue()

      async def listen(self):
            logger.info('Listening to messages...')
            loop = asyncio.get_event_loop()
            try:
                  self.sckt.settimeout(None)
                  while True:
                        try:
                              logger.info(f'[listen] Buffer Size = {self.buffer.qsize()}')
                              req_packet, client = await loop.sock_recvfrom(self.sckt, self.MAX_BUFF)
                              await self.buffer.put((req_packet, client))
                        except skt.timeout:
                              continue
            except Exception as err:
                  logger.error(err)



      async def process_buffer(self):
            logger.info('Processing messages...')
            while True:
                  pckt, client = await self.buffer.get()
                  await self._process_pckt(pckt, client)
                  self.buffer.task_done()
                  print('Current buffer size:', self.buffer.qsize())

      def _is_username(self, name):
            return len([n for n in self.connections.values() if n == name])
      
      def _is_reserva(self, res_key):
            return self.reservations.get(res_key)

      def _validate_reserva(self, room, day, hour):
            time = int(hour[0:-1]) # format: 8h, 11h
            room_num = int(room[1:])
            print(room[0], room[1:])
            if time < 8 or time > 17:
                  return 'Horario Invalido'
            if room[0] != 'e' or room_num < 101 or room_num > 105:
                  return 'Sala Inválida'
            return 'Horario e dia indisponivel.' if self._is_reserva(f'{room}-{day}-{hour}') else None
      
      def _check_available_hours(self, room, day) -> list[str]:
            hours = [f'{h}h' for h in list(range(8, 18))]
            occupied = [k.split('-')[-1] for k in list(self.reservations.keys()) 
                        if k.split('-')[0] == room and k.split('-')[1] == day]

            return [h for h in hours if h not in occupied]

      async def _process_pckt(self, pckt, client):
            key = f'{client[0]}:{client[1]}'
            p = Packet(received=pckt)
            command, data = self._decode_command(p)
            msg = ''

            if command != 'connect' and not self.connections.get(key):
                  msg = 'Falha na autenticação.'.encode()
            
            if command == 'connect':
                  name = ' '.join(data[1:])
                  if self._is_username(name):
                        msg = 'Nome já em uso.'.encode()
                  else:
                        await self._broadcast(f'{name} está avaliando reservas!')
                        self.connections[key] = name
                        logger.info(self.connections)
                        msg = 'Você está conectado.'.encode()
            
            elif command == 'bye':
                  try:
                        await self._broadcast(f'{self.connections[key]} saiu do sistema.', [key])
                        self.connections.pop(key)
                        logger.info(self.connections)
                  except KeyError:
                        pass
                  return
            
            elif command == 'list':
                  msg = show_reservations(self.reservations, self.connections).encode()

            elif command == 'reservar':
                  room, day, hour = data
                  error = self._validate_reserva(room.lower(), day.lower(), hour.lower())
                  if not error:
                        self.reservations[f'{room.lower()}-{day.lower()}-{hour.lower()}'] = key
                        await self._broadcast(f'{self.connections[key]} [{key}] reservou a sala {room} na {day} {hour}', [key])
                        msg = f'Você [{key}] reservou a sala {room}.'.encode()
                  else:
                        msg = error.encode()
            
            elif command == 'cancelar':
                  room, day, hour = data
                  res_key = f'{room.lower()}-{day.lower()}-{hour.lower()}'
                  if self._is_reserva(res_key) and self.reservations[res_key] == key:
                        await self._broadcast(f'{self.connections[key]} [{key}] cancelou a sala {room} na {day} {hour}', [key])
                        msg = f'Você [{key}] cancelou a sala {data[1]}.'.encode()
                        self.reservations.pop(res_key)                  
                  else:
                        msg = f'Reserva nao existe ou nao pertence a voce.'.encode()
            
            elif command == 'check':
                  room, day = data
                  msg = ' '.join(self._check_available_hours(room, day))
                  msg = f'{room} {day} -> {msg}'.encode()

            await self.dispacth(client, msg)

      async def _broadcast(self, msg: str, except_hosts = []):
            loop = asyncio.get_event_loop()

            for cli in self.connections.keys():
                  if cli not in except_hosts:
                        host, port = cli.split(':')
                        port =  int(port)
                        p = Packet(msg.encode())
                        await loop.sock_sendto(self.sckt, p.__dump__(), (host, port))

            
      async def send_data(self, client_addr: tuple[str, str], pckt: Packet):
            loop = asyncio.get_event_loop()
            self.sckt.settimeout(self.TIMEOUT)
            max_timeouts = 2

            while max_timeouts:
                  try:
                        await loop.sock_sendto(self.sckt, pckt.__dump__(), client_addr)
                        logger.info(f'[CLI:{client_addr}] sent pckt #{pckt.packet['seq_num']} of {pckt.packet['total']}')
                        
                        logger.info(f'Waiting for ack from {client_addr}')
                        resp, client = await self.buffer.get() # Receive the ack 'ok' or 'not ok' pckt

                        # Packet from some other client
                        if client != client_addr:
                              logger.info(f'Received from other client: {client}')
                              self.buffer.put_nowait((resp, client))
                              continue

                        rcv_packt = Packet(received=resp)

                        if rcv_packt.packet.get('ack') == self.ACK_OK:
                              logger.info(f'[{client_addr}] Packet #{pckt.packet.get("seq_num")} ack = "ok"')
                              return 1 # Success
                        else:
                              logger.info(f'[{client_addr}] Packet #{pckt.packet.get("seq_num")} ack = "not ok"')
                              return 0
                  except skt.timeout:
                        logger.warning(f'Client timeout.')
                        max_timeouts -= 1

            return 0 # Not successfull (timeout or ack not ok)
      

      def _decode_command(self, packet: Packet):
            command_data = packet.packet['data'].decode().split(' ')
            command = command_data[0]
            data = command_data[1:] if len(command_data) > 1 else None

            return command, data


      async def dispacth(self, client: tuple[str, str], data: bytes):
            loop = asyncio.get_event_loop()
            
            chunks = math.ceil(len(data) / self.MAX_BUFF)
            max_retry = 3
            seq_count = 0

            for chunk in range(chunks):
                  batch = data[chunk:(chunk * self.MAX_BUFF + self.MAX_BUFF)]
                  pckt = Packet(msg=batch, seq_num=seq_count + 1, total=chunks)
                  
                  while max_retry:
                        ret = await self.send_data(client, pckt)
                        if not ret:
                              max_retry -= 1
                        else:
                              break
                  
                  if not max_retry:
                        break
                  
                  max_retry = 3
                  seq_count += 1

            if seq_count < chunks: # Failed
                  logger.warn(f'{client} > Failed to ack.')
                  p = Packet('Error:failed to ack.'.encode(), error=1)
                  await loop.sock_sendto(self.sckt, p.__dump__(), client)
                  return 0
            else:
                  logger.info(f'Data was sent to {client}.')
                  return 1

