import os
import csv
import psycopg2
import re

# Paramètres de connexion à la base de données
hostname = 'localhost'  
database = 'postgres'        
username = 'groupe_iot'   
password = 'guacamole'     
port_id = 5432             

# Chemin du dossier contenant les fichiers CSV
csv_folder_path = "CSV/"

# Connexion à la base de données
conn = psycopg2.connect(
    host=hostname,
    dbname=database,
    user=username,
    password=password,
    port=port_id
)

# Création d'un curseur
cursor = conn.cursor()
print("bonjour")
# Parcourir les fichiers CSV dans le dossier
for filename in os.listdir(csv_folder_path):
    if filename.endswith(".csv"):
        print(f"Traitement du fichier : {filename}")
        csv_file_path = os.path.join(csv_folder_path, filename)
        # Lecture du fichier CSV et insertion des données
        with open(csv_file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Ignorer l'en-tête
            # Utilisation de l'expression régulière pour extraire l'ID de la station du nom de fichier
            match = re.search(r'(\d{4}[A-Z]{2}\d{3})', filename)
            if match:
                station_id = match.group(0)
                print(f"ID de station extrait : {station_id}")
                table_name = f"station_{station_id}"
                cursor.execute("SELECT type FROM stations WHERE id = %s;", (station_id,))
                station_type = cursor.fetchone()[0]
                print(f"Type de station trouvé : {station_type}")
                for row in reader:
                    row = [-1 if value == '' else value for value in row]
                    if station_type == "Helix":
                        cursor.execute("""
                            INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """.format(table_name), row)
                    elif station_type == "Wind":
                        cursor.execute("""
                            INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """.format(table_name), row)
                print(f"Données insérées dans la table {table_name}")
            else:
                print(f"Aucun ID de station trouvé dans le nom de fichier : {filename}")

# Commit des changements
conn.commit()

# Fermeture du curseur et de la connexion
cursor.close()
conn.close()
