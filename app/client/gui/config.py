import os
import sys
import re


class GUIConfig():
  def __init__(self):
    self.config_path = os.path.join("app", "client", "config")
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
      'DEFAULT_FG': self.default_text_color['DEFAULT_FG'],
      'USER_FG': self.default_text_color['USER_FG'],
      'MSG_FG': self.default_text_color['MSG_FG'],
      'PRIV_USER_FG': self.default_text_color['PRIV_USER_FG'],
      'PRIV_MSG_FG': self.default_text_color['PRIV_MSG_FG'],
      'SRV_MSG_FG': self.default_text_color['SRV_MSG_FG'],
      'SRV_ERR_FG': self.default_text_color['SRV_ERR_FG'],
      'ERROR_FG': self.default_text_color['ERROR_FG'],
      'HELP_FG': self.default_text_color['HELP_FG'],
      'APP_MSG': self.default_text_color['APP_MSG'],
    }

    if os.path.exists(self.config_path):
      with open(self.config_path, "r") as f:
        for line in f:
          opt, val = line.replace("\n", "").split(": ")
          if opt in self.text_color and self.hex_color(val):
            self.text_color[opt] = self.format_hex(val)
    self.save_config()


  def save_config(self):
    for cs in self.text_color:
      if self.hex_color(self.text_color[cs]):
        self.text_color[cs] = self.format_hex(self.text_color[cs])
      else:
        self.text_color[cs] = self.default_text_color[cs]

    with open(self.config_path, "w+") as f:
      for opt in self.text_color:
        f.write("%s: %s\n" % (opt, self.text_color[opt]))


  def hex_color(self, c):
    hex_pattern = re.compile(r"^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$")
    return hex_pattern.match(c)


  def format_hex(self, c):
    if len(c) == 4:
      return ('#' + c[1]*2 + c[2]*2 + c[3]*2).lower()
    return c.lower()
