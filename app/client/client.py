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

    gpkt = Packet.server_packet("USR_CON", self.user)
    s = self.send_packet(gpkt, close=False)
    resp = self.receive_packet(s)

    if resp['type'] == "SRV_OK":
      self.server_socket = s
      self.status = "CONNECTED"
    elif resp['type'] == "SRV_ERR":
      s.close()
    else:
      s.close()


  def disconnect(self):
    self.receiving = False
    self.status = "DISCONNECTED"
    gpkt = Packet.server_packet("USR_DCN", self.user)
    self.send_packet(gpkt)


  def get_server_address(self):
    return "%s:%s" % (self.server_ip, self.server_port)


  def send_message(self, message):
    gpkt = Packet.server_packet("USR_SND", self.user, message)
    self.send_packet(gpkt)


  def send_whisper(self, send_to, message):
    gpkt = Packet.server_packet("USR_WHPR", self.user, {
      'send_to': send_to,
      'message': message,
    })
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
      pkt = self.receive_packet(self.server_socket)
      if pkt:
        gui.update_view(pkt)


  def send_packet(self, pkt, close=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.server_ip, self.server_port))
    s.sendall(pkt)
    if close:
      s.close()
    return s


  def receive_packet(self, sock):
    xpkt_len = recvall(sock, 4)
    if not xpkt_len:
      return None
    pkt_len = struct.unpack('>I', xpkt_len)[0]
    return Packet.decode_packet(recvall(sock, pkt_len))
