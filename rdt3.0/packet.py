import pickle

class Packet:
      def __init__(self, msg=b'', ack='', status='', seq_num=0, file_name='', received=None) -> None:
            if received:
                  self.packet = pickle.loads(received)
            else:
                  self.packet = {
                        "status": status,
                        "ack": ack,
                        "seq_num": seq_num,
                        "file_name": file_name,
                        "data": msg
                  }

      def __dump__(self):
            return pickle.dumps(self.packet)