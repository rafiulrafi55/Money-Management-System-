import signup
import signin
import dashboard
import os

appdata_path = os.getenv("APPDATA")
folder_name = "Monefy"
folder_path = os.path.join(appdata_path, folder_name)
current_user_file = os.path.join(folder_path, "current_user.json")





def main():
    if os.path.exists(current_user_file):
        launch_dashboard()
    else:
        launch_signin()


def launch_signup():
    signup.signup_ui()

def launch_signin():
    signin.signin_ui()

def launch_dashboard():
    dashboard.dashboard_ui()


if __name__ == "__main__":
    main()
