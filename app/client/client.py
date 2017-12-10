import socket
import threading
import struct
from app.server.packet import encode_server_packet
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

    data = encode_server_packet("CONNECT", self.username, self.password)
    s.sendall(data)
    resp = self.receive_packet(s)
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


  def send_packet(self, command, message=""):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.server_ip, self.server_port))
    data = encode_server_packet(command, self.username, self.password, message)
    s.sendall(data)
    s.close()


  def send_message(self, message):
    self.send_packet("SEND", message)


  def start_receiving(self, gui):
    self.receiving = True
    self.recv_thread = threading.Thread(target=self.receive_message, args=(gui,))
    self.recv_thread.daemon = True
    self.recv_thread.start()


  def stop_receiving(self):
    self.receiving = False


  def receive_message(self, gui):
    while self.receiving:
      message = self.receive_packet(self.server_socket)
      if message:
        gui.recv_msg(message)


  def receive_packet(self, sock):
    xcommand = recvall(sock, 1)
    if not xcommand:
      return sock.close()
    command = struct.unpack('>B', xcommand)[0]

    xdata_len = recvall(sock, 4)
    if not xdata_len:
      return None
    data_len = struct.unpack('>I', xdata_len)[0]
    return recvall(sock, data_len)
