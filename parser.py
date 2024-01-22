import csv
import psycopg2

# Paramètres de connexion à la base de données
hostname = 'localhost'  
database = 'postgres'        
username = 'groupe_iot'   
password = 'guacamole'     
port_id = 5432             

# Chemin du fichier CSV
csv_file_path = './infos.csv'

# Connexion à la base de données
conn = psycopg2.connect(
    host=hostname,
    dbname=database,
    user=username,
    password=password,
    port=port_id
)

# Création d'un curseur
cur = conn.cursor()

# Lecture du fichier CSV et insertion des données
with open(csv_file_path, 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)  # Ignorer l'en-tête
    for row in reader:
        # Remplacer les chaînes vides par None
        row = [None if x == '' else x for x in row]
        cur.execute(
            "INSERT INTO info_csv VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            row
        )

# Commit des changements
conn.commit()

# Fermeture du curseur et de la connexion
cur.close()
conn.close()
