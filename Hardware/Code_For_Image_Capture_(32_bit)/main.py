"""This module contains the main function of the program"""
import atexit
import sys
from app import App

def main():
    """Creates and runs the app."""
    app = None
    try:
        if len(sys.argv) == 4:
            app = App(int(sys.argv[1]), int(sys.argv[2]),sys.argv[3])
        else:
            app = App()
        app.run()
    except (RuntimeError, KeyboardInterrupt):
        pass
    finally:
        # Close the app upon any termination
        atexit.register(app.close)

if __name__ == "__main__":
    main()
