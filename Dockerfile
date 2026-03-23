# Dockerfile optimisé
FROM python:3.11-slim

WORKDIR /app

# Installe curl pour le healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code
COPY . .

EXPOSE 8501

# Utilise tini comme entrypoint pour gérer proprement les signaux (SIGTERM)
# Cela compense le fait que os.system() ne forward pas les signaux
ENTRYPOINT ["/usr/bin/tini", "--"]

# Lance run.py qui lancera streamlit en sous-processus
CMD ["python", "run.py"]

# Healthcheck (toujours sur le port 8501)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1