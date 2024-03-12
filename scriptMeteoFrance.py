import requests
import csv
import time
from datetime import datetime, timedelta

def get_yesterday_date():
    # Obtenez la date d'aujourd'hui
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Soustraire un jour pour obtenir la date d'hier
    yesterday = today - timedelta(days=1)

    return yesterday.strftime('%Y-%m-%dT') + '00:00:00Z'

def get_yesterday_end_date():
    # Obtenez la date d'aujourd'hui
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Soustraire un jour pour obtenir la date d'hier
    yesterday = today - timedelta(days=1)

    return yesterday.strftime('%Y-%m-%dT') + '23:59:59Z'

def get_filename():
    base_filename = "donnees_climatiques"
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_date = yesterday.strftime('%d-%m-%Y')
    extension = ".csv"
    new_filename = f"{base_filename}_{yesterday_date}{extension}"

    return new_filename

def download_data_for_station(api_key):
    station_id = '20004002'
    date_deb_periode = get_yesterday_date() # Début de la journée d'hier
    date_fin_periode = get_yesterday_end_date() # Fin de la journée d'hier

    url = f"https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/horaire"
    params = {
        "id-station": station_id,
        "date-deb-periode": date_deb_periode,
        "date-fin-periode": date_fin_periode
    }
    headers = {
        "Accept": "application/json",
        "apikey": f"{api_key}" 
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Lève une exception en cas d'erreur HTTP
        data = response.json()
        commande_numero = data.get('elaboreProduitAvecDemandeResponse', {}).get('return')
        if commande_numero:
            print("Numéro de commande pour la station Ajaccio :", commande_numero)
            return commande_numero
        else:
            print("Aucun numéro de commande trouvé dans la réponse.")
            return None
    except requests.exceptions.RequestException as e:
        print("Erreur lors de la requête : ", e)
        if hasattr(response, 'status_code') and response.status_code == 502:
            print("Erreur 502 : Tentative de reconnexion dans 5 secondes...")
            time.sleep(5)
            download_data_for_station(api_key)
        return None

def download_data_file(commande_id, api_key):
    url = "https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier"
    params = {
        "id-cmde": commande_id
    }
    headers = {
        "Accept": "text/plain",
        "apikey": f"{api_key}" 
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Lève une exception en cas d'erreur HTTP
        
        #pour avoir un nom personnalisé avec la date du téléchargement
        filename = get_filename() 
        
        # Écrire le contenu de la réponse dans un fichier CSV
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f, delimiter=';')
            lines = response.text.strip().split('\n')
            for line in lines:
                writer.writerow(line.split(';'))
        
        print("Les données climatiques ont été téléchargées avec succès.")
    except requests.exceptions.RequestException as e:
        print("Erreur lors de la requête : ", e)
        if hasattr(response, 'status_code') and response.status_code == 502:
            print("Erreur 502 : Tentative de reconnexion dans 5 secondes...")
            time.sleep(5)
            download_data_file(commande_id, api_key)

if __name__ == "__main__":
    #Valable 5ans à partir du 08/03/2024
    api_key = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJIdWdvQXNAY2FyYm9uLnN1cGVyIiwiYXBwbGljYXRpb24iOnsib3duZXIiOiJIdWdvQXMiLCJ0aWVyUXVvdGFUeXBlIjpudWxsLCJ0aWVyIjoiVW5saW1pdGVkIiwibmFtZSI6IkRlZmF1bHRBcHBsaWNhdGlvbiIsImlkIjoxMDM3NCwidXVpZCI6IjVhZDdiNTg0LWQ0ZjItNDgyZS1hMDQ1LTU0ZWFjZGM3NjcxOSJ9LCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnI6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsiNTBQZXJNaW4iOnsidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsImdyYXBoUUxNYXhDb21wbGV4aXR5IjowLCJncmFwaFFMTWF4RGVwdGgiOjAsInN0b3BPblF1b3RhUmVhY2giOnRydWUsInNwaWtlQXJyZXN0TGltaXQiOjAsInNwaWtlQXJyZXN0VW5pdCI6InNlYyJ9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzQ2xpbWF0b2xvZ2llIiwiY29udGV4dCI6IlwvcHVibGljXC9EUENsaW1cL3YxIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoidjEiLCJzdWJzY3JpcHRpb25UaWVyIjoiNTBQZXJNaW4ifV0sImV4cCI6MTg2NzU5MDU1NiwidG9rZW5fdHlwZSI6ImFwaUtleSIsImlhdCI6MTcwOTkxMDU1NiwianRpIjoiNjMzNjM4MzUtZDhiNi00ZjUxLTg0MDItYzYyNTQ2MTY0ZGM2In0=.RL4_e6aLAwg-gEO8sUCeNuLPjtGfADhK6Jyx6MZNhVC0lH7zyy5xjRQaPK-cZdH6VX8vHwdSYF3tm7vFsNLXEdc9akcd51iYATCGVTR1hitCzuw7pmdFB_u4THWMGCdIAE0yLGECmfo_FFf7fC0gvNLMJZoYoVobWsRdN8fkYr-_tpqYhI8QSf-NTFh3psEKyGczUEvBM003ylAS3VKZQ0mb9Tg1uh3DpCdrT5_SocBqaPa0Hb57vGv0qrr3FYTvoSxmcNkJf_yWxZSxFNGTWOlbIgun3wHSBDKxs8aYzmc8RdU-4GAgKs77OqHrxwTsSIeo84SuDfi2weJY3qou4A=="

    while True:
        now = datetime.utcnow()
        if now.hour == 6 and now.minute == 30:
            # Récupérer la date d'hier
            yesterday = datetime.utcnow() - timedelta(days=1)
            yesterday_date = yesterday.strftime('%d/%m/%Y')
            print(f"Lancement du téléchargement pour le {yesterday_date} ...")
            
            # Télécharger les données pour la station d'Ajaccio
            commande_id = download_data_for_station(api_key)
            if commande_id:
                download_data_file(commande_id, api_key)
                print("Prochain téléchargement demain !")
                time.sleep(60)
        else:
            # Attendre une minute avant de vérifier à nouveau l'heure
            time.sleep(60)


