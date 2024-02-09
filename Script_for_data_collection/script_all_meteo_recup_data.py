from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import os
import shutil

#Necessaires API login
email = "master.iot.2023@gmail.com"
mdp = "mkNZ4r8486dDUP3"

#Listes des stations 
tab = [
    "SAPHIR MeteoHelix and RainGauge, Phare des Sanguinaires, Ajaccio", #2105SH022
    "SAPHIR MeteoHelix, INSPE Garden, Ajacccio",                        #2008SH045
    "SAPHIR MeteoHelix & RainGauge, Coti-Chiavari, FR",                 #2008SH008
    "SAPHIR MeteoHelix & RainGauge, I Costi, Villanova, FR",            #2008SH047
    "SAPHIR MeteoHelix & RainSensor Corte, FR",                         #2008SH025
    "SAPHIR MeteoHelix & RainSensor Vignola",                           #2110SH043
    "SAPHIR MeteoWind Capu di Muru, Coti-Chiavari, FR",                 #2204SW013
    "SAPHIR MeteoWind Corte Bat.CRIT, FR",                              #2108SW031
    "SAPHIR MeteoWind, I Costi, Villanova, FR",                         #2204SW012
    "SAPHIR MeteoWind, INSPE garden,  Ajaccio",                         #2204SW018
    "SAPHIR MeteoWind, Phare des Sanguinaires, Ajaccio",                #2201SW005
    "SAPHIR MeteoWind Vignola"                                          #2108SW030
]

#variable pour les time.sleep 
m = 3

# Chemin du répertoire contenant les fichiers à trier
repertoire_source = "/home/pgip/Documents/recupData/data"

while True:
    t1 = time.time()
    #si ca marche pas on reessaye deux fois de plus
    for n in range(m):
        #options necessaires a la VM (pas d'affichage)
        options = Options()
        options.add_argument("--headless")

        #Pour le téléchargement 
        # Activer les options de téléchargement automatique
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", repertoire_source)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
        
        # Creer une instance du navigateur Firefox
        driver = webdriver.Firefox(options=options) 

        # URL de la page Web ou se trouve les donnees
        url = 'https://weather.allmeteo.com/#/'
        driver.get(url)
    
        try:
            # On se connecte 
            champ_email = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
            champ_mot_de_passe = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')

            champ_email.send_keys(email)
            champ_mot_de_passe.send_keys(mdp)

            champ_mot_de_passe.send_keys(Keys.RETURN)

            #on boucle pour recuperer les infos de toutes les stations meteos
            for i in range(12):
                #Pour aller chercher les différentes stations météos à chaque boucle
                bouton_devices = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(.,"Devices") and .//i[@class="icon-screen-tablet"]]')))
                bouton_devices.click()
                
                bouton_stationsN = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, (f'//h4[contains(text(),"{tab[i]}")]'))))     
                bouton_stationsN.click()
            
                #On va chercher les datas 
                bouton_nav = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Data"]')))
                bouton_nav.click()

                bouton_export = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-primary')))
                bouton_export.click()

                bouton_2H = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'dropdown-item')))
                bouton_2H.click()

                #ici on lance le telechargement du fichier
                bouton_yes = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-success'))) 
                bouton_yes.click()

                maintenant = datetime.now()
                print(f"Téléchargement réussi le {maintenant.strftime('%d-%m-%Y à %H:%M:%S')}.")

                #pour que le telechargement se lance bien 
                time.sleep(5)

            bouton_deco = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(.,"Logout") and .//i[@class="icon-logout"]]')))
            bouton_deco.click()

            time.sleep(2)
            break
            
        except Exception as e:         
            print(f"Erreur lors du clic sur les boutons : {e}")
            print(f"On reessaye, tentative n°{n+1}")
            if n >= m-1:
                print(f"Échec après {m} tentatives. Abandon.")
                break
                
        finally:
            # Fermer le navigateur
            driver.quit()

    # Parcourir tous les fichiers dans le répertoire source
    for fichier in os.listdir(repertoire_source):
        if fichier.endswith(".csv") and fichier.startswith("allmeteo-export-"):
            # Extraire l'ID du fichier
            id_fichier = fichier.split("allmeteo-export-")[1].split(".")[0]

            # Créer le chemin du répertoire de destination pour cet ID
            dossier_destination = os.path.join(repertoire_source, id_fichier)

            # Vérifier si le répertoire de destination existe, sinon le créer
            if not os.path.exists(dossier_destination):
                os.makedirs(dossier_destination)

            # Construire le chemin de destination complet
            chemin_destination_complet = os.path.join(dossier_destination, fichier)

            # Si le fichier de destination existe déjà, renommer le fichier
            nouveau_nom = fichier
            index = 1
            while os.path.exists(chemin_destination_complet):
                nom_sans_extension, extension = os.path.splitext(fichier)
                nouveau_nom = f"{nom_sans_extension}_{index}{extension}"
                chemin_destination_complet = os.path.join(dossier_destination, nouveau_nom)
                index += 1

            if nouveau_nom != fichier:
                os.rename(os.path.join(repertoire_source, fichier),os.path.join(repertoire_source, nouveau_nom))

            # Déplacer le fichier vers le répertoire de destination
            shutil.move(os.path.join(repertoire_source, nouveau_nom), dossier_destination)

    print("Tri des fichiers terminé.")

    
    t2 = time.time()
    k = t2 - t1
    t3 = 600-k
    minutes = int(t3 // 60)
    secondes = int(t3 % 60)
    print(f"Prochain téléchargement dans {minutes}min{secondes}sec")
    time.sleep(t3)
