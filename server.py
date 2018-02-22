import sys
import socket
import threading
from app.server.gui.color_print import pr_green
from app.server.request_handler import RequestHandler

SERVER_IP = '0.0.0.0'
SERVER_PORT = 3000
SERVER_BACKLOG = 5

if (len(sys.argv) >= 2):
  SERVER_IP = sys.argv[1]
if (len(sys.argv) >= 3):
  SERVER_PORT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(SERVER_BACKLOG)

pr_green("SERVER: %s:%s" % (SERVER_IP, SERVER_PORT))

def dispatch_req(active_connections, client, address):
  rh = RequestHandler(active_connections, client, address)
  rh.handle_request()


# global active_connections should lock - threading
active_connections = {}
while True:
  try:
    (client, address) = s.accept()
    ct = threading.Thread(target=dispatch_req, args=(active_connections, client, address))
    ct.start()
  except Exception as e:
    if e.errno != 11:
      raise e
