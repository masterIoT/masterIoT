from flask import Flask, Response
import docker
import logging
from docker.errors import DockerException
from flask import jsonify

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Initialisation du client Docker avec gestion des exceptions
try:
    client = docker.from_env(timeout=10)
except DockerException as e:
    logging.error(f"Erreur d'initialisation du client Docker : {e}")
    client = None

@app.route('/metrics')
def metrics():
    docker_status = 0
    running_containers = 0
    total_containers = 0
    container_metrics = ""

    # Vérification du démon Docker
    if client:
        try:
            client.ping()
            docker_status = 1  # Docker est actif
        except DockerException as e:
            logging.error(f"Erreur lors de la vérification du démon Docker : {e}")
    else:
        logging.error("Client Docker non initialisé.")

    # Collecte de l'état des conteneurs
    if docker_status == 1:
        try:
            containers = client.containers.list(all=True)
            running_containers = sum(1 for c in containers if c.status == "running")
            total_containers = len(containers)

            # Noms des conteneurs à suivre
            containers_to_monitor = [
                "mongodbformeteo-container",
                "wordpress-wordpress-1",
                "wordpress-db-1",
                "prometheus",
                "node-exporter"
            ]

            for container in containers:
                if container.name in containers_to_monitor:
                    status = 1 if container.status == "running" else 0
                    container_metrics += f'docker_container_status{{name="{container.name}"}} {status}\n'
        except DockerException as e:
            logging.error(f"Erreur lors de la récupération des conteneurs : {e}")
    else:
        logging.warning("Docker est inactif, impossible de récupérer les informations des conteneurs.")

    # Format Prometheus des métriques
    metrics_data = f"""
# HELP docker_status Docker daemon status (1 = active, 0 = inactive)
# TYPE docker_status gauge
docker_status {docker_status}

# HELP docker_running_containers Number of running containers
# TYPE docker_running_containers gauge
docker_running_containers {running_containers}

# HELP docker_total_containers Total number of containers
# TYPE docker_total_containers gauge
docker_total_containers {total_containers}

# HELP docker_container_status Status of specific containers (1 = running, 0 = not running)
# TYPE docker_container_status gauge
{container_metrics}
"""
    return Response(metrics_data, mimetype='text/plain')

# Gestion globale des erreurs pour Flask
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Erreur inattendue : {e}")
    response = jsonify({"error": "Une erreur inattendue est survenue."})
    response.status_code = 500
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9101)
