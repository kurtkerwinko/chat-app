import socket
import struct
from packet import encode_packet, decode_packet
from app.helper.socket_helper import recvall


class RequestHandler():
  def __init__(self, active_connections, client, address):
    self.active_connections = active_connections
    self.client = client
    self.address = address
    self.cl_addr = "%s:%s" % self.address


  def handle_request(self):
    pkt = self.receive_packet(self.client)
    if not pkt:
      self.client.close()
      return None
    self.authenticated = self.authenticate(pkt["username"], pkt["password"])

    if (pkt["command"] == "CONNECT"):
      self.connect(pkt)
    elif (pkt["command"] == "DISCONNECT" and self.authenticated):
      self.disconnect(pkt)
    elif (pkt["command"] == "SEND" and self.authenticated):
      self.broadcast("%s: %s" % (pkt["username"], pkt["data"]))
      self.client.close()
    elif (pkt["command"] == "WHISPER" and self.authenticated):
      self.whisper(pkt)
      self.client.close()
    else:
      self.client.close()


  def connect(self, pkt):
    if self.user_exists(pkt["username"]):
      self.send_message(self.client, "USERNAME_TAKEN")
      self.client.close()
      print("FAILED - USERNAME TAKEN: %s @ %s" % (pkt["username"], self.cl_addr))
    else:
      self.broadcast("<SERVER> " + pkt["username"] + " CONNECTED")
      self.active_connections[pkt["username"]] = {
        'client': self.client,
        'ip_address': self.cl_addr,
        'password': pkt["password"]
      }
      self.send_message(self.client, "CONNECTED")
      print("CONNECTED: %s @ %s" % (pkt["username"], self.cl_addr))
      self.broadcast_user_list()


  def disconnect(self, pkt):
    ac = self.active_connections[pkt["username"]]
    del self.active_connections[pkt["username"]]
    cl_socket = ac["client"]
    cl_socket.close()
    print("DISCONNECTED: %s @ %s" % (pkt["username"], ac["ip_address"]))
    self.broadcast("<SERVER> " + pkt["username"] + " DISCONNECTED")
    self.client.close()
    self.broadcast_user_list()


  def broadcast(self, message):
    dropped = [] # TEMP
    for c in self.active_connections:
      acl = self.active_connections[c]["client"]
      try: # TEMP TRY > Cause: CONNECTION DROPS
        self.send_message(acl, message)
      except:
        dropped.append(c)
    for c in dropped:
      ip_addr = self.active_connections[c]["ipaddress"]
      print("DISCONNECTED: %s @ %s" % (c, ip_addr))
      del self.active_connections[c]
    if len(dropped) > 0:
      self.broadcast("DISCONNECTED: %s" % (','.join(dropped)))
      self.broadcast_user_list()


  def broadcast_user_list(self):
    dropped = [] # TEMP
    for c in self.active_connections:
      acl = self.active_connections[c]["client"]
      try: # TEMP TRY > Cause: CONNECTION DROPS
        self.send_user_list(acl)
      except:
        dropped.append(c)
    for c in dropped:
      ip_addr = self.active_connections[c]["ipaddress"]
      print("DISCONNECTED: %s @ %s" % (c, ip_addr))
      del self.active_connections[c]
    if len(dropped) > 0:
      self.broadcast("DISCONNECTED: %s" % (','.join(dropped)))
      self.broadcast_user_list()


  def whisper(self, pkt):
    from_user = pkt["username"]
    recv_user = pkt["data"]["user"]
    cl = self.active_connections[pkt["username"]]["client"]
    if recv_user in self.active_connections.keys():
      recv_cl = self.active_connections[recv_user]["client"]
      message = pkt["data"]["message"]
      self.send_whisper(cl, recv_user, "<To: %s>: %s" % (recv_user, message))
      self.send_whisper(recv_cl, from_user, "<From: %s>: %s" % (from_user, message))
    else:
      self.send_message(cl, "User does not exist.")


  def send_user_list(self, cl):
    self.send_packet(cl, "USER_LIST", sorted(self.active_connections.keys()))


  def send_message(self, cl, message):
    self.send_packet(cl, "MESSAGE", message)


  def send_whisper(self, cl, user, message):
    self.send_packet(cl, "WHISPER", {
      "user": user,
      "message": message,
    })


  def send_packet(self, cl, command, data):
    cl.sendall(encode_packet({
      "command": command,
      "data": data,
    }))


  def receive_packet(self, client):
    xpkt_len = recvall(client, 4)
    if not xpkt_len:
      return client.close()
    pkt_len = struct.unpack('>I', xpkt_len)[0]
    return decode_packet(recvall(client, pkt_len))


  def authenticate(self, username, password):
    return self.active_connections.get(username, False) and self.active_connections[username]['password'] == password


  def user_exists(self, username):
    return username in self.active_connections
