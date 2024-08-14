import socket
import json
import psutil
import requests

# URL for posting results to Node.js server
NODE_SERVER_URL = "http://10.0.100.100:3000/command"

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

def send_results_to_server(results):
    try:
        payload = {"command": "network_info", "result": results}
        response = requests.post(NODE_SERVER_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Results sent to Node.js server successfully.")
    except requests.exceptions.RequestException as e:
        print(f"[*] Failed to send results to Node.js server: {e}")

def run():
    ip_address = get_ip_address()
    interfaces = get_network_interfaces()
    result = {
        "IP Address": ip_address,
        "Network Interfaces": interfaces
    }
    result_json = json.dumps(result, indent=4)
    print(result_json)
    
    # Send results to the Node.js server
    send_results_to_server(result)

    return result_json

if __name__ == "__main__":
    run()

