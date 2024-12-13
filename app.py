from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json
from sklearn.preprocessing import MinMaxScaler

# Charger le modèle TensorFlow
model = tf.keras.models.load_model("forecast_model.h5")

# Configurer Kafka
KAFKA_BROKER = "kafka:9092"
OUTPUT_TOPIC = "TPC_IA"
producer = None
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
except Exception as e:
    print(f"Kafka non disponible : {e}")

# Initialiser Flask
app = Flask(__name__)

# Charger le scaler basé sur les plages des données d'entraînement
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(np.array([-20, 50]).reshape(-1, 1))  # Ajusté pour les températures de -20°C à 50°C

def generate_hourly_timestamps(start, end):
    """
    Génère une liste de timestamps horaires entre deux dates.
    """
    start_time = datetime.fromisoformat(start)
    end_time = datetime.fromisoformat(end)
    timestamps = []
    current = start_time
    while current <= end_time:
        timestamps.append(current.isoformat())
        current += timedelta(hours=1)
    return timestamps

def prepare_input_data(timestamps, look_back=24):
    """
    Prépare les données d'entrée pour le modèle à partir des timestamps.
    """
    if len(timestamps) < look_back:
        raise ValueError("Le nombre de timestamps doit être au moins égal à look_back.")

    features = []
    for i in range(len(timestamps) - look_back):
        sequence = []
        for j in range(i, i + look_back):
            dt = datetime.fromisoformat(timestamps[j])
            sequence.append([
                dt.hour / 24.0,  # Normalisation de l'heure
                dt.day / 31.0,   # Normalisation du jour
                dt.month / 12.0  # Normalisation du mois
            ])
        features.append(sequence)
    return np.array(features)

def predict_temperatures(start_date, end_date):
    """
    Prédit les températures horaires entre deux dates en utilisant le modèle chargé.
    """
    # Générer les timestamps horaires
    timestamps = generate_hourly_timestamps(start_date, end_date)

    # Préparer les données d'entrée
    input_data = prepare_input_data(timestamps)

    # Normaliser les données
    input_data_scaled = scaler.transform(input_data.reshape(-1, 3)).reshape(input_data.shape)

    # Prédire les températures
    predictions = model.predict(input_data_scaled)

    # Dénormaliser les prédictions
    predictions_denormalized = scaler.inverse_transform(predictions)

    # Structurer les résultats
    results = [
        {"timestamp": timestamps[i + 24], "temperature": round(predictions_denormalized[i][0], 2)}
        for i in range(len(predictions))
    ]

    return results

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Récupérer les données de la requête POST
        data = request.get_json()
        start_date = data["start_date"]  # Format attendu : "2024-12-10T00:00:00"
        end_date = data["end_date"]

        # Prédire les températures
        predictions = predict_temperatures(start_date, end_date)

        # Publier les prédictions sur Kafka
        if producer:
            producer.send(OUTPUT_TOPIC, value={"predictions": predictions})

        return jsonify({"status": "success", "predictions": predictions})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
