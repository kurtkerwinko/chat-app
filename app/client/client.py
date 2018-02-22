import socket
import threading
import struct
from app.misc.packet import Packet
from app.misc.socket_helper import recvall


class Client():
  def __init__(self):
    self.server_ip = None
    self.server_port = None
    self.user = {
      'username': None,
      'password': None,
    }
    self.receiving = False
    self.status = "DISCONNECTED"
    self.last_received = None


  def connect(self, server_ip, server_port, username, password):
    self.server_ip = server_ip
    self.server_port = server_port
    self.user = {
      'username': username,
      'password': password,
    }

    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.connect((self.server_ip, self.server_port))
    self.server_socket.setblocking(0)

    gpkt = Packet(pkt_type="USR_CON", **self.user)
    self.send_packet(gpkt)
    resp = self.receive_packet()

    if resp.pkt_type == "SRV_OK":
      self.status = "CONNECTED"
    elif resp.pkt_type == "SRV_ERR":
      self.server_socket.close()
    else:
      self.server_socket.close()


  def disconnect(self):
    self.receiving = False
    self.status = "DISCONNECTED"
    gpkt = Packet(pkt_type="USR_DCN", **self.user)
    self.send_packet(gpkt)


  def get_server_address(self):
    return "%s:%s" % (self.server_ip, self.server_port)


  def send_message(self, message):
    gpkt = Packet(pkt_type="USR_SND", message=message, **self.user)
    self.send_packet(gpkt)


  def send_whisper(self, send_to, message):
    gpkt = Packet(pkt_type="USR_WHPR", send_to=send_to, message=message, **self.user)
    self.send_packet(gpkt)


  def start_receiving(self, gui):
    self.gui = gui
    self.receiving = True
    self.recv_thread = threading.Thread(target=self.listen_packets, args=(gui,))
    self.recv_thread.daemon = True
    self.recv_thread.start()


  def stop_receiving(self):
    self.receiving = False


  def listen_packets(self, gui):
    while self.receiving:
      pkt = self.receive_packet()
      if pkt:
        gui.update_view(pkt)


  def send_packet(self, pkt):
    data = Packet.encode_packet(pkt)
    while len(data):
      sent = self.server_socket.send(data)
      data = data[sent:]


  def receive_packet(self):
    xpkt_len = recvall(self.server_socket, 4)
    if not xpkt_len:
      return None
    pkt_len = struct.unpack('>I', xpkt_len)[0]
    return Packet.decode_packet(recvall(self.server_socket, pkt_len))
