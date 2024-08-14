import psutil

def list_processes():
    for proc in 
psutil.process_iter(['pid', 'name']):
    print(proc.info)

def run():
    list_processes()
    print("Process management module executed")

