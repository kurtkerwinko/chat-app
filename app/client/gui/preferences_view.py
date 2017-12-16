import re
from Tkinter import *


class PreferencesUI(Frame):
  def __init__(self, master, gui_config):
    self.root = Toplevel()
    self.root.winfo_toplevel().title("Preferences")
    self.root.protocol("WM_DELETE_WINDOW", self.cancel)
    self.view = master

    width = 375
    height = 300
    sizes = re.compile("([x]|[+])").split(self.view.root.geometry())
    offset_x = int(sizes[0]) - width
    offset_y = int(sizes[2]) - height - 50
    x = (self.view.root.winfo_x()) + (offset_x/2)
    y = (self.view.root.winfo_y()) + (offset_y/2) - 20
    self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    self.root.resizable(width=False, height=False)

    Frame.__init__(self, self.root)

    self.gui_config = gui_config
    self.grid(row=0, column=0, padx=20, pady=20, sticky=N+S+W+E)
    self.createWidgets()


  def createWidgets(self):
    def sample_color_change(option, hex_color):
      hex_pattern = re.compile(r"^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$")
      match = hex_pattern.match(hex_color.get())
      if match:
        self.text_colors[option][0].config(fg=hex_color.get())


    color_settings = ['DEFAULT_FG', 'USER_FG', 'MSG_FG', 'PRIV_USER_FG', 'PRIV_MSG_FG', 'SRV_MSG_FG', 'SRV_ERR_FG', 'ERROR_FG', 'HELP_FG', 'APP_MSG']

    self.text_colors = {}
    for i, cs in enumerate(color_settings):
      lb = Label(self, text=cs + ":")
      lb.grid(row=i, column=0, sticky=N+S+E)
      conf_color = self.gui_config.text_color[cs]

      tc_text = StringVar()
      color_entry = Entry(self, textvariable=tc_text)
      color_entry.insert(0, conf_color)
      tc_text.trace("w", lambda n, i, m, cs=cs, tc=tc_text: sample_color_change(cs, tc))
      color_entry.grid(row=i, column=1, columnspan=2, sticky=N+S+W+E)

      # Center label padx
      phax = 10
      slb = Label(self, text="SAMPLE", fg=conf_color, padx=phax)
      slb.grid(row=i, column=3, sticky=N+S+E)

      self.text_colors[cs] = slb, color_entry

    filler = Label(self, text="")
    filler.grid(row=len(color_settings))
    self.save = Button(self, text="Save Changes", command=self.save)
    self.save.grid(row=len(color_settings)+1, column=0, columnspan=2, sticky=N+S+W+E)

    self.cancel = Button(self, text="Cancel", command=self.cancel)
    self.cancel.grid(row=len(color_settings)+1, column=2, columnspan=2, sticky=N+S+W+E)


  def save(self):
    for cs in self.text_colors:
      self.gui_config.text_color[cs] = self.text_colors[cs][1].get()
    self.gui_config.save_config()
    self.view.refresh_config()
    self.close()


  def cancel(self):
    self.close()


  def close(self):
    self.view.preferences_ui = None
    self.root.destroy()
