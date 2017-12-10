import struct

# 1 byte - Command
# 1 byte - Length of Username
# X - Username
# 1 byte - Length of Password
# X - Password
# 4 byte - Length of Message
# All - Message
def encode_server_packet(command, username, password, message=""):
  c = get_i_command(command)
  user = struct.pack('>B', len(username)) + username
  pw = struct.pack('>B', len(password)) + password
  payload = struct.pack('>I', len(message)) + message
  return c + user + pw + payload

def encode_client_packet(command, payload):
  c = get_c_command(command)
  payload = struct.pack('>I', len(payload)) + payload
  return c + payload

def get_i_command(command):
  error = struct.pack('>B', 44)
  commands = {
    'CONNECT': struct.pack('>B', 1),
    'DISCONNECT': struct.pack('>B', 2),
    'SEND': struct.pack('>B', 3),
  }
  return commands.get(command, error)

def get_c_command(command):
  error = struct.pack('>B', 44)
  commands = {
    'MESSAGE': struct.pack('>B', 1),
    'WHISPER': struct.pack('>B', 2),
    'USERLIST': struct.pack('>B', 3),
  }
  return commands.get(command, error)
