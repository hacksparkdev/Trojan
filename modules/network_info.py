import socket
import json
import psutil

def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        return {"error": str(e)}

def get_network_interfaces():
    interfaces = psutil.net_if_addrs()
    return {iface: [addr.address for addr in addrs] for iface, addrs in interfaces.items()}

def run():
    ip_address = get_ip_address()
    interfaces = get_network_interfaces()
    result = {
        "IP Address": ip_address,
        "Network Interfaces": interfaces
    }
    result_json = json.dumps(result, indent=4)
    print(result_json)
    return result_json

if __name__ == "__main__":
    run()

