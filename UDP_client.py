import socket

target_host = "127.0.0.1"
target_port = 9997

# Création de l'objet socket (DGRAM = UDP)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Envoi de données
# Pas de .connect() nécessaire en UDP !
print(f"[*] Envoi de données à {target_host}:{target_port}")
client.sendto(b"AAABBBCCC", (target_host, target_port))

# Réception de la réponse
# Attention : Le programme va "bloquer" (attendre) ici jusqu'à recevoir une réponse
try:
    data, addr = client.recvfrom(4096)
    print(f"[*] Reçu de {addr}: {data.decode()}")
except KeyboardInterrupt:
    print("\n[!] Arrêt par l'utilisateur.")

client.close()
