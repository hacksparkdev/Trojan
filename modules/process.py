import psutil
import json

def list_processes():
    processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            process_info = proc.info
            processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def run():
    processes = list_processes()
    result = json.dumps(processes, indent=4)
    print(result)
    return result

if __name__ == "__main__":
    run()

