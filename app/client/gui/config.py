import re


class GUIConfig():
  def __init__(self):
    self.default_text_color = {
      'DEFAULT_FG': "#000000",
      'USER_FG': "#00afac",
      'MSG_FG': "#000000",
      'PRIV_USER_FG': "#b250b2",
      'PRIV_MSG_FG': "#b250b2",
      'SRV_MSG_FG': "#000000",
      'SRV_ERR_FG': "#ff4700",
      'ERROR_FG': "#ff4700",
      'HELP_FG': "#7b78ba",
      'APP_MSG': "#000000",
    }
    self.load_config()


  def load_config(self):
    self.text_color = {
      'DEFAULT_FG': "#000000",
      'USER_FG': "#00afac",
      'MSG_FG': "#000000",
      'PRIV_USER_FG': "#b250b2",
      'PRIV_MSG_FG': "#b250b2",
      'SRV_MSG_FG': "#000000",
      'SRV_ERR_FG': "#ff4700",
      'ERROR_FG': "#ff4700",
      'HELP_FG': "#7b78ba",
      'APP_MSG': "#000000",
    }
    # missing load from config file


  def save_config(self):
    def format_hex(c):
      if len(c) == 4:
        return ('#' + c[1]*2 + c[2]*2 + c[3]*2).lower()
      return c.lower()

    hex_pattern = re.compile(r"^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$")
    for cs in self.text_color:
      match = hex_pattern.match(self.text_color[cs])
      if match:
        self.text_color[cs] = format_hex(self.text_color[cs])
      else:
        self.text_color[cs] = self.default_text_color[cs]

    # missing save to config file
