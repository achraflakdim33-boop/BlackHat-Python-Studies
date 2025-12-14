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
Ouvrez un premier terminal et lancez le serveur qui va écouter sur le port 9998.
```bash
python3 TCP_server.py

# Résultat attendu : [*] Listening on 0.0.0.0:9998```

**Étape 2 : Lancer le Client** Ouvrez un Terminal 2 et lancez le client.
```bash
python3 TCP_client.py

#Résultat :
#    Le Client doit afficher la réponse reçue (ex: ACK).

#    Le Serveur doit afficher : [*] Accepted connection from... suivi du message Salut Serveur!.
