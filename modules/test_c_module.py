import ctypes
import os

def load_c_module(module_name):
    if os.name == 'nt':  # Windows
        return ctypes.CDLL(f"{module_name}.dll")
    else:  # Linux
        return ctypes.CDLL(f"./{module_name}.so")

def run_c_module(module_name):
    try:
        c_module = load_c_module(module_name)
        run_func = c_module.run
        run_func.restype = ctypes.c_char_p
        result = run_func()
        print(result.decode())
    except Exception as e:
        print(f"Error running C module {module_name}: {e}")

if __name__ == '__main__':
    run_c_module("simple_module")

