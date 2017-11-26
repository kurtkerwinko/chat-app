import sys
import socket
import threading
from app.server.request_handler import RequestHandler

SERVER_IP = ''
SERVER_PORT = 3000
SERVER_BACKLOG = 5

if (len(sys.argv) >= 2):
  SERVER_IP = sys.argv[1]
if (len(sys.argv) >= 3):
  SERVER_PORT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(SERVER_BACKLOG)

print("SERVER: %s:%s" % (SERVER_IP, SERVER_PORT))

def dispatch_req(active_connections, client, address):
  rh = RequestHandler(active_connections, client, address)
  rh.handle_request()


# global active_connections should lock - threading
active_connections = {}
while True:
  (client, address) = s.accept()
  ct = threading.Thread(target=dispatch_req, args=(active_connections, client, address))
  ct.daemon = True
  ct.start()
