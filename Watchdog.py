import smtplib
import time
import subprocess
import shutil
import socket
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

directory_to_watch = "/chemin/vers/le/repertoire/SMTP"

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"Le fichier {event.src_path} a été modifié. Je check les statuts SMTP...")
        try:
            if not check_smtp_status():
                print("Le service SMTP a été stoppé")
                restart_smtp_service()
                print("Le service SMTP a été redémarré.")

                # Après le redémarrage, effectuez des étapes de diagnostic
                if not check_smtp_status():
                    
                    print("Le service SMTP ne fonctionne pas après le redémarrage, je check les statuts SMTP...")

                    check_smtp_logs()
                    check_smtp_port()
                    check_smtp_auth()
                    check_smtp_tls_ssl()
                    check_smtp_server_status()
                    check_disk_space()
                    test_smtp_connection_manuel()

        except Exception as e:
            print(f"Une erreur s'est produite lors de la vérification des statuts SMTP : {e}")

def check_smtp_status():
    try:
        # Établir une connexion au serveur SMTP 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('ousmaneb2307@gmail.com', 'kewf hvaf zvlm hrkf')
        server.quit()
        return True
    except smtplib.SMTPConnectError:
        return False
    
def restart_smtp_service():
    # Redémarre le service SMTP  
    subprocess.run(['sudo', 'service', 'sendmail', 'restart'])

def main():
    periodic_restart_thread = threading.Thread(target=periodic_restart_smtp_server)
    periodic_restart_thread.start()

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)s
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Redémarrage du serveur SMTP tous les jours (24h)
def periodic_restart_smtp_server():
    while True:
        print("Redémarrage periodique du serveur SMTP...")
        try:
            restart_smtp_service()
            time.sleep(86400)  # 86400 secondes = 24 heures
        except Exception as e:
            print(f"Une erreur est survenue pendant la période de redémarrage, je check les statuts SMTP... {e}")
            check_smtp_logs()
            check_smtp_port()
            check_smtp_auth()
            check_smtp_tls_ssl()
            check_smtp_server_status()
            check_disk_space()
            test_smtp_connection_manuel()





#Si le serveur SMTP ne fonctionne toujours pas après le redémarrage, voici la baterie de tests à faire :


# 1. Vérification des journaux (logs)
def check_smtp_logs():
    smtp_log_path = "/chemin/vers/les/logs/smtp.log"   
    if os.path.exists(smtp_log_path):
        with open(smtp_log_path, 'r') as log_file:
            log_contents = log_file.read()
            if ("erreur") in log_contents.lower():
                print("Erreur trouvé dans les logs SMTP.")
            else:
                print("Pas d'erreur dans les logs SMTP.")
    else:
        print("Le fichier log n'a pas été trouvé.")


# 2. Vérification des ports
def check_smtp_port():
    smtp_port = 587  
    try:
        with socket.create_connection(('smtp.gmail.com', smtp_port), timeout=5) as sock:
            print(f"Le port {smtp_port} est ouvert.")
    except Exception as e:
        print(f"Erreur dans le check du port: {e}")


# 3. Vérification des informations d'identification
def check_smtp_auth():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.login('ousmaneb2307@gmail.com', 'kewf hvaf zvlm hrkf')
        server.quit()
        print("SMTP credentials are valid.")
    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed.")


# 4. Vérification de la configuration TLS/SSL
def check_smtp_tls_ssl():
    smtp_port = 587   
    try:
        context = ssl.create_default_context()
        with socket.create_connection(('smtp.gmail.com', smtp_port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname='smtp.gmail.com') as ssock:
                print("La configuration TLS/SSL est correcte.")
    except Exception as e:
        print(f"Erreur dans le check de la configuration TLS/SSL: {e}")


# 5. Vérification de la disponibilité du serveur SMTP
def check_smtp_server_status():
    try:
        server_status = subprocess.run(['sudo', 'service', 'sendmail', 'status'], capture_output=True)
        if b"active (running)" in server_status.stdout:
            print("Le serveur SMTP fonctionne.")
        else:
            print("Le serveur SMTP est à l'arrêt.")
    except Exception as e:
        print(f"Erreur dans le check des statuts du serveur SMTP: {e}")


# 6. Vérification de l'espace disque
def check_disk_space():
    try:
        disk_space = shutil.disk_usage("/")
        free_space_percentage = (disk_space.free / disk_space.total) * 100
        print(f"L'espace restant du disque: {free_space_percentage:.2f}%")
    except Exception as e:
        print(f"Erreur dans le check du disque: {e}")


# 7. Test de connexion SMTP manuel
def test_smtp_connection_manuel():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('ousmaneb2307@gmail.com', 'kewf hvaf zvlm hrkf')
        server.quit()
        print("La connexion manuelle à SMTP a fonctioné.")
    except Exception as e:
        print(f"La connexion manuel à SMTP a échoué: {e}")


 