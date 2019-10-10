import os
import sys
import xerox
import pickle
import argparse
import threading
import pprint
import time
from pynput import keyboard

try:
    import utils
except ImportError:
    import clix.utils as utils
from .gui import clipboard

global available_keys

available_keys = utils.available_keys


# previously logged key
prev_Key = None
# path to site package
curr_dir = os.getcwd()

key_binding = []

# loading key_binding from config file
# try:
with open(os.path.join(os.path.dirname(__file__), 'config'), "rb") as f:
    key_binding = pickle.load(f)

# if file does not exist create empty file
try:
    clips_data = open(os.path.join(os.path.dirname(__file__),
                      'clips_data'), "rb")
    utils.clips = pickle.load(clips_data)
    clips_data.close()
except FileNotFoundError:
    utils.clips = []

global curros
if sys.platform == 'linux' or sys.platform == 'linux2':
    curros = 'linux'
elif sys.platform == 'win32':
    curros = 'win'


# Collect events until released
class ThreadedKeyBind(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        with keyboard.Listener(
                on_press=self.on_press,
                ) as listener:
            listener.join()

    def on_press(self, key):
        """
        function called when any key is pressed
        """
        global prev_Key, key_binding
        if (key == keyboard.Key.space and
                prev_Key == keyboard.Key.ctrl_l):
            if utils.active == 1:
                utils.active = 0
            elif utils.active == 0:
                utils.active = 1
            prev_Key = None

        elif (((pprint.pformat(key) == "'c'" or
                pprint.pformat(key) == "u'c'") and
                prev_Key == keyboard.Key.ctrl) or
                pprint.pformat(key) == "'\\x03'"):
            try:
                if curros == "linux":
                    self.text = xerox.paste()
                else:
                    time.sleep(.2)
                    self.text = utils.root.clipboard_get()
            except:
                self.text = ""

            utils.clips.append(self.text)
            # pickle clips data
            with open(os.path.join(os.path.dirname(__file__),
                      'clips_data'), "wb") as f:
                pickle.dump(utils.clips, f, protocol=2)

            print("You just copied: {}".format(self.text))

        elif (((pprint.pformat(key) == "'z'" or
                pprint.pformat(key) == "u'z'") and
                prev_Key == keyboard.Key.ctrl) or
                pprint.pformat(key) == "'\\x1a'"):
            utils.root.destroy()
            self.stop()

        else:
            prev_Key = key

        return True


def _show_available_keybindings():
    """
    function to show available keys
    """
    print("Available Keys: "+"\n")
    for key in available_keys:
        print(key)


def get_current_keybinding():
    """
    function to show current key-binding
    """
    global key_binding
    temp = {b: a for a, b in available_keys.items()}
    return temp[key_binding[0]] + "+" + temp[key_binding[1]]


def create_new_session():
    """
     clear old session
    """
    with open(os.path.join(os.path.dirname(__file__),
              'clips_data'), "wb") as f:
        utils.clips = []
        pickle.dump(utils.clips, f, protocol=2)


def main():
    """
    main function (CLI endpoint)
    """
    global key_binding

    parser = argparse.ArgumentParser()

    help = """Set alternate key binding. Default is LCTRL+SPACE
                Format :- <KEY1>+<KEY2>. Ex:- RCTRL+RALT .
                To see availble key bindings use 'clix -a' option"""

    parser.add_argument("-s", "--set-keybinding", type=str,
                        default=None, help=help)

    parser.add_argument("-a", "--show-available-keybindings",
                        help="Show available key bindings",
                        action="store_true")

    parser.add_argument("-c", "--show-current-keybinding",
                        action="store_true")

    parser.add_argument("-n", "--new-session", action="store_true",
                        help="start new session clearing old session")

    args = parser.parse_args()
    args_dict = vars(args)

    if args.show_current_keybinding:
        print("Current key binding is: {}".format(get_current_keybinding()))
        sys.exit()

    elif args.show_available_keybindings:
        _show_available_keybindings()
        sys.exit()

    elif args.set_keybinding:
        try:
            keys = args_dict['set_keybinding'].split('+')
            key_binding = [available_keys[keys[0]],
                           available_keys[keys[1]]]
        except KeyError:
            print("Please follow the correct format.")
        else:
            with open(os.path.join(os.path.dirname(__file__),
                      'config'), "wb") as f:
                pickle.dump(key_binding, f, protocol=2)
        finally:
            sys.exit()

    elif args.new_session:
        print("new session")
        create_new_session()

    # seperate thread because of tkinter mainloop
    # which blocks every other event
    ThreadedKeyBind().start()

    # start gui
    utils.active = 1
    clipboard(utils.clips)


if __name__ == "__main__":
    main()
