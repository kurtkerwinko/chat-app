import socket
import struct
from packet import *
from app.helper.socket_helper import recvall

class RequestHandler():
  def __init__(self, active_connections, client, address):
    self.active_connections = active_connections
    self.client = client
    self.address = address
    self.cl_address = "%s:%s" % self.address


  def handle_request(self):
    decoded_packet = self.receive_packet(self.client)
    if not decoded_packet:
      self.client.close()
      return None
    self.authenticated = self.authenticate(decoded_packet["username"], decoded_packet["password"])

    if (decoded_packet["command"] == 1):
      self.connect(decoded_packet)
    elif (decoded_packet["command"] == 2 and self.authenticated):
      self.disconnect(decoded_packet)
    elif (decoded_packet["command"] == 3 and self.authenticated):
      self.send_message(decoded_packet)
    else:
      self.client.close()


  def connect(self, decoded_packet):
    if self.user_exists(decoded_packet["username"]):
      self.send_packet(self.client, "MESSAGE", "USERNAME_TAKEN")
      self.client.close()
      print("FAILED - USERNAME TAKEN: %s" % (self.cl_address))
    else:
      self.broadcast("MESSAGE", "<SERVER> " + decoded_packet["username"] + " CONNECTED")
      self.active_connections[decoded_packet["username"]] = {
        'client': self.client,
        'ip_address': self.cl_address,
        'password': decoded_packet["password"]
      }
      self.send_packet(self.client, "MESSAGE", "CONNECTED")
      print("CONNECTED: %s" % (self.cl_address))


  def disconnect(self, decoded_packet):
    ac = self.active_connections[decoded_packet["username"]]
    del self.active_connections[decoded_packet["username"]]
    cl_socket = ac["client"]
    cl_socket.close()
    print("DISCONNECTED: %s" % (ac["ip_address"]))
    self.broadcast("MESSAGE", "<SERVER> " + decoded_packet["username"] + " DISCONNECTED")
    self.client.close()


  def send_message(self, decoded_packet):
    self.broadcast("MESSAGE", "%s: %s" % (decoded_packet["username"], decoded_packet["message"]))
    self.client.close()


  def broadcast(self, command, message):
    dropped = [] # TEMP
    for c in self.active_connections:
      acl = self.active_connections[c]["client"]
      try: # TEMP TRY > Cause: CONNECTION DROPS
        self.send_packet(acl, command, message)
      except:
        dropped.append(c)
    for c in dropped:
      print("DISCONNECTED: %s" % (self.active_connections[c]["ip_address"]))
      del self.active_connections[c]
    if len(dropped) > 0:
      self.broadcast("MESSAGE", "DISCONNECTED: %s" % (','.join(dropped)))


  def send_packet(self, cl, command, message):
    data = encode_client_packet(command, message)
    cl.sendall(data)


  def receive_packet(self, client):
    xcommand = recvall(client, 1)
    if not xcommand:
      return client.close()
    command = struct.unpack('>B', xcommand)[0]

    xuser_len = recvall(client, 1)
    if not xuser_len:
      return client.close()
    user_len = struct.unpack('>B', xuser_len)[0]
    username = recvall(client, user_len)

    xpassword_len = recvall(client, 1)
    if not xpassword_len:
      return client.close()
    password_len = struct.unpack('>B', xpassword_len)[0]
    password = recvall(client, password_len)

    xmessage_len = recvall(client, 4)
    if not xmessage_len:
      return client.close()
    message_len = struct.unpack('>I', xmessage_len)[0]
    message = recvall(client, message_len)

    return {
      'command': command,
      'username': username,
      'password': password,
      'message': message
    }


  def authenticate(self, username, password):
    return self.active_connections.get(username, False) and self.active_connections[username]['password'] == password


  def user_exists(self, username):
    return username in self.active_connections
