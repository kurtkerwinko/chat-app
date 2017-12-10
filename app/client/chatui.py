from Tkinter import *
from random import randint
from app.client.client import Client

# Tkinter UI
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

    self.port = Entry(self)
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


class ChatUI(Frame):
  def __init__(self, parent, master, client):
    self.client = client

    self.parent = parent
    self.root = master
    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)
    self.root.winfo_toplevel().title("Logged in as <%s> @ %s" % (self.client.username, self.client.get_server_address()))

    Frame.__init__(self, self.root)

    self.grid()
    self.grid(row=0, column=0, sticky=N+S+W+E)
    self.createWidgets()

    self.root.update()
    self.connected()


  def connected(self):
    self.display.config(state=NORMAL)
    self.display.insert(END, "Connected to %s:%s" %(self.client.server_ip, self.client.server_port))
    self.display.config(state=DISABLED)
    self.client.start_receiving(self)


  def disconnect(self):
    self.client.disconnect()
    self.parent.show_login()


  def send_msg(self, event=None):
    if len(self.input.get()) > 0:
      self.client.send_message(self.input.get())
      self.input.delete(0, END)


  def recv_msg(self, message):
    self.display.config(state=NORMAL)
    self.display.insert(END, "\n" + message)
    self.display.config(state=DISABLED)
    self.display.see(END)


  def update_user_list(self, user_list):
    self.user_list.delete(0, END)
    for user in user_list:
      self.user_list.insert(END, user)


  def createWidgets(self):
    def input_reply_auto(text):
      if text.get().startswith(("/reply ", "/r ")):
        if self.client.last_received:
          self.input.delete(0, END)
          self.input.insert(0, "/w %s " % (self.client.last_received))


    def input_whisper_auto(event=None):
      if self.input.get().startswith(("/whisper ", "/w ")):
        args = self.input.get().split(" ", 2)
        if len(args) < 3:
          matching = [x for x in self.user_list.get(0, END) if x.startswith(args[1])]
          if len(matching) == 1:
            self.input.delete(0, END)
            self.input.insert(0, "/w %s " % (matching[0]))
          return("break")


    self.rowconfigure(0, weight=1)
    self.rowconfigure(1, weight=1000)
    self.rowconfigure(2, weight=1)

    self.columnconfigure(0, minsize=1, weight=10000)
    self.columnconfigure(1, minsize=1, weight=1)
    self.columnconfigure(2, minsize=1, weight=1)
    self.columnconfigure(3, minsize=1, weight=1)
    self.columnconfigure(4, minsize=1, weight=1)

    # Row 0
    self.disconnect = Button(self, text="DISCONNECT", command=self.disconnect)
    self.disconnect.grid(row=0, column=0, columnspan=3, sticky=N+S+W+E)

    self.user_list = Listbox(self, selectmode="SINGLE")
    self.user_list.grid(row=0, rowspan=3, column=3, sticky=N+S+W+E)
    self.user_list_ds = Scrollbar(self)
    self.user_list_ds.grid(row=0, rowspan=3, column=4, sticky=N+S+E)
    self.user_list_ds.config(command=self.user_list.yview)
    self.user_list.config(yscrollcommand=self.user_list_ds.set)

    # Row 1
    self.display = Text(self)
    self.display.grid(row=1, column=0, columnspan=2, sticky=N+S+W+E)
    self.display_ds = Scrollbar(self)
    self.display_ds.grid(row=1, column=2, sticky=N+S+E)
    self.display_ds.config(command=self.display.yview)
    self.display.config(state=DISABLED, wrap="word", yscrollcommand=self.display_ds.set)

    # Row 2
    input_text = StringVar()
    self.input = Entry(self, textvariable=input_text)
    input_text.trace("w", lambda *args: input_reply_auto(input_text))
    self.input.grid(row=2, column=0, sticky=N+S+W+E)
    self.input.bind("<Return>", self.send_msg)
    self.input.bind("<Tab>", input_whisper_auto)

    self.send = Button(self, text="SEND", command=self.send_msg)
    self.send.grid(row=2, column=1, columnspan=2, sticky=N+S+W+E)


class MainUI(Frame):
  def __init__(self, client, width, height):
    self.client = client

    self.root = Tk()

    Frame.__init__(self, self.root)

    x = (self.root.winfo_screenwidth()/2) - (width/2)
    y = (self.root.winfo_screenheight()/2) - (height/2)
    self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    self.grid()
    self.root.update()
    self.root.minsize(500, 500)

    self.show_login()


  def show_login(self):
    self.destroy_current_frame()
    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)

    self.current_frame = LoginUI(self, self.root, self.client)
    self.current_frame.grid(row=0, column=0)


  def logged_in(self):
    self.show_chat()


  def show_chat(self):
    self.destroy_current_frame()
    self.current_frame = ChatUI(self, self.root, self.client)
    self.current_frame.grid(row=0, column=0)


  def destroy_current_frame(self):
    if hasattr(self, 'current_frame') and self.current_frame:
      self.current_frame.grid_forget()
      self.current_frame.destroy()
