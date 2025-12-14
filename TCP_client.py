import socket

target_host = "127.0.0.1"
target_port = 9998

# Création de l'objet socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connexion au serveur
client.connect((target_host, target_port))

# Envoi de données (Message test)
client.send(b"Salut Serveur! C'est Achraf.")

# Réception de la réponse
response = client.recv(4096)

print(response.decode())
client.close()
