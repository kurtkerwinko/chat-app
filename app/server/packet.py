import struct

# 1 byte - Command
# 4 byte - Length of Message
# All - Message
def encode_server_packet(command, username, password, message=""):
  c = get_i_command(command)
  payload = username + "|" + password + "|" + message
  return c + struct.pack('>I', len(payload)) + payload

def encode_client_packet(message):
  return struct.pack('>I', len(message)) + message

def get_i_command(command):
  error = struct.pack('>B', 44)
  commands = {
    'CONNECT': struct.pack('>B', 1),
    'DISCONNECT': struct.pack('>B', 2),
    'SEND': struct.pack('>B', 3),
  }
  return commands.get(command, error)
