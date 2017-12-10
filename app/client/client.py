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
    self.recv_thread = threading.Thread(target=self.listen_packets, args=(gui,))
    self.recv_thread.daemon = True
    self.recv_thread.start()


  def stop_receiving(self):
    self.receiving = False


  def listen_packets(self, gui):
    while self.receiving:
      decoded_packet = self.receive_packet(self.server_socket)
      if decoded_packet:
        self.process_packet(gui, decoded_packet)


  def process_packet(self, gui, decoded_packet):
    if decoded_packet["command"] == 1: # MESSAGE
      gui.recv_msg(decoded_packet["data"])
    elif decoded_packet["command"] == 2: # WHISPER
      pass
    elif decoded_packet["command"] == 3: # USER LIST
      pass


  def receive_packet(self, sock):
    xcommand = recvall(sock, 1)
    if not xcommand:
      return None
    command = struct.unpack('>B', xcommand)[0]

    xdata_len = recvall(sock, 4)
    if not xdata_len:
      return None
    data_len = struct.unpack('>I', xdata_len)[0]
    data = recvall(sock, data_len)

    return {
      "command": command,
      "data": data,
    }
