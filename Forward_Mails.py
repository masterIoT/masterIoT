import time
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.parser import HeaderParser

# Paramètres IMAP pour lire les e-mails
imap_server = 'imap.gmail.com'
imap_user = 'ousmaneb2307@gmail.com'
imap_password = 'renc pmmu uqvg vskc'

# Paramètres SMTP pour envoyer des e-mails
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'ousmaneb2307@gmail.com'
smtp_password = 'kewf hvaf zvlm hrkf'

# Adresse e-mail de l'administrateur
admin_email = 'master.iot.2023@gmail.com'

# Liste des expéditeurs autorisés
authorized_senders = ['barryo2307@yahoo.com']

def forward_email(from_email, subject, body):
    """Transférer l'e-mail à l'administrateur."""
    msg = MIMEText(body)
    msg['Subject'] = f'FOWARD: {subject}'
    msg['From'] = from_email
    msg['To'] = admin_email

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, admin_email, msg.as_string())
    server.quit()

def check_incoming_emails():
    """Vérifier les e-mails entrants et les transférer à l'administrateur."""
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(imap_user, imap_password)
    mail.select('inbox')

    # Rechercher tous les e-mails non lus
    status, messages = mail.search(None, 'UNSEEN') #recherche les mails non lus
    if status == 'OK':
        for num in messages[0].split():
            # Récupérer l'e-mail complet
            status, data = mail.fetch(num, '(RFC822)')
            if status == 'OK':
                message = data[0][1]
                parser = HeaderParser()
                try:
                    msg = parser.parsestr(message.decode('utf-8'))
                except UnicodeDecodeError:
                    msg = parser.parsestr(message.decode('ISO-8859-1', 'ignore'))
                subject = msg['Subject']
                from_email = msg['From']
                body = msg.get_payload()

                # Transférer l'e-mail directement à l'administrateur
                forward_email(from_email, subject, body)

    mail.close()
    mail.logout()

def main_loop():
    """Boucle principale pour vérifier continuellement les e-mails."""
    while True:
        check_incoming_emails()
        time.sleep(30)  # Attendre 30 secondes avant la prochaine vérification

