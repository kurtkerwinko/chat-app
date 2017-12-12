import json
import struct


class Packet():
  @staticmethod
  def client_packet(ptype, data={}):
    """ Client Packet Types """
    """ SRV_OK (STATUS), SRV_MSG, SRV_ERR, SRV_USR_CON, SRV_USR_DCN """
    """ USR_MSG, PRV_USR_MSG_SND, PRV_USR_MSG_RECV, USR_LST """
    pkt = {'type': ptype}
    if ptype in ['SRV_MSG', 'SRV_ERR']:
      pkt.update({'message': data})
    elif ptype in ['SRV_USR_CON', 'SRV_USR_DCN']:
      pkt.update({'username': data})
    elif ptype in ['USR_MSG', 'PRV_USR_MSG_SND', 'PRV_USR_MSG_RECV']:
      pkt.update({
        'username': data['username'],
        'message': data['message'],
      })
    elif ptype == 'USR_LST':
      pkt.update({'user_list': data})
    return Packet.encode_packet(pkt)


  @staticmethod
  def server_packet(ptype, user, data={}):
    """ Server Packet Types """
    """ USR_CON (STATUS), USR_DCN (STATUS), USR_SND, USR_WHPR """
    pkt = {'type': ptype}
    pkt.update(**user)
    if ptype == 'USR_SND':
      pkt.update({'message': data})
    elif ptype == 'USR_WHPR':
      pkt.update(data)
    return Packet.encode_packet(pkt)


  # 4 byte - Length of Payload
  # All - Payload
  @staticmethod
  def encode_packet(payload):
    json_payload = json.dumps(payload)
    return struct.pack('>I', len(json_payload)) + json_payload


  @staticmethod
  def decode_packet(payload):
    return json.loads(payload)
