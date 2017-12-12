BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BR_BLACK = '\033[90m'
BR_RED = '\033[91m'
BR_GREEN = '\033[92m'
BR_YELLOW = '\033[93m'
BR_BLUE = '\033[94m'
BR_MAGENTA = '\033[95m'
BR_CYAN = '\033[96m'
BR_WHITE = '\033[97m'
END = '\033[0m'

def pr_red(text):
  print(BR_RED + text + END)

def pr_green(text):
  print(BR_GREEN + text + END)

def pr_yellow(text):
  print(BR_YELLOW + text + END)
