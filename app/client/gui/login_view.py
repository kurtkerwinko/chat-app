from Tkinter import *
from random import randint


class LoginUI(Frame):
  def __init__(self, parent, master, client):
    self.client = client

    self.parent = parent
    self.root = master
    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)
    self.root.winfo_toplevel().title("Chat - Login")

    Frame.__init__(self, self.root)

    self.USERNAME_LIMIT = 9
    self.PASSWORD_LIMIT = 16
    self.SERVER_LIMIT = 15
    self.PORT_LIMIT = 5

    self.grid()
    self.createWidgets()

    self.root.update()


  def createWidgets(self):
    def character_limit(text, limit):
      if len(text.get()) > 0:
          text.set(text.get()[:limit])

    self.rowconfigure(0, weight=1)
    self.rowconfigure(1, weight=1)
    self.rowconfigure(2, weight=1)
    self.rowconfigure(3, weight=1)
    self.rowconfigure(4, weight=1)

    self.columnconfigure(0, minsize=1, weight=1)
    self.columnconfigure(1, minsize=1, weight=1)

    self.username_label = Label(self, text="Username:")
    self.username_label.grid(row=0, column=0, sticky=N+S+E)
    self.password_label = Label(self, text="Password:")
    self.password_label.grid(row=1, column=0, sticky=N+S+E)
    self.server_label = Label(self, text="Server IP:")
    self.server_label.grid(row=2, column=0, sticky=N+S+E)
    self.port_label = Label(self, text="Port:")
    self.port_label.grid(row=3, column=0, sticky=N+S+E)

    username_text = StringVar()
    self.username = Entry(self, textvariable=username_text)
    username_text.trace("w", lambda *args: character_limit(username_text, self.USERNAME_LIMIT))
    self.username.grid(row=0, column=1, sticky=N+S+W+E)
    self.username.insert(0, "user-" + str(randint(1, 1000)))

    password_text = StringVar()
    self.password = Entry(self, show="*", textvariable=password_text)
    password_text.trace("w", lambda *args: character_limit(password_text, self.PASSWORD_LIMIT))
    self.password.grid(row=1, column=1, sticky=N+S+W+E)

    server_text = StringVar()
    self.server = Entry(self, textvariable=server_text)
    server_text.trace("w", lambda *args: character_limit(server_text, self.SERVER_LIMIT))
    self.server.grid(row=2, column=1, sticky=N+S+W+E)
    self.server.insert(0, "localhost")

    port_text = StringVar()
    self.port = Entry(self, textvariable=port_text)
    port_text.trace("w", lambda *args: character_limit(port_text, self.PORT_LIMIT))
    self.port.grid(row=3, column=1, sticky=N+S+W+E)
    self.port.insert(0, "3000")

    self.login = Button(self, text="Connect", command=self.connect)
    self.login.grid(row=4, column=0, columnspan=2, sticky=N+S+W+E)


  def connect(self, event=None):
    if not self.port.get().isdigit():
      return None

    self.client.connect(self.server.get(), int(self.port.get()), self.username.get(), self.password.get())

    if self.client.status == "CONNECTED":
      self.parent.logged_in()