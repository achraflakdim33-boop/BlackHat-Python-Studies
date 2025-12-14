# Guide de Test des Scripts

Ce projet contient des scripts Python pour tester des connexions réseau basiques (TCP et UDP).
Voici comment vérifier qu'ils fonctionnent correctement.

## Prérequis
* Python 3
* Netcat (`nc`) pour simuler des serveurs/clients

---

## 1. Tester le Client & Serveur TCP

Ce test fait communiquer deux scripts Python entre eux.

**Étape 1 : Lancer le Serveur**
Ouvrez un Terminal 1 et lancez le serveur qui va écouter sur le port 9998.
```bash
python3 TCP_server.py

# Résultat attendu : [*] Listening on 0.0.0.0:9998

Étape 2 : Lancer le Client Ouvrez un Terminal 2 et lancez le client.
Bash

python3 TCP_client.py

# Résultat Client : Doit afficher la réponse reçue (ex: ACK)

Vérification finale (Terminal 1)
Plaintext

# Le Serveur doit afficher : 
# [*] Accepted connection from 127.0.0.1:xxxxx
# [*] Received: Salut Serveur! C'est Achraf.

2. Tester le Client UDP

Le script UDP n'ayant pas de connexion, nous utiliserons Netcat pour voir les données passer.

Étape 1 : Préparer l'écouteur Netcat Ouvrez un Terminal 1 et lancez Netcat en mode UDP sur le port 9997.
Bash

nc -u -lvp 9997

# Résultat : Netcat attend (listening on [any] 9997 ...)

Étape 2 : Lancer le Client Python Ouvrez un Terminal 2 et lancez le script.
Bash

python3 UDP_client.py

# Note : Le terminal va sembler bloqué, c'est normal (voir étape suivante).

Étape 3 : Interaction (Obligatoire) Le script Python attend une réponse pour finir.

    Regardez le Terminal 1 (Netcat) : vous devez voir AAABBBCCC.

    Tapez un message dans Netcat (ex: Bien recu) et faites Entrée.

    Le script Python dans le Terminal 2 recevra le message et s'arrêtera.
