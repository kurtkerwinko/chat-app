from Tkinter import *
from app.client.gui.login_view import LoginUI
from app.client.gui.chat_view import ChatUI


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

    self.create_menu_bar()
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


  def create_menu_bar(self):
    # Menubar
    def test():
      print("ASD")

    # Menu Bar
    self.menu_bar = Menu(self)
    self.root.config(menu=self.menu_bar)

    # Chat Menu
    self.chat_menu = Menu(self.menu_bar, tearoff=0)
    self.chat_menu.add_command(label="Preferences", command=test)
    self.chat_menu.add_separator()
    self.chat_menu.add_command(label="Exit", command=self.root.quit)
    self.menu_bar.add_cascade(label='Chat', menu=self.chat_menu)

    self.menu_bar.add_command(label="Undo", command=test)
