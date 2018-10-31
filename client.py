import socket
import threading

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 8080            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

def listen():
    global tcp
    while True:
        print(tcp.recv(1024).decode("utf-8"))

t = threading.Thread(target = listen)
t.start()

msg = input()

while msg != 'exit()':
    tcp.send(msg.encode('utf-8'))
    msg = input()
tcp.close()
