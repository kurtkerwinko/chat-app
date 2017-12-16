from Tkinter import *
from app.client.gui.preferences_view import PreferencesUI


class ChatUI(Frame):
  def __init__(self, parent, master, client):
    self.client = client

    self.parent = parent
    self.root = master
    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)
    self.root.winfo_toplevel().title("Logged in as <%s> @ %s" % (self.client.user['username'], self.client.get_server_address()))

    Frame.__init__(self, self.root)

    self.gui_config = self.parent.gui_config
    self.grid(row=0, column=0, sticky=N+S+W+E)
    self.create_menu_bar()
    self.createWidgets()
    self.refresh_config()

    self.root.update()
    self.connected()


  def connected(self):
    self.display.config(state=NORMAL)
    msg = "Connected to %s:%s" % (self.client.server_ip, self.client.server_port)
    self.display.insert(END, msg, "APP_MSG")
    self.display.config(state=DISABLED)
    self.client.start_receiving(self)


  def disconnect(self, quit=False):
    self.client.disconnect()
    if quit:
      self.root.quit()
    else:
      self.parent.show_login()


  def send_msg(self, event=None):
    if len(self.input.get()) > 0:
      text = self.input.get()
      self.input.delete(0, END)
      if text.startswith("/"):
        self.chat_commands(text)
      else:
        self.client.send_message(text)


  def recv_msg(self, *argv):
    self.display.config(state=NORMAL)
    self.display.insert(END, "\n")
    for msg in argv:
      self.display.insert(END, msg[0], msg[1])
    self.display.config(state=DISABLED)
    self.display.see(END)


  def chat_commands(self, string):
    command = string.split(" ", 1)[0]
    if command in ["/help", "/h"]:
      message = "List of commands\n" \
              + "/help or /h -- show this\n" \
              + "/whisper or /w [user] [message] sends a private message\n" \
              + "/reply or /r [message] -- sends a reply to latest private message\n" \
              + "/disconnect or /dc -- disconnect from server"
      self.recv_msg([message, "HELP_FG"])
    elif command in ["/whisper", "/w"]:
      args = string.split(" ", 2)
      if len(args) == 3:
        self.client.send_whisper(args[1], args[2])
      else:
        message = "Invalid use of /whisper. /whisper [user] [message]"
        self.recv_msg([message, "ERROR_FG"])
    elif command in ["/reply", "/r"]:
      args = string.split(" ", 1)
      if len(args) == 2:
        last_recv = self.client.last_received
        if last_recv:
          self.chat_commands(" ".join(["/w", last_recv, args[1]]))
        else:
          message = "No one sent you a private message."
          self.recv_msg([message, "ERROR_FG"])
      else:
        message = "Invalid use of /reply. /reply [message]"
        self.recv_msg([message, "ERROR_FG"])
    elif command in ["/disconnect", "/dc"]:
      self.disconnect()
    else:
      message = "Invalid Command"
      self.recv_msg([message, "ERROR_FG"])


  def update_view(self, pkt):
    if pkt['type'] == 'USR_LST':
      self.user_list.delete(0, END)
      for user in pkt['user_list']:
        self.user_list.insert(END, user)
    else:
      self.recv_msg(*self.construct_message(pkt))


  def construct_message(self, pkt):
    if pkt['type'] == 'SRV_MSG':
      return (["<SERVER> {message}".format(**pkt), "SRV_MSG_FG"], )
    if pkt['type'] == 'SRV_ERR':
      return (["<SERVER ERROR> {message}".format(**pkt), "SRV_ERR_FG"], )
    if pkt['type'] == 'SRV_USR_CON':
      return (
        ["{username}".format(**pkt), "USER_FG"],
        [" CONNECTED", "SRV_MSG_FG"],
      )
    if pkt['type'] == 'SRV_USR_DCN':
      if type(pkt['username']) == list:
        msg = ()
        for user in pkt['username']:
          msg += ([user, "USER_FG"], [", ", "SRV_MSG_FG"])
        return msg[:-1] + ([" DISCONNECTED", "SRV_MSG_FG"], )
      else:
        return (
          [pkt['username'], "USER_FG"],
          [" DISCONNECTED", "SRV_MSG_FG"],
        )
    if pkt['type'] == 'USR_MSG':
      return (
        ["{username}".format(**pkt), "USER_FG"],
        [": {message}".format(**pkt), "MSG_FG"],
      )
    if pkt['type'] == 'PRV_USR_MSG_SND':
      self.client.last_received = pkt['username']
      return (
        ["<To: ", "PRIV_MSG_FG"],
        ["{username}".format(**pkt), "PRIV_USER_FG"],
        ["> ", "PRIV_MSG_FG"],
        ["{message}".format(**pkt), "PRIV_MSG_FG"],
      )
    if pkt['type'] == 'PRV_USR_MSG_RECV':
      self.client.last_received = pkt['username']
      return (
        ["<From: ", "PRIV_MSG_FG"],
        ["{username}".format(**pkt), "PRIV_USER_FG"],
        ["> ", "PRIV_MSG_FG"],
        ["{message}".format(**pkt), "PRIV_MSG_FG"],
      )


  def show_preferences(self):
    if not self.preferences_ui:
      self.preferences_ui = PreferencesUI(self.parent, self.gui_config)


  def create_menu_bar(self):
    self.menu_bar = Menu(self)
    self.root.config(menu=self.menu_bar)
    self.chat_menu = Menu(self.menu_bar, tearoff=0)
    self.chat_menu.add_command(label="Preferences", command=self.show_preferences)
    self.chat_menu.add_command(label="Disconnect", command=self.disconnect)
    self.chat_menu.add_separator()
    self.chat_menu.add_command(label="Exit", command=lambda: self.disconnect(True))
    self.menu_bar.add_cascade(label='Chat', menu=self.chat_menu)
    self.preferences_ui = None


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

    # Row 0 ~ 1
    self.display = Text(self)
    self.display.grid(row=0, rowspan=2, column=0, columnspan=2, sticky=N+S+W+E)
    self.display_ds = Scrollbar(self)
    self.display_ds.grid(row=1, column=2, sticky=N+S+E)
    self.display_ds.config(command=self.display.yview)
    self.display.config(state=DISABLED, wrap="word", yscrollcommand=self.display_ds.set)

    self.user_list = Listbox(self, selectmode="SINGLE")
    self.user_list.grid(row=0, rowspan=3, column=3, sticky=N+S+W+E)
    self.user_list_ds = Scrollbar(self)
    self.user_list_ds.grid(row=0, rowspan=3, column=4, sticky=N+S+E)
    self.user_list_ds.config(command=self.user_list.yview)
    self.user_list.config(yscrollcommand=self.user_list_ds.set)

    # Row 2
    input_text = StringVar()
    self.input = Entry(self, textvariable=input_text)
    input_text.trace("w", lambda *args: input_reply_auto(input_text))
    self.input.grid(row=2, column=0, sticky=N+S+W+E)
    self.input.bind("<Return>", self.send_msg)
    self.input.bind("<Tab>", input_whisper_auto)

    self.send = Button(self, text="SEND", command=self.send_msg)
    self.send.grid(row=2, column=1, columnspan=2, sticky=N+S+W+E)


  def refresh_config(self):
    for cs in self.gui_config.text_color:
      fgc = self.gui_config.text_color[cs]
      self.display.tag_config(cs, foreground=fgc)
