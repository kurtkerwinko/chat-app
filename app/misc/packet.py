import pickle
import struct


class Packet():
  def __init__(self, **kwargs):
    """ Client Packet Types """
    """ SRV_OK (STATUS), SRV_MSG, SRV_ERR, SRV_USR_CON, SRV_USR_DCN """
    """ USR_MSG, PRV_USR_MSG_SND, PRV_USR_MSG_RECV, USR_LST """

    """ Server Packet Types """
    """ USR_CON (STATUS), USR_DCN (STATUS), USR_SND, USR_WHPR """

    self.pkt_type = kwargs.get('pkt_type', None)
    self.username = kwargs.get('username', None)
    self.password = kwargs.get('password', None)
    self.message = kwargs.get('message', None)
    self.send_to = kwargs.get('send_to', None)
    self.user_list = kwargs.get('user_list', None)
    self.last_received = None
    if self.pkt_type in ['PRV_USR_MSG_SND', 'PRV_USR_MSG_RECV']:
      self.last_received = self.username


  def construct_message(self):
    if self.pkt_type == 'SRV_MSG':
      return (["<SERVER> %s" % (self.message), "SRV_MSG_FG"], )
    if self.pkt_type == 'SRV_ERR':
      return (["<SERVER ERROR> %s" % (self.message), "SRV_ERR_FG"], )
    if self.pkt_type == 'SRV_USR_CON':
      return (
        [self.username, "USER_FG"],
        [" CONNECTED", "SRV_MSG_FG"],
      )
    if self.pkt_type == 'SRV_USR_DCN':
      if type(self.username) == list:
        msg = ()
        for user in self.username:
          msg += ([user, "USER_FG"], [", ", "SRV_MSG_FG"])
        return msg[:-1] + ([" DISCONNECTED", "SRV_MSG_FG"], )
      else:
        return (
          [self.username, "USER_FG"],
          [" DISCONNECTED", "SRV_MSG_FG"],
        )
    if self.pkt_type == 'USR_MSG':
      return (
        [self.username, "USER_FG"],
        [": %s" % (self.message), "MSG_FG"],
      )
    if self.pkt_type == 'PRV_USR_MSG_SND':
      return (
        ["<To: ", "PRIV_MSG_FG"],
        ["%s" % (self.username), "PRIV_USER_FG"],
        ["> ", "PRIV_MSG_FG"],
        ["%s" % (self.message), "PRIV_MSG_FG"],
      )
    if self.pkt_type == 'PRV_USR_MSG_RECV':
      return (
        ["<From: ", "PRIV_MSG_FG"],
        ["%s" % (self.username), "PRIV_USER_FG"],
        ["> ", "PRIV_MSG_FG"],
        ["%s" % (self.message), "PRIV_MSG_FG"],
      )


  # 4 byte - Length of Payload
  # All - Payload
  @staticmethod
  def encode_packet(payload):
    pickle_payload = pickle.dumps(payload, pickle.HIGHEST_PROTOCOL)
    return struct.pack('>I', len(pickle_payload)) + pickle_payload


  @staticmethod
  def decode_packet(payload):
    return pickle.loads(payload)
