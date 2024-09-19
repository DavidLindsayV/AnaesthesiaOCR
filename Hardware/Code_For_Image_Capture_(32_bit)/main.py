"""This module contains the main function of the program"""
import atexit
import sys
from app import App

def main():
    """Creates and runs the app."""
    app = None
    try:
        if len(sys.argv) == 3:
            app = App(sys.argv[1], sys.argv[2])
        else:
            print("You need to provide two cmd arguments - the IPv4 address and the password used on the ssh connection")
            return
        app.run()
    except (RuntimeError, KeyboardInterrupt):
        pass
#    finally:
#        # Close the app upon any termination
#        atexit.register(app.close)

if __name__ == "__main__":
    main()
