import signup
import signin

is_signed_in = False

def main():
    if is_signed_in == False:
        launch_signin()
    else:
        launch_signup()


def launch_signup():
    signup.signup_ui()

def launch_signin():
    signin.signin_ui()

def set_signedin(bool):
    is_signed_in = bool


if __name__ == "__main__":
    main()
