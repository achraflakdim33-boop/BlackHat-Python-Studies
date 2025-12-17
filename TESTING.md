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

## 3. Tester le Remplaçant Netcat (BHP Net Tool)

Ce script (`netcat.py`) peut agir comme un serveur ou un client. Voici comment tester sa fonction "Command Shell" (le plus utile).

### Scénario : Créer un Shell Distant

### Étape 1 : Lancer le "Serveur" (La Victime)
Dans le Terminal 1, nous lançons le script en mode écoute (`-l`), sur le port 5555 (`-p`), et nous activons le shell de commande (`-c`).

```bash
python3 netcat.py -l -p 5555 -c

# Résultat attendu : Le script attend en silence (listening)
```

### Étape 2 : Se Connecter depuis un Client
Dans le Terminal 2, connectez-vous au serveur avec Netcat.

```bash
nc 127.0.0.1 5555

# Vous obtenez un prompt : BHP:#>
```

### Étape 3 : Exécuter des Commandes
Tapez des commandes système dans le Terminal 2.

```bash
BHP:#> ls
BHP:#> pwd
BHP:#> whoami

# Les résultats s'affichent dans votre terminal client
```

### Notes de Sécurité
⚠️ **Attention** : Ce script donne un accès shell complet à votre système. Ne l'utilisez que dans un environnement de test contrôlé.

---

## 3. Tester le Proxy TCP (Interception & Modification)

Ce test vérifie que le proxy peut non seulement lire le trafic, mais aussi le modifier à la volée (attaque Man-in-the-Middle).

**Prérequis :** Avoir modifié la fonction `request_handler` dans `proxy.py` pour remplacer "Secret" par "Hacke!".

### Étape 1 : Lancer le Serveur TCP
Ouvrez un **Terminal 1** (La Cible).

```bash
python3 TCP_server.py

# Résultat : [*] Listening on 0.0.0.0:9998
```

### Étape 2 : Lancer le Proxy
Ouvrez un **Terminal 2** (L'Attaquant). On redirige le port 9999 vers le port 9998.

```bash
# Syntaxe : [LocalHost] [LocalPort] [RemoteHost] [RemotePort] [ReceiveFirst]
python3 proxy.py 127.0.0.1 9999 127.0.0.1 9998 False

# Résultat : [*] Listening on 127.0.0.1:9999
```

### Étape 3 : Lancer le Client
Ouvrez un **Terminal 3** (La Victime) et connectez-vous au Proxy (9999).

```bash
nc 127.0.0.1 9999
```

Tapez ensuite le message suivant et faites Entrée : `Ceci est un Secret`

### Vérification (Résultats)
* **Terminal 2 (Proxy)** : Vous voyez le trafic en hexdump. Il affiche `[!!] MOT SECRET DETECTE ! Modification du paquet...`.
* **Terminal 1 (Serveur)** : Le serveur reçoit le message modifié : `[*] Received: Ceci est un Hacke!`

---

## 4. Tester le Proxy FTP (Protocole Complexe)

Ce test vérifie que le proxy gère les protocoles où le serveur parle en premier (comme FTP). Nous utiliserons un serveur FTP public (ex: `ftp.sun.ac.za` ou `ftp.gnu.org`).

### Étape 1 : Lancer le Proxy en mode Root
Ouvrez un **Terminal 1**. Nous utilisons `sudo` car le port 21 est privilégié.

```bash
# Redirige le port 21 local vers le port 21 du serveur FTP public
sudo python3 proxy.py 127.0.0.1 21 ftp.sun.ac.za 21 True

# Résultat : [*] Listening on 127.0.0.1:21
```

### Étape 2 : Se connecter avec un Client FTP
Ouvrez un **Terminal 2**. Connectez-vous à votre propre machine (localhost).

```bash
ftp 127.0.0.1
```

* **Name** : `anonymous`
* **Password** : `test` (ou n'importe quoi)
* Une fois connecté (`ftp>`), tapez `ls` pour voir les fichiers distants.
* Tapez `bye` pour quitter.

### Vérification (Terminal 1)
Vous devez voir tout l'échange défiler en Hexdump :
* `[<==] Received X bytes from remote` (La bannière de bienvenue du serveur FTP).
* `[==>] Sent to remote` (Vos commandes `USER anonymous`, `PASS...`).
* Le contenu des dossiers listés par `ls`.

---

## 5. 🧪 Le Grand Test (Kicking the Tires)

C'est le moment de jouer à l'attaquant et à la victime sur la même machine.

### 1. Terminal 1 : L'Attaquant (Toi)
Lance le serveur qui va attendre la connexion de la victime.

```bash
python3 ssh_server.py

# Résultat attendu : [+] Listening for connection on 0.0.0.0:2222 ...
```

### 2. Terminal 2 : La Victime (Le Script Piégé)
Lance le script qui va se connecter à l'attaquant.

```bash
python3 ssh_rcmd.py
```

### 3. Interaction : Exécuter des Commandes
Retournez dans le **Terminal 1** (le serveur). Vous avez maintenant un prompt interactif.

```bash
Enter command: whoami
# Le résultat de la commande s'affiche

Enter command: ls
# Liste des fichiers

Enter command: pwd
# Répertoire courant

Enter command: exit
# Ferme la connexion
```

### Vérification
* **Terminal 1** : Affiche les résultats des commandes exécutées sur la "victime"
* **Terminal 2** : Le script continue de tourner et exécute les commandes reçues

### Notes
⚠️ **Sécurité** : Ce test utilise SSH avec des clés hardcodées dans le code. Ne jamais utiliser en production !

---

## Résumé des Ports Utilisés

| Script | Type | Port |
|--------|------|------|
| TCP_server.py | TCP | 9998 |
| TCP_client.py | TCP | 9998 |
| UDP_client.py | UDP | 9997 |
| netcat.py | TCP | 5555 (configurable) |
| proxy.py (TCP) | TCP | 9999 → 9998 |
| proxy.py (FTP) | TCP | 21 → 21 (remote) |
| ssh_server.py | SSH/TCP | 2222 |
| ssh_rcmd.py | SSH/TCP | 2222 |

---

## Dépannage

**Problème : "Address already in use"**
- Un autre processus utilise déjà le port. Tuez-le avec : `sudo lsof -i :9998` puis `kill -9 <PID>`

**Problème : Le client UDP ne reçoit rien**
- Vérifiez que Netcat est bien en mode UDP (`-u`)
- Assurez-vous d'avoir tapé une réponse dans Netcat après avoir lancé le client Python

**Problème : Permission denied**
- Sur certains systèmes, les ports < 1024 nécessitent `sudo`
