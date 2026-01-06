import os
import subprocess
import sys
import shutil

APPDATA_FOLDER = r"C:\Users\Rafiul\AppData\Roaming\Money-Management-System"
SOURCE_FOLDER = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(APPDATA_FOLDER):
    os.makedirs(APPDATA_FOLDER)
    FILES_TO_COPY = [
        "login.py",
        "Core.py",
        "security_utils.py",
        "main.py",
        "Forgot_Password.py",
        "signup.py"
    ]
    for file_name in FILES_TO_COPY:
        src = os.path.join(SOURCE_FOLDER, file_name)
        dst = os.path.join(APPDATA_FOLDER, file_name)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"Copied {file_name} to AppData")
        else:
            print(f"WARNING: {file_name} not found in source folder!")

CURRENT_USER_FILE = os.path.join(APPDATA_FOLDER, "current_user.json")
CORE_APP = os.path.join(APPDATA_FOLDER, "Core.py")
LOGIN_APP = os.path.join(APPDATA_FOLDER, "login.py")

if os.path.exists(CURRENT_USER_FILE):
    subprocess.Popen([sys.executable, CORE_APP])
else:
    subprocess.Popen([sys.executable, LOGIN_APP])