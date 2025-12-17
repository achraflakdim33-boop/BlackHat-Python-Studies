import sys
import socket
import threading

# Filtre pour afficher les caractères ASCII imprimables
# Si un caractère n'est pas imprimable, on affiche un point '.'
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16):
    """
    Affiche les données brutes sous forme hexadécimale et ASCII.
    Exemple de sortie :
    0000  50 4F 53 54 20 2F 20 48  54 54 50 2F 31 2E 31 0D  POST / HTTP/1.1.
    """
    if isinstance(src, bytes):
        src = src.decode(errors='ignore') # On décode les bytes en string pour l'affichage
        
    results = list()
    for i in range(0, len(src), length):
        # On prend un morceau de 16 caractères
        word = str(src[i:i+length])
        
        # On convertit en caractères imprimables
        printable = word.translate(HEX_FILTER)
        
        # On convertit en hexadécimal
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length * 3
        
        # On formate la ligne finale
        results.append(f'{i:04x}  {hexa:<{hexwidth}}  {printable}')
    
    # On affiche tout, ligne par ligne
    for line in results:
        print(line)

def receive_from(connection):
    """
    Reçoit toutes les données disponibles sur une socket.
    """
    buffer = b""
    
    # On définit un timeout de 5 secondes pour ne pas bloquer indéfiniment
    # si la cible n'envoie rien ou a fini d'envoyer.
    connection.settimeout(5)
    
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
        
    return buffer

def request_handler(buffer):
    # On cherche le mot "Secret" et on le remplace par "Hacke!"
    # Attention : on travaille avec des bytes (b"...")
    if b"Secret" in buffer:
        print("[!!] MOT SECRET DETECTE ! Modification du paquet...")
        buffer = buffer.replace(b"Secret", b"Hacke!")
    return buffer

def response_handler(buffer):
    """
    Permet de modifier les paquets reçus du serveur distant.
    """
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    """
    Gère la logique de trafic entre le client local et le serveur distant.
    """
    
    # 1. On se connecte au VRAI serveur (la cible)
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # 2. Si nécessaire, on vérifie si le serveur parle en premier
    # (Exemple : un serveur FTP envoie une bannière de bienvenue)
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        
        # On passe les données à notre fonction de modification (au cas où)
        remote_buffer = response_handler(remote_buffer)
        
        # S'il y a des données, on les renvoie à notre client local
        if len(remote_buffer):
            print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")
            client_socket.send(remote_buffer)
            
    # 3. La Boucle Principale d'échange (Le Ping-Pong)
    while True:
        # --- SENS : LOCAL VERS DISTANT ---
        
        # On lit ce que l'attaquant (nous) ou le client envoie
        local_buffer = receive_from(client_socket)
        
        if len(local_buffer):
            print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
            hexdump(local_buffer)
            
            # Opportunité de modifier le paquet avant l'envoi
            local_buffer = request_handler(local_buffer)
            
            # On envoie au serveur distant
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        # --- SENS : DISTANT VERS LOCAL ---
        
        # On lit la réponse du vrai serveur
        remote_buffer = receive_from(remote_socket)
        
        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)
            
            # Opportunité de modifier la réponse
            remote_buffer = response_handler(remote_buffer)
            
            # On renvoie la réponse au client local
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        # --- FERMETURE ---
        
        # Si plus personne n'a rien à dire, on coupe
        if not len(local_buffer) and not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break



def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    """
    Monte le serveur d'écoute principal.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to listen on {local_host}:{local_port}")
        print(f"[!!] Check for other listening sockets or correct permissions.")
        print(f"[!!] {e}")
        sys.exit(0)
        
    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        # On affiche qui s'est connecté
        line = f"> Received incoming connection from {addr[0]}:{addr[1]}"
        print(line)
        
        # On lance un thread pour gérer ce nouveau client
        # sans bloquer les autres qui pourraient arriver
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    
    # Configuration des arguments
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    # Le 'True' sert à dire si on attend que le serveur parle en premier (ex: FTP)
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
        
    # Lancement de la boucle d'écoute
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()


