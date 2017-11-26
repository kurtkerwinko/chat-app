import socket


def recvall(sock, n):
  data = ''
  while len(data) < n:
    packet = sock.recv(n - len(data)) # Loop if > 4096
    if not packet:
      return None
    data += packet
  return data
