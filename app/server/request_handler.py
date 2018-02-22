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
    self.connected = False

    self.connect()


  def handle_request(self):
    while self.connected:
      pkt = self.receive_packet(self.client)
      if pkt:
        if (pkt.pkt_type == 'USR_DCN'):
          self.disconnect(pkt)
        elif (pkt.pkt_type == 'USR_SND'):
          self.user_send(pkt)
        elif (pkt.pkt_type == 'USR_WHPR'):
          self.whisper(pkt)


  def connect(self):
    pkt = self.receive_packet(self.client)
    if pkt.pkt_type == 'USR_CON':
      if self.user_exists(pkt.username):
        gpkt = Packet(pkt_type="SRV_ERR", message="USERNAME_TAKEN")
        self.send_packet(self.client, gpkt)
        self.drop_connection()
        pr_yellow("FAILED - USERNAME TAKEN: %s @ %s" % (pkt.username, self.cl_addr))
      else:
        gpkt = Packet(pkt_type="SRV_USR_CON", username=pkt.username)
        self.broadcast(gpkt)
        self.active_connections[pkt.username] = {
          'client': self.client,
          'ip_address': self.cl_addr,
          'password': pkt.password
        }
        gpkt = Packet(pkt_type="SRV_OK")
        self.send_packet(self.client, gpkt)
        pr_green("CONNECTED: %s @ %s" % (pkt.username, self.cl_addr))
        gpkt_usr = Packet(pkt_type="USR_LST", user_list=sorted(self.active_connections.keys()))
        self.broadcast(gpkt_usr)
        self.connected = True


  def disconnect(self, pkt):
    ac = self.active_connections[pkt.username]
    del self.active_connections[pkt.username]
    cl_socket = ac["client"]
    cl_socket.close()
    pr_red("DISCONNECTED: %s @ %s" % (pkt.username, ac["ip_address"]))
    gpkt = Packet(pkt_type="SRV_USR_DCN", username=pkt.username)
    self.broadcast(gpkt)
    self.client.close()
    gpkt_usr = Packet(pkt_type="USR_LST", user_list=sorted(self.active_connections.keys()))
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
      gpkt = Packet(pkt_type="SRV_USR_DCN", username=dropped)
      gpkt_usr = Packet(pkt_type="USR_LST", user_list=sorted(self.active_connections.keys()))
      self.broadcast(gpkt)
      self.broadcast(gpkt_usr)


  def user_send(self, pkt):
    gpkt = Packet(pkt_type="USR_MSG", username=pkt.username, message=pkt.message)
    self.broadcast(gpkt)


  def whisper(self, pkt):
    snd_user = pkt.username
    recv_user = pkt.send_to
    snd_cl = self.active_connections[snd_user]["client"]
    if recv_user in self.active_connections.keys():
      recv_cl = self.active_connections[recv_user]["client"]
      recv_gpkt = Packet(pkt_type="PRV_USR_MSG_RECV", username=snd_user, message=pkt.message)
      snd_gpkt = Packet(pkt_type="PRV_USR_MSG_SND", username=recv_user, message=pkt.message)
      self.send_packet(snd_cl, snd_gpkt)
      self.send_packet(recv_cl, recv_gpkt)
    else:
      gpkt = Packet(pkt_type="SRV_ERR", message="User does not exist.")
      self.send_packet(snd_cl, gpkt)


  def send_packet(self, cl, pkt):
    data = Packet.encode_packet(pkt)
    while len(data):
      sent = cl.send(data)
      data = data[sent:]


  def receive_packet(self, client):
    xpkt_len = recvall(client, 4)
    if not xpkt_len:
      return None
    pkt_len = struct.unpack('>I', xpkt_len)[0]
    return Packet.decode_packet(recvall(client, pkt_len))


  def authenticate(self, pkt):
    return self.active_connections.get(pkt.username, False) and self.active_connections[pkt.username]['password'] == pkt.password


  def user_exists(self, username):
    return username in self.active_connections


  def drop_connection(self):
    self.connected = False
    self.disconnect()
