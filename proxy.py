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
