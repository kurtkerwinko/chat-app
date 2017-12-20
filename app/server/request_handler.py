import socket
import struct
from app.server.gui.color_print import pr_red, pr_green, pr_yellow
from app.misc.packet import Packet
from app.misc.socket_helper import recvall


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
    self.authenticated = self.authenticate(**pkt)

    if (pkt['type'] == 'USR_CON'):
      self.connect(**pkt)
    elif (pkt['type'] == 'USR_DCN' and self.authenticated):
      self.disconnect(**pkt)
    elif (pkt['type'] == 'USR_SND' and self.authenticated):
      self.user_send(**pkt)
      self.client.close()
    elif (pkt['type'] == 'USR_WHPR' and self.authenticated):
      self.whisper(**pkt)
      self.client.close()
    else:
      self.client.close()


  def connect(self, username, password, **_):
    if self.user_exists(username):
      gpkt = Packet.generate_packet("SRV_ERR", message="USERNAME_TAKEN")
      self.send_packet(self.client, gpkt)
      self.client.close()
      pr_yellow("FAILED - USERNAME TAKEN: %s @ %s" % (username, self.cl_addr))
    else:
      gpkt = Packet.generate_packet("SRV_USR_CON", username=username)
      self.broadcast(gpkt)
      self.active_connections[username] = {
        'client': self.client,
        'ip_address': self.cl_addr,
        'password': password
      }
      gpkt = Packet.generate_packet("SRV_OK")
      self.send_packet(self.client, gpkt)
      pr_green("CONNECTED: %s @ %s" % (username, self.cl_addr))
      gpkt_usr = Packet.generate_packet("USR_LST", user_list= sorted(self.active_connections.keys()))
      self.broadcast(gpkt_usr)


  def disconnect(self, username, password, **_):
    ac = self.active_connections[username]
    del self.active_connections[username]
    cl_socket = ac["client"]
    cl_socket.close()
    pr_red("DISCONNECTED: %s @ %s" % (username, ac["ip_address"]))
    gpkt = Packet.generate_packet("SRV_USR_DCN", username=username)
    self.broadcast(gpkt)
    self.client.close()
    gpkt_usr = Packet.generate_packet("USR_LST", user_list= sorted(self.active_connections.keys()))
    self.broadcast(gpkt_usr)


  def broadcast(self, pkt):
    dropped = [] # TEMP
    for c in self.active_connections:
      acl = self.active_connections[c]["client"]
      try: # TEMP TRY > Cause: CONNECTION DROPS
        self.send_packet(acl, pkt)
      except:
        dropped.append(c)
    for c in dropped:
      ip_addr = self.active_connections[c]["ip_address"]
      pr_red("DISCONNECTED: %s @ %s" % (c, ip_addr))
      del self.active_connections[c]
    if len(dropped) > 0:
      gpkt = Packet.generate_packet("SRV_USR_DCN", username=dropped)
      gpkt_usr = Packet.generate_packet("USR_LST", user_list= sorted(self.active_connections.keys()))
      self.broadcast(gpkt)
      self.broadcast(gpkt_usr)


  def user_send(self, username, message, **_):
    gpkt = Packet.generate_packet('USR_MSG', username=username, message=message)
    self.broadcast(gpkt)


  def whisper(self, username, send_to, message, **_):
    snd_user = username
    recv_user = send_to
    snd_cl = self.active_connections[snd_user]["client"]
    if recv_user in self.active_connections.keys():
      recv_cl = self.active_connections[recv_user]["client"]
      recv_gpkt = Packet.generate_packet("PRV_USR_MSG_RECV", username=snd_user, message=message)
      snd_gpkt = Packet.generate_packet("PRV_USR_MSG_SND", username=recv_user, message=message)
      self.send_packet(snd_cl, snd_gpkt)
      self.send_packet(recv_cl, recv_gpkt)
    else:
      gpkt = Packet.generate_packet('SRV_ERR', message="User does not exist.")
      self.send_packet(snd_cl, gpkt)


  def send_packet(self, cl, pkt):
    cl.sendall(pkt)


  def receive_packet(self, client):
    xpkt_len = recvall(client, 4)
    if not xpkt_len:
      return client.close()
    pkt_len = struct.unpack('>I', xpkt_len)[0]
    return Packet.decode_packet(recvall(client, pkt_len))


  def authenticate(self, username, password, **_):
    return self.active_connections.get(username, False) and self.active_connections[username]['password'] == password


  def user_exists(self, username):
    return username in self.active_connections
