# Utilise l'image officielle Python 3.11
FROM python:3.11-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie les fichiers de dépendances (si présents)
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code source dans le conteneur
COPY . .

# Commande par défaut (à adapter selon votre projet)
CMD ["python", "run.py"]
