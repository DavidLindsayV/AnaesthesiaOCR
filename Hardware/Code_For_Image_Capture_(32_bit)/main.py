"""This module contains the main function of the program"""
import atexit
import sys
from app import App

def main():
    """Creates and runs the app."""
    app = None
    try:
        if len(sys.argv) == 5:
            app = App(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print("You need to provide 4 cmd arguments - the remote user, the IPv4 address, the password used on the ssh connection and the folder to send images to")
            return
        app.run()
    except (RuntimeError, KeyboardInterrupt):
        pass
#    finally:
#        # Close the app upon any termination
#        atexit.register(app.close)

if __name__ == "__main__":
    main()
