import psycopg2
import csv
import sys

def export_data_to_csv(table_name, output_file):
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="postgres",
        user="groupe_iot",
        password="guacamole"
    )
    cursor = connection.cursor()
    
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    
    # Récupérer les en-têtes
    column_headers = [desc[0] for desc in cursor.description]

    rows = cursor.fetchall()
    
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        # Écrire les en-têtes en premier
        csvwriter.writerow(column_headers)
        # Écrire les lignes de données
        for row in rows:
            csvwriter.writerow(row)
    
    connection.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py table_name")
        sys.exit(1)
    
    table_name = sys.argv[1]
    output_file = f"{table_name}_export.csv"
    
    export_data_to_csv(table_name, output_file)
    print(f"Data exported to {output_file}")

