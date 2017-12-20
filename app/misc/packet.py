import json
import struct


class Packet():
  @staticmethod
  def generate_packet(ptype, **kwargs):
    """ Client Packet Types """
    """ SRV_OK (STATUS), SRV_MSG, SRV_ERR, SRV_USR_CON, SRV_USR_DCN """
    """ USR_MSG, PRV_USR_MSG_SND, PRV_USR_MSG_RECV, USR_LST """

    """ Server Packet Types """
    """ USR_CON (STATUS), USR_DCN (STATUS), USR_SND, USR_WHPR """
    pkt = {'type': ptype}
    pkt.update(**kwargs)
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
