from Tkinter import *
from app.client.gui.login_view import LoginUI
from app.client.gui.chat_view import ChatUI
from app.client.gui.config import GUIConfig


class MainUI(Frame):
  def __init__(self, client, width, height):
    self.client = client

    self.root = Tk()

    Frame.__init__(self, self.root)

    x = (self.root.winfo_screenwidth()/2) - (width/2)
    y = (self.root.winfo_screenheight()/2) - (height/2)
    self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    self.gui_config = GUIConfig()

    self.grid()
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
