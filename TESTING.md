# Guide de Test des Scripts

Ce projet contient des scripts Python pour tester des connexions réseau basiques (TCP et UDP).
Voici comment vérifier qu'ils fonctionnent correctement.

## Prérequis
* Python 3
* Netcat (`nc`) pour simuler des serveurs/clients

---

## 1. Tester le Client & Serveur TCP

Ce test fait communiquer deux scripts Python entre eux.

### Étape 1 : Lancer le Serveur
Ouvrez un Terminal 1 et lancez le serveur qui va écouter sur le port 9998.

```bash
python3 TCP_server.py

# Résultat attendu : [*] Listening on 0.0.0.0:9998
```

### Étape 2 : Lancer le Client

**Option A : Utiliser le script Python**

Ouvrez un Terminal 2 et lancez le client.

```bash
python3 TCP_client.py

# Résultat Client : Doit afficher la réponse reçue (ex: ACK)
```

**Option B : Utiliser Netcat comme client**

Alternativement, vous pouvez utiliser Netcat pour tester le serveur.

```bash
nc 127.0.0.1 9998

# Puis tapez un message et faites Entrée
# Résultat : Le serveur vous répondra et vous verrez sa réponse
```

### Vérification finale (Terminal 1)

```
# Le Serveur doit afficher : 
# [*] Accepted connection from 127.0.0.1:xxxxx
# [*] Received: <votre message>
```

---

## 2. Tester le Client UDP

Le script UDP n'ayant pas de connexion, nous utiliserons Netcat pour voir les données passer.

### Étape 1 : Préparer l'écouteur Netcat
Ouvrez un Terminal 1 et lancez Netcat en mode UDP sur le port 9997.

```bash
nc -u -lvp 9997

# Résultat : Netcat attend (listening on [any] 9997 ...)
```

### Étape 2 : Lancer le Client Python
Ouvrez un Terminal 2 et lancez le script.

```bash
python3 UDP_client.py

# Note : Le terminal va sembler bloqué, c'est normal (voir étape suivante).
```

### Étape 3 : Interaction (Obligatoire)
Le script Python attend une réponse pour finir.

1. Regardez le Terminal 1 (Netcat) : vous devez voir `AAABBBCCC`.
2. Tapez un message dans Netcat (ex: `Bien recu`) et faites Entrée.
3. Le script Python dans le Terminal 2 recevra le message et s'arrêtera.

---

## Résumé des Ports Utilisés

| Script | Type | Port |
|--------|------|------|
| TCP_server.py | TCP | 9998 |
| TCP_client.py | TCP | 9998 |
| UDP_client.py | UDP | 9997 |

---

## Dépannage

**Problème : "Address already in use"**
- Un autre processus utilise déjà le port. Tuez-le avec : `sudo lsof -i :9998` puis `kill -9 <PID>`

**Problème : Le client UDP ne reçoit rien**
- Vérifiez que Netcat est bien en mode UDP (`-u`)
- Assurez-vous d'avoir tapé une réponse dans Netcat après avoir lancé le client Python

**Problème : Permission denied**
- Sur certains systèmes, les ports < 1024 nécessitent `sudo`
