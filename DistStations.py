import math

# Définition des données des stations météo avec les noms
stations = [
    {"key": "2105SH022", "nom": "SAPHIR MeteoHelix and RainGauge, Phare des Sanguinaires, Ajaccio", "latitude": 41.878778, "longitude": 8.594500},
    {"key": "2008SH045", "nom": "SAPHIR MeteoHelix, INSPE Garden, Ajacccio", "latitude": 41.913833, "longitude": 8.728028},
    {"key": "2008SH008", "nom": "SAPHIR MeteoHelix & RainGauge, Coti-Chiavari, FR", "latitude": 41.740083, "longitude": 8.661028},
    {"key": "2008SH047", "nom": "SAPHIR MeteoHelix & RainGauge, I Costi, Villanova, FR", "latitude": 41.974472, "longitude": 8.662278},
    {"key": "2008SH025", "nom": "SAPHIR MeteoHelix & RainSensor Corte, FR", "latitude": 42.298917, "longitude": 9.153389},
    {"key": "2110SH043", "nom": "SAPHIR MeteoHelix & RainSensor Vignola", "latitude": 41.912417, "longitude": 8.652833},
    {"key": "2204SW013", "nom": "SAPHIR MeteoWind Capu di Muru, Coti-Chiavari, FR", "latitude": 41.740472, "longitude": 8.661611},
    {"key": "2108SW031", "nom": "SAPHIR MeteoWind Corte Bat.CRIT, FR", "latitude": 42.298778, "longitude": 9.152917},
    {"key": "2204SW012", "nom": "SAPHIR MeteoWind, I Costi, Villanova, FR", "latitude": 41.974500, "longitude": 8.662361},
    {"key": "2204SW018", "nom": "SAPHIR MeteoWind, INSPE garden,  Ajaccio", "latitude": 41.913778, "longitude": 8.728694},
    {"key": "2201SW005", "nom": "SAPHIR MeteoWind, Phare des Sanguinaires, Ajaccio", "latitude": 41.878806, "longitude": 8.594583},
    {"key": "2108SW030", "nom": "SAPHIR MeteoWind Vignola", "latitude": 41.912889, "longitude": 8.653611}
]


def distance_gps(lat1, lon1, lat2, lon2):
    """
    Calcule la distance en kilomètres entre deux points GPS
    (latitude/longitude) en utilisant la formule de Haversine
    """
    # Convertir les coordonnées de degrés à radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Rayon moyen de la Terre en kilomètres
    rayon_terre = 6371.0

    # Différence de latitude et de longitude
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1

    # Calcul de la distance en utilisant la formule de Haversine
    a = math.sin(d_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = rayon_terre * c

    return distance

def station_meteo_proche(latitude, longitude):
    # Initialiser la distance minimale et la station météo la plus proche
    min_distance = float('inf')
    station_proche = None

    # Parcourir toutes les stations météo pour trouver la plus proche
    for station in stations:
        dist = distance_gps(latitude, longitude, station['latitude'], station['longitude'])
        if dist < min_distance:
            min_distance = dist
            station_proche = station

    return station_proche['key'], station_proche['nom'], min_distance

if __name__ == "__main__":
    # Demander les coordonnées à l'utilisateur
    latitude_point = float(input("Entrez la latitude du point GPS : "))
    longitude_point = float(input("Entrez la longitude du point GPS : "))

    # Trouver la station météo la plus proche
    key_station_proche, nom_station_proche, min_distance = station_meteo_proche(latitude_point, longitude_point)

    # Imprimer le nom, la clé et la distance de la station météo la plus proche
    print(f"La station météo la plus proche est : {nom_station_proche} ({key_station_proche})")
    print(f"Distance à la station météo la plus proche : {min_distance:.2f} kilomètres")
