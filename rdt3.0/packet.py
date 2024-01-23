import pickle

class Packet:
      def __init__(self, msg=b'', ack='', status='', seq_num=0, received=None) -> None:
            if received:
                  self.packet = pickle.loads(received)
            else:
                  self.packet = {
                        "status": status,
                        "ack": ack,
                        "seq_num": seq_num,
                        "data": msg
                  }

      def __dump__(self):
            return pickle.dumps(self.packet)