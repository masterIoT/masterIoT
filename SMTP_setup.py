import time
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.parser import HeaderParser

# ParamÃ¨tres IMAP pour lire les e-mails
imap_server = 'imap.gmail.com'
imap_user = 'ousmaneb2307@gmail.com'
imap_password = 'renc pmmu uqvg vskc'

# ParamÃ¨tres SMTP pour envoyer des rÃ©ponses
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'ousmaneb2307@gmail.com'
smtp_password = 'kewf hvaf zvlm hrkf'
subject_to_response = {
    "Objet 1": "RÃ©ponse pour l'objet 1",
    "Objet 2": "RÃ©ponse pour l'objet 2",
    # Ajoutez d'autres sujets et rÃ©ponses au besoin
}
def send_response_email(response, recipient):
    """Envoyez un e-mail de rÃ©ponse."""
    msg = MIMEText(response)
    msg['Subject'] = 'RÃ©ponse Automatique'
    msg['From'] = smtp_user
    msg['To'] = recipient

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, recipient, msg.as_string())
    server.quit()
authorized_senders = ['barryo2307@yahoo.com']

def check_incoming_emails():
    """Vérifiez les e-mails entrants et répondez en fonction de l'expéditeur et du sujet."""
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(imap_user, imap_password)
    mail.select('inbox')

    status, messages = mail.search(None, 'UNSEEN')
    if status == 'OK':
        for num in messages[0].split():
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

                if any(sender in from_email for sender in authorized_senders):
                    response = subject_to_response.get(subject)
                    if response:
                        send_response_email(response, 'master.iot.2023@gmail.com')

    mail.close()
    mail.logout()

def main_loop():
    """Boucle principale pour vÃ©rifier continuellement les e-mails."""
    while True:
        check_incoming_emails()
        time.sleep(60)  # Attendre 60 secondes avant la prochaine vÃ©rification
# ExÃ©cutez la boucle principale
main_loop()
# ExÃ©cutez la boucle principale
main_loop()
