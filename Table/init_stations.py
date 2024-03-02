import psycopg2

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

def insert_data():
    connection = connect_to_db()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        # Commande SQL pour insérer les données
        create_query = """CREATE TABLE Stations (
                            id VARCHAR(20) PRIMARY KEY,
                            name VARCHAR(255),
                            type VARCHAR(10) CHECK (Type IN ('Helix', 'Wind')),
                            latitude FLOAT,
                            longitude FLOAT   
                        );
        """                                                               
        insert_query = """
            INSERT INTO Stations (id, name, type, latitude, longitude) VALUES
            ('2105SH022', 'SAPHIR MeteoHelix and RainGauge, Phare des Sanguinaires, Ajaccio', 'Helix', 41.52436, 8.35402),
            ('2008SH045', 'SAPHIR MeteoHelix, INSPE Garden, Ajacccio', 'Helix', 41.54498, 8.43409),
            ('2008SH008', 'SAPHIR MeteoHelix & RainGauge, Coti-Chiavari, FR', 'Helix', 41.44243, 8.39397),
            ('2008SH047', 'SAPHIR MeteoHelix & RainGauge, I Costi, Villanova, FR', 'Helix', 41.58281, 8.39442),
            ('2008SH025', 'SAPHIR MeteoHelix & RainSensor Corte, FR', 'Helix', 42.17561, 9.09122),
            ('2110SH043', 'SAPHIR MeteoHelix & RainSensor Vignola', 'Helix', 41.54447, 8.39102),
            ('2204SW013', 'SAPHIR MeteoWind Capu di Muru, Coti-Chiavari, FR', 'Wind', 41.44257, 8.39418),
            ('2108SW031', 'SAPHIR MeteoWind Corte Bat.CRIT, FR', 'Wind', 42.17556, 9.09105),
            ('2204SW012', 'SAPHIR MeteoWind, I Costi, Villanova, FR', 'Wind', 41.58282, 8.39445),
            ('2204SW018', 'SAPHIR MeteoWind, INSPE garden,  Ajaccio', 'Wind', 41.54496, 8.43413),
            ('2201SW005', 'SAPHIR MeteoWind, Phare des Sanguinaires, Ajaccio', 'Wind', 41.52437, 8.35405),
            ('2108SW030', 'SAPHIR MeteoWind Vignola', 'Wind', 41.54464, 8.3913);
        """
        cursor.execute(create_query)
        cursor.execute(insert_query)
        connection.commit()
        print("Table Stations créé avec succès.")
    except psycopg2.Error as e:
        print("Erreur lors de la création de la table:", e)
    finally:
        if connection is not None:
            connection.close()

# Appel de la fonction pour insérer les données
insert_data()
