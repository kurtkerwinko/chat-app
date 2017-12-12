from Tkinter import *


class ChatUI(Frame):
  def __init__(self, parent, master, client):
    self.client = client

    self.parent = parent
    self.root = master
    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)
    self.root.winfo_toplevel().title("Logged in as <%s> @ %s" % (self.client.user['username'], self.client.get_server_address()))

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


  def update_view(self, pkt):
    if pkt['type'] == 'USR_LST':
      self.user_list.delete(0, END)
      for user in pkt['user_list']:
        self.user_list.insert(END, user)
    else:
      self.recv_msg(self.construct_message(pkt))


  def construct_message(self, pkt):
    if pkt['type'] == 'SRV_MSG':
      return "<SERVER> {message}".format(**pkt)
    if pkt['type'] == 'SRV_ERR':
      return "<SERVER ERROR> {message}".format(**pkt)
    if pkt['type'] == 'SRV_USR_CON':
      return "{username} CONNECTED".format(**pkt)
    if pkt['type'] == 'SRV_USR_DCN':
      return "{username} DISCONNECTED".format(**pkt)
    if pkt['type'] == 'USR_MSG':
      return "{username}: {message}".format(**pkt)
    if pkt['type'] == 'PRV_USR_MSG_SND':
      self.client.last_received = pkt['username']
      return "<To: {username}> {message}".format(**pkt)
    if pkt['type'] == 'PRV_USR_MSG_RECV':
      self.client.last_received = pkt['username']
      return "<From: {username}> {message}".format(**pkt)


  def createWidgets(self):
    def longest_common_string(match, usr_list):
      if len(usr_list) == 0:
        return match
      if all(x.startswith(match) for x in usr_list):
        if len(match) >= len(min(usr_list, key=len)):
          return match
        return longest_common_string(match + usr_list[0][len(match)], usr_list)
      return match[:-1]


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
          match = longest_common_string(args[1], matching)
          if len(matching) == 1:
            match += " "
          self.input.delete(0, END)
          self.input.insert(0, "/w %s" % (match))
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
