import json
import struct

# 4 byte - Length of Payload
# All - Payload
def encode_packet(payload):
  json_payload = json.dumps(payload)
  return struct.pack('>I', len(json_payload)) + json_payload


def decode_packet(payload):
  return json.loads(payload)
