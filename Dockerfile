# ── Image de base ─────────────────────────────────────────────────────────────
# Python 3.11 en version "slim" : légère (~120 Mo) mais complète pour nos besoins
FROM python:3.11-slim

# ── Répertoire de travail ─────────────────────────────────────────────────────
# Tous les fichiers copiés ou commandes exécutées seront relatifs à /app
WORKDIR /app

# ── Installation des outils système ───────────────────────────────────────────
# CORRECTION : ajout de 'tini' ici pour l'ENTRYPOINT (sinon erreur au runtime)
# curl : utilisé pour le HEALTHCHECK et les tests d'intégration
# --no-install-recommends : réduit la taille de l'image en évitant les paquets optionnels
# rm -rf /var/lib/apt/lists/* : nettoie le cache apt pour alléger l'image finale
RUN apt-get update && apt-get install -y --no-install-recommends curl tini \
    && rm -rf /var/lib/apt/lists/*

# ── Installation des dépendances Python ───────────────────────────────────────
# Copie d'abord requirements.txt seul pour profiter du cache Docker :
# si le fichier ne change pas, cette étape est skipée au rebuild → gain de temps
COPY requirements.txt .

# Installation des packages Python sans cache pip (réduit la taille de l'image)
RUN pip install --no-cache-dir -r requirements.txt

# ── Copie du code source ──────────────────────────────────────────────────────
# Copie TOUT le projet dans /app (après les deps pour optimiser le cache)
# Ordre important : code en dernier car il change plus souvent que requirements.txt
COPY . .

# ── Exposition du port ────────────────────────────────────────────────────────
# Streamlit écoute par défaut sur le port 8501 → on l'expose pour le mapping Docker
EXPOSE 8501

# ── Point d'entrée avec tini ──────────────────────────────────────────────────
# tini est un "init process" minimal qui :
# - Forward proprement les signaux (SIGTERM, SIGINT) au processus enfant
# - Évite les zombies processes dans les conteneurs long-lived
# - Compense le fait que Python/os.system() ne gère pas nativement les signaux UNIX
# Syntaxe JSON (exec form) obligatoire pour que Docker puisse remplacer CMD
ENTRYPOINT ["/usr/bin/tini", "--"]

# ── Commande par défaut ───────────────────────────────────────────────────────
# Lance run.py qui orchestre le démarrage de Streamlit
# CMD est combiné avec ENTRYPOINT → résultat : /usr/bin/tini -- python run.py
CMD ["python", "run.py"]

# ── Healthcheck ───────────────────────────────────────────────────────────────
# Docker interroge cette endpoint toutes les 30s pour vérifier que l'app est alive
# --interval : fréquence des checks
# --timeout : délai max pour une réponse avant de considérer l'échec
# --start-period : temps de grâce au démarrage (le temps que Streamlit initialise)
# --retries : nombre d'échecs consécutifs avant de marquer le conteneur "unhealthy"
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1