import psutil

def list_processes():
    # Iterate over all processes and print their PID and name
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            # Get process information
            process_info = proc.info
            print(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle the case where the process is no longer available or access is denied
            pass

def run():
    list_processes()
    print("Process management module executed")

if __name__ == "__main__":
    run()

