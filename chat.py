from app.client.client import Client
from app.client.chatui import MainUI


if __name__ == '__main__':
  client = Client()
  mainui = MainUI(client, 500, 500)
  mainui.mainloop()
