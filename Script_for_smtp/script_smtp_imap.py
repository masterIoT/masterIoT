import time
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.parser import Parser
import requests
import zipfile
import re
import os
from email import message_from_bytes
import subprocess
import shutil
import sys

# Paramètres IMAP pour lire les e-mails
IMAP_SERVER = 'imap.gmail.com'
IMAP_USER = 'master.iot.2023@gmail.com'
IMAP_PASSWORD = 'yrae icaj cxmx taiy'

# Paramètres SMTP pour envoyer des réponses
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = IMAP_USER
SMTP_PASSWORD = IMAP_PASSWORD

# Liste des administrateurs - utilisée pour envoyer des alertes et des réponses
ADMIN_RECIPIENTS = ['master.iot.2023@gmail.com']  # Ajoutez ici les emails des administrateurs

# Réponses en fonction des sujets et expéditeurs autorisés
SUBJECT_TO_RESPONSE = {
    "Objet 1": "Réponse pour l'objet 1",
    "Objet 2": "Réponse pour l'objet 2",
}

# Liste des expéditeurs autorisés - ajoutez les adresses email autorisées ici
AUTHORIZED_SENDERS = []  # Exemple: ['example@example.com']]

def send_response_email(subject, response):
    """Envoyez un e-mail de réponse aux administrateurs."""
    msg = MIMEText(response)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = ", ".join(ADMIN_RECIPIENTS)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    print(f"Réponse envoyée pour le sujet '{subject}' à {'; '.join(ADMIN_RECIPIENTS)}.")


def check_incoming_emails():
    """Vérifiez les e-mails entrants et répondez en fonction de l'expéditeur et du sujet."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(IMAP_USER, IMAP_PASSWORD)
    mail.select('inbox')
    status, messages = mail.search(None, 'UNSEEN')
    if status == 'OK':
        for num in messages[0].split():
            typ, data = mail.fetch(num, '(RFC822)')
            if typ == 'OK':
                msg = message_from_bytes(data[0][1])
                subject = msg['Subject']
                from_email = msg['From']
                if any(sender in from_email for sender in AUTHORIZED_SENDERS):
                    response = SUBJECT_TO_RESPONSE.get(subject)
                    if response:
                        send_response_email(subject, response)  # Utiliser ADMIN_RECIPIENTS directement
                    print(f"Email traité: {subject}")
                elif "noreply@baranidesign.com" in msg['From']:
                    payload = msg.get_payload(decode=True).decode('utf-8')
                    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', payload)
                    for url in links:
                        sensor_id_match = re.search(r'export_(\w+)_', url)
                        if sensor_id_match:
                            sensor_id = sensor_id_match.group(1)
                            download_and_extract_zip(url, sensor_id)
                            print(f"Email avec ZIP traité de {msg['From']}")


def download_and_extract_zip(url, sensor_id):
    """Télécharge et extrait un fichier ZIP trouvé dans un e-mail et supprime le dossier après traitement."""
    local_zip_path = f"/tmp/{sensor_id}.zip"
    try:
        response = requests.get(url, stream=True, timeout=10)  # Ajoute un timeout pour éviter les blocages
        response.raise_for_status()  # S'assure que la réponse est valide

        with open(local_zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Vérifie si le fichier ZIP a bien été téléchargé
        if os.path.getsize(local_zip_path) > 0:
            with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
                extract_path = os.path.join("/Users/Barry's/Downloads", sensor_id)
                os.makedirs(extract_path, exist_ok=True)
                zip_ref.extractall(extract_path)
            print(f"Fichier ZIP pour le capteur {sensor_id} téléchargé et extrait.")

            # Traite chaque fichier CSV trouvé dans le dossier extrait
            csv_files = [f for f in os.listdir(extract_path) if f.endswith('.csv')]
            for csv_file in csv_files:
                csv_file_path = os.path.join(extract_path, csv_file)
                subprocess.run(['python3', 'parser.py', csv_file_path], check=True)
            
            # Supprime le dossier après le traitement des fichiers
            shutil.rmtree(extract_path)
            print(f"Dossier {extract_path} supprimé avec succès.")

        else:
            print("Le fichier téléchargé est vide.")
    
    except requests.exceptions.RequestException as e:
        print(f"Échec du téléchargement du fichier ZIP pour {sensor_id}: {e}")
    except zipfile.BadZipFile:
        print("Le fichier téléchargé n'est pas un fichier ZIP valide.")
    finally:
        if os.path.exists(local_zip_path):
            os.remove(local_zip_path)

def mail_alert_bd(station_id):
    """Envoie une alerte email en cas de problème avec la base de données pour une station spécifique."""
    subject = f"Problème lié à la base de données sur la station {station_id}"
    content = (f"Bonjour,\n\n"
               f"Ce message est envoyé automatiquement pour vous informer que la base de données "
               f"associée au capteur {station_id} n'a pas enregistré de nouvelles données ces 10 dernières minutes. "
               "Veuillez vérifier le système pour prévenir toute perte de données importante.\n\n"
               "Cordialement,\n"
               "Équipe technique")
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = IMAP_USER
    msg['To'] = ", ".join(ADMIN_RECIPIENTS)  # Utiliser la liste globale des administrateurs
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    print(f"Alerte envoyée à {', '.join(ADMIN_RECIPIENTS)} pour la station {station_id}.")


def main_loop():
    while True:
        check_incoming_emails()
        time.sleep(60)  # il est préférable d'ajouter un délai pour éviter une utilisation excessive des ressources

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == 'mail_alert_bd':
        station_id = sys.argv[2]  # Récupère le numéro de station à partir des arguments de la ligne de commande
        mail_alert_bd(station_id)  # Appelle mail_alert_bd() avec le numéro de station en argument
    else:
        main_loop()

