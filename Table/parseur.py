from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import csv
import psycopg2
import os

# Paramètres de connexion à la base de données
hostname = 'localhost'
database = 'postgres'
username = 'groupe_iot'
password = 'guacamole'
port_id = 5432

# Chemin du répertoire de téléchargement
download_dir = "/home/pgip/Documents/Table/Temp"

# Nécessaires API login
email = "master.iot.2023@gmail.com"
mdp = "mkNZ4r8486dDUP3"

# Connexion à la base de données
conn = psycopg2.connect(
    host=hostname,
    dbname=database,
    user=username,
    password=password,
    port=port_id
)

def insert_data_into_database(station_id, file_path):
    try:
        cursor = conn.cursor()
        table_name = f"station_{station_id}"
        cursor.execute("SELECT type FROM stations WHERE id = %s;", (station_id,))
        row = cursor.fetchone()
        station_type = row[0]

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Ignorer l'en-tête

            # Vérifier si la table est vide
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            if row_count > 0:
                # Récupérer la date de la dernière ligne
                cursor.execute(f"SELECT time_utc FROM {table_name} ORDER BY time_utc DESC LIMIT 1;")
                last_row_date = cursor.fetchone()[0]

            for row in reader:
                row = [-1 if value == '' else value for value in row]
                new_row_date = row[0]  # Supposons que la date est la première colonne

                # Comparer avec la date de la dernière ligne
                if row_count == 0 or new_row_date != last_row_date:
                    if station_type == "Helix":
                        cursor.execute("""
                            INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """.format(table_name), row)
                    elif station_type == "Wind":
                        cursor.execute("""
                            INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """.format(table_name), row)
                    else:
                        print("J'appelle la police")
                else:
                    print(f"Ligne dupliquée ignorée pour la table {table_name}.")

        conn.commit()
        print(f"Données insérées avec succès dans la table {table_name}.")
    except psycopg2.Error as e:
        print("Erreur lors de l'insertion des données dans la base de données:", e)
    finally:
        if cursor:
            cursor.close()

def get_stations_from_database():
    stations = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM stations;")
        rows = cursor.fetchall()
        for row in rows:
            stations.append(row[0])
        cursor.close()
    except psycopg2.Error as e:
        print("Erreur lors de la récupération des stations depuis la base de données:", e)
    return stations

def download_data(driver, station_name):
    try:
        bouton_devices = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(.,"Devices") and .//i[@class="icon-screen-tablet"]]')))
        bouton_devices.click()

        bouton_stationsN = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, (f'//h4[contains(text(),"{station_name}")]'))))     
        bouton_stationsN.click()

        bouton_nav = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Data"]')))
        bouton_nav.click()

        bouton_export = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-primary')))
        bouton_export.click()

        bouton_2H = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'dropdown-item')))
        bouton_2H.click()

        bouton_yes = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-success'))) 
        bouton_yes.click()

        maintenant = datetime.now()
        print(f"Téléchargement des données de la station {station_name} réussi le {maintenant.strftime('%d-%m-%Y à %H:%M:%S')}.")
        time.sleep(5)
    except Exception as e:
        print(f"Erreur lors du téléchargement des données pour {station_name}: {e}")

def main():
    # Nombre de tentatives en cas d'échec
    max_attempts = 3

    while True:
        t1 = time.time()
        # Si le téléchargement ne réussit pas, réessayer jusqu'à max_attempts fois
        for attempt in range(max_attempts):
            # Options du navigateur
            options = Options()
            options.add_argument("--headless")

            # Activer les options de téléchargement automatique
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", download_dir)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

            # Créer une instance du navigateur Firefox
            driver = webdriver.Firefox(options=options)

            # URL de la page Web contenant les données
            url = 'https://weather.allmeteo.com/#/'
            driver.get(url)

            try:
                # Connexion
                champ_email = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
                champ_mot_de_passe = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')

                champ_email.send_keys(email)
                champ_mot_de_passe.send_keys(mdp)
                champ_mot_de_passe.send_keys(Keys.RETURN)

                # Téléchargement des données pour chaque station météo
                stations = get_stations_from_database()
                for station in stations:
                    download_data(driver, station)

                break  # Sortir de la boucle de tentative si tout se passe bien

            except Exception as e:
                print(f"Erreur lors du téléchargement : {e}")
                print(f"Reessai, tentative n°{attempt + 1}")
                if attempt >= max_attempts - 1:
                    print(f"Echec après {max_attempts} tentatives. Abandon.")
                    break

            finally:
                # Fermer le navigateur
                driver.quit()

        # Insérer les données des fichiers CSV dans les bases de données correspondantes
        for file_name in os.listdir(download_dir):
            file_path = os.path.join(download_dir, file_name)
            station_id = file_name.split('-')[-1].split('.')[0]  # Extraire l'ID de la station du nom du fichier            insert_data_into_database(station_id, file_path)
            insert_data_into_database(station_id, file_path)

            # Supprimer les fichiers CSV après traitement
            os.remove(file_path)

        t2 = time.time()
        elapsed_time = t2 - t1
        next_execution_time = 600 - elapsed_time
        minutes = int(next_execution_time // 60)
        seconds = int(next_execution_time % 60)
        print(f"Prochaine exécution dans {minutes} min {seconds} sec")
        time.sleep(next_execution_time)

if __name__ == "__main__":
    main()
