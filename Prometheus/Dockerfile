FROM python:3.9

# Installer le client Docker SDK pour Python
RUN pip install Flask docker

# Copier le script
COPY docker_metrics_exporter.py /docker_metrics_exporter.py

# Exposer le port pour le serveur Flask
EXPOSE 9101

# Commande pour démarrer le script
