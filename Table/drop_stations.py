import psycopg2
from psycopg2 import sql

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

# Fonction pour supprimer les tables
def drop_tables():
    connection = connect_to_db()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'station_%';")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            drop_query = sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(sql.Identifier(table_name))
            cursor.execute(drop_query)
            print(f"Table {table_name} supprimée avec succès.")
        connection.commit()
    except psycopg2.Error as e:
        print("Erreur lors de la suppression des tables:", e)
    finally:
        if connection is not None:
            connection.close()

# Appel de la fonction pour supprimer les tables
drop_tables()
