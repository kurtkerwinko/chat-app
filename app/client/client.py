import socket
import threading
import struct
from app.server.packet import encode_packet, decode_packet
from app.helper.socket_helper import recvall

class Client():
  def __init__(self):
    self.receiving = False
    self.status = "DISCONNECTED"


  def connect(self, server_ip, server_port, username, password):
    self.server_ip = server_ip
    self.server_port = server_port
    self.username = username
    self.password = password

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.server_ip, self.server_port))

    s.sendall(encode_packet({
      "command": "CONNECT",
      "username": self.username,
      "password": self.password,
    }))
    resp = self.receive_packet(s)["data"]
    if resp == "CONNECTED":
      self.server_socket = s
      self.status = "CONNECTED"
    else:
      s.close()


  def disconnect(self):
    self.receiving = False
    self.status = "DISCONNECTED"
    self.send_packet("DISCONNECT")


  def get_server_address(self):
    return "%s:%s" % (self.server_ip, self.server_port)


  def send_message(self, message):
    self.send_packet("SEND", message)


  def start_receiving(self, gui):
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
        self.process_packet(gui, pkt)


  def process_packet(self, gui, pkt):
    if pkt["command"] == "MESSAGE":
      gui.recv_msg(pkt["data"])
    elif pkt["command"] == "WHISPER":
      pass
    elif pkt["command"] == "USER_LIST":
      pass


  def send_packet(self, command, data={}):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.server_ip, self.server_port))
    s.sendall(encode_packet({
      "command": command,
      "username": self.username,
      "password": self.password,
      "data": data,
    }))
    s.close()


  def receive_packet(self, sock):
    xpkt_len = recvall(sock, 4)
    if not xpkt_len:
      return None
    pkt_len = struct.unpack('>I', xpkt_len)[0]
    return decode_packet(recvall(sock, pkt_len))
