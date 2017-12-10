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

    s = self.send_packet("CONNECT", close=False)
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
    if message.startswith("/"):
      self.chat_commands(message)
    else:
      self.send_packet("SEND", message)


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
        self.process_packet(gui, pkt)


  def process_packet(self, gui, pkt):
    if pkt["command"] == "MESSAGE":
      gui.recv_msg(pkt["data"])
    elif pkt["command"] == "WHISPER":
      pass
    elif pkt["command"] == "USER_LIST":
      gui.update_user_list(pkt["data"])


  def send_packet(self, command, data={}, close=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.server_ip, self.server_port))
    s.sendall(encode_packet({
      "command": command,
      "username": self.username,
      "password": self.password,
      "data": data,
    }))
    if close:
      s.close()
    return s


  def receive_packet(self, sock):
    xpkt_len = recvall(sock, 4)
    if not xpkt_len:
      return None
    pkt_len = struct.unpack('>I', xpkt_len)[0]
    return decode_packet(recvall(sock, pkt_len))


  def chat_commands(self, string):
    command = string.split(" ", 1)[0]
    if command in ["/help", "/h"]:
      message = "List of commands\n" \
              + "/h -- show this\n" \
              + "/whisper or /w [user] [message] sends a private message\n" \
              + "/reply or /r [message] -- sends a reply to latest private message"
      self.gui.recv_msg(message)
    else:
      self.gui.recv_msg("Invalid Command")
