import socket


def recvall(sock, n):
  data = ''
  while len(data) < n:
    try:
      packet = sock.recv(n - len(data)) # Loop if > 4096
      data += packet
    except Exception as e:
      if e.errno != 11:
        raise e
  return data
