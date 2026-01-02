import os
import subprocess
import sys


APPDATA_FOLDER = r"C:\Users\Rafiul\AppData\Roaming\Money-Management-System"
CURRENT_USER_FILE = os.path.join(APPDATA_FOLDER, "current_user.json")
CORE_APP = os.path.join(APPDATA_FOLDER, "Core.py")
LOGIN_APP = os.path.join(APPDATA_FOLDER, "login.py")

if os.path.exists(CURRENT_USER_FILE):
    subprocess.Popen([sys.executable, CORE_APP])
else:
    subprocess.Popen([sys.executable, LOGIN_APP])