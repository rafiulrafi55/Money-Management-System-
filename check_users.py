from security_utils import encrypt_json,decrypt_json
import os

appdata_path = os.getenv("APPDATA")
folder_name = "Monefy"
folder_path = os.path.join(appdata_path, folder_name)
users_file_path = os.path.join(folder_path, "users.json")

with open(users_file_path, "rb") as file:
    data = decrypt_json(file.read())

print(data)