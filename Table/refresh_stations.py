import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import time

hostname = 'localhost'  
database = 'postgres'        
username = 'groupe_iot'   
password = 'guacamole'     
port_id = 5432  

# Fonction pour se connecter à la base de données
def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port_id
        )
        return connection
    except psycopg2.Error as e:
        print("Erreur lors de la connexion à la base de données:", e)
        return None

# Fonction pour vérifier si une table existe
def table_exists(cursor, table_name):
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);", (table_name,))
    return cursor.fetchone()[0]

# Fonction pour créer une nouvelle table Wind
def create_wind_table(cursor, station_id):
    table_name = f"station_{station_id}"
    create_table_query = """
        CREATE TABLE IF NOT EXISTS {} (
            time_utc TIMESTAMP,
            battery_v NUMERIC,
            wdir_avg10 NUMERIC,
            wdir_gust10 NUMERIC,
            wdir_max10 NUMERIC,
            wdir_min10 NUMERIC,
            wind_avg10_m_per_s NUMERIC,
            wind_max10_m_per_s NUMERIC,
            wind_min10_m_per_s NUMERIC,
            wind_stdev10_m_per_s NUMERIC,
            wdir_stdev10 NUMERIC
        );
    """.format(table_name)
    cursor.execute(create_table_query)
    print(f"Table {table_name} créée avec succès.")

# Fonction pour créer une nouvelle table Helix
def create_helix_table(cursor, station_id):
    table_name = f"station_{station_id}"
    create_table_query = """
        CREATE TABLE IF NOT EXISTS {} (
            time_utc TIMESTAMP,
            battery_v NUMERIC,
            dewPoint_c NUMERIC,
            humidity_percent NUMERIC,
            irradiation_w_per_m2 NUMERIC,
            irradiation_max_w_per_m2 NUMERIC,
            pressure_raw_hpa NUMERIC,
            rain_mm NUMERIC,
            temperature_c NUMERIC,
            temperature_max_c NUMERIC,
            temperature_min_c NUMERIC,
            rainfall_rate_max_mm_per_h NUMERIC,
            pressure_hpa NUMERIC,
            temperature_wetbulb_stull2011_c NUMERIC
        );
    """.format(table_name)
    cursor.execute(create_table_query)
    print(f"Table {table_name} créée avec succès.")

# Fonction principale pour vérifier et créer les tables
def check_and_create_tables():
    # Se connecter à la base de données
    connection = connect_to_db()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        
        # Sélectionner toutes les stations de la table "Stations"
        cursor.execute("SELECT id, type FROM Stations;")
        stations = cursor.fetchall()

        for station in stations:
            station_id = station[0]
            station_type = station[1]
            if station_type == "Helix":
                table_name = f"{station_id}"
                if not table_exists(cursor, table_name):
                    create_helix_table(cursor, station_id)
                else:
                    print(f"La table {table_name} existe déjà.")
            elif station_type == "Wind":
                table_name = f"{station_id}"
                if not table_exists(cursor, table_name):
                    create_wind_table(cursor, station_id)
                else:
                    print(f"La table {table_name} existe déjà.")
                    
        connection.commit()
        cursor.close()
    except psycopg2.Error as e:
        print("Erreur lors de l'exécution des requêtes SQL:", e)
    finally:
        if connection is not None:
            connection.close()

# Fonction principale pour exécuter le script toutes les heures
def main():
    while True:
        check_and_create_tables()
        # Attendre une heure avant de vérifier à nouveau
        next_hour = datetime.now() + timedelta(hours=1)
        wait_time = next_hour.replace(minute=0, second=0, microsecond=0) - datetime.now()
        print(f"Attente de {wait_time} avant la prochaine exécution...")
        time.sleep(wait_time.total_seconds())

if __name__ == "__main__":
    main()
