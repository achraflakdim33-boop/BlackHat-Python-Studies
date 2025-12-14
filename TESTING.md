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
# Résultat attendu : [*] Listening on 0.0.0.0:9998
