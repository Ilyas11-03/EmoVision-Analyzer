# Système d'Analyse Comportementale Multimodale 🎭📹

Un système d'analyse vidéo par intelligence artificielle combinant 
la détection des émotions faciales, l'analyse du stress vocal, 
la transcription automatique et l'évaluation de la cohérence 
des réponses dans un pipeline multimodal unifié.

---

##  Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Structure du projet](#structure-du-projet)
- [Rôle de chaque fichier](#rôle-de-chaque-fichier)
- [Bibliothèques utilisées](#bibliothèques-utilisées)
- [Fonctionnalités](#fonctionnalités)
- [Lancement](#lancement)
- [Rapports générés](#rapports-générés)
- [Limites](#limites)

---

##  Prérequis

- **Python 3.11** — [Télécharger](https://www.python.org/downloads/)
- **ffmpeg** — Requis pour l'extraction audio
  - Windows : [Télécharger ffmpeg](https://ffmpeg.org/download.html)
  - Ajouter ffmpeg au PATH système
- **Git** — [Télécharger](https://git-scm.com/)

---

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/Ilyas11-03/EmoVision-Analyzer.git
cd EmoVision-Analyzer
```

### 2. Créer un environnement virtuel
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application
```bash
python run.py
```

L'application sera accessible sur `http://localhost:8501`

---

## Structure du projet
```
EmoVision-Analyzer/
│
├── app/                          ← Modules backend (96.7% Python)
│   ├── __init__.py               ← Package initialization
│   ├── analyzer.py               ← Pipeline principal
│   ├── video_processing.py       ← Extraction des frames
│   ├── emotion_detector.py       ← Détection des émotions faciales
│   ├── emotion_utils.py          ← Statistiques émotionnelles
│   ├── behavior_summary.py       ← Résumé comportemental
│   ├── stress_analysis.py        ← Analyse du stress vocal
│   ├── speech_to_text.py         ← Transcription automatique
│   ├── qa_analyzer.py            ← Analyse Q/R sémantique
│   ├── truth_detector.py         ← Indicateur de sincérité
│   └── report_generator.py       ← Génération des rapports
│
├── interface/
│   ├── __init__.py               ← Package initialization
│   └── web_app.py                ← Interface Streamlit
│
├── tests/                        ← Tests unitaires
│
├── .github/                      ← Configuration GitHub
├── .gitignore                    ← Fichiers ignorés
├── .isort.cfg                    ← Configuration isort
├── setup.cfg                     ← Configuration setuptools
├── pytest.ini                    ← Configuration pytest
│
├── run.py                        ← Point d'entrée Streamlit
├── api.py                        ← API REST FastAPI alternative
├── requirements.txt              ← Dépendances Python
├── Dockerfile                    ← Configuration Docker (3.3%)
├── docker-compose.yaml           ← Orchestration multi-conteneur
└── README.md                     ← Cette documentation
```

### Répertoires d'exécution (générés)
```
├── temp_frames/                  ← Frames temporaires (cache)
├── uploads/                      ← Vidéos uploadées
├── data/                         ← Données d'entraînement/données brutes
└── models/                       ← Modèles pré-entraînés (DeepFace, Whisper)
```

---

## Rôle de chaque fichier

### Backend — `app/`

| Fichier | Rôle |
|---------|------|
| `analyzer.py` | Chef d'orchestre — appelle tous les modules dans le bon ordre et retourne un dictionnaire complet des résultats |
| `video_processing.py` | Découpe la vidéo en frames à intervalles réguliers et retourne les métadonnées vidéo |
| `emotion_detector.py` | Analyse chaque frame via DeepFace — détecte les émotions primaires et calcule les émotions dérivées par heuristique |
| `emotion_utils.py` | Agrège les résultats individuels en statistiques globales — top frames, répartition catégorielle, score de dissonance |
| `behavior_summary.py` | Génère un résumé textuel en français du comportement émotionnel global |
| `stress_analysis.py` | Extrait l'audio via ffmpeg et calcule les features acoustiques (RMS, pitch, ZCR, MFCCs, stress score) |
| `speech_to_text.py` | Transcrit automatiquement l'audio en texte via Whisper d'OpenAI avec support multilingue |
| `qa_analyzer.py` | Évalue la cohérence sémantique entre une question et une réponse via similarité cosinus |
| `truth_detector.py` | Calcule un indicateur de sincérité heuristique combinant stress vocal et émotion faciale |
| `report_generator.py` | Exporte tous les résultats en PDF (10 sections), CSV et JSON |

### Interface — `interface/`

| Fichier | Rôle |
|---------|------|
| `web_app.py` | Interface Streamlit — upload vidéo, visualisations interactives, téléchargement des rapports |

### API Alternative

| Fichier | Rôle |
|---------|------|
| `api.py` | API REST FastAPI — endpoints pour l'analyse sans interface web |

### Racine

| Fichier | Rôle |
|---------|------|
| `run.py` | Point d'entrée — lance l'application Streamlit |
| `Dockerfile` | Configuration Docker (3.3%) — conteneurisation de l'application |
| `docker-compose.yaml` | Orchestration multi-conteneur pour déploiement simplifié |
| `requirements.txt` | Liste des dépendances Python |

---

## Bibliothèques utilisées

### Interface
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `streamlit` | 1.45.1 | Dashboard web interactif |
| `altair` | 5.5.0 | Visualisations interactives |

### Vision par ordinateur
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `opencv-python` | 4.11.0.86 | Extraction des frames vidéo |
| `deepface` | 0.0.93 | Détection des émotions faciales |

### Traitement audio
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `librosa` | 0.11.0 | Extraction features acoustiques |
| `soundfile` | 0.13.1 | Chargement audio robuste (Windows) |

### Deep Learning & NLP
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `torch` | 2.7.1 | Backend Whisper + SentenceTransformers |
| `transformers` | 4.41.1 | Dépendance SentenceTransformers |
| `sentence-transformers` | 2.6.1 | Embeddings sémantiques Q/R |

### Transcription
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `openai-whisper` | latest | Transcription automatique multilingue |

### Data Science
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `numpy` | 1.26.4 | Calculs numériques |
| `pandas` | 2.2.3 | Manipulation tabulaire |
| `scipy` | 1.15.3 | Dépendance SentenceTransformers |
| `scikit-learn` | 1.6.1 | Dépendance SentenceTransformers |

### Rapport
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `fpdf` | 1.7.2 | Génération rapports PDF |

### Système (non-Python)
| Outil | Usage |
|-------|-------|
| `ffmpeg` | Extraction audio depuis vidéo |
| `ffprobe` | Détection piste audio |

---

## Fonctionnalités

### Analyse faciale
- Détection de **7 émotions primaires** via DeepFace
  (joie, tristesse, colère, peur, dégoût, surprise, neutralité)
- Calcul de **24 émotions dérivées** par règles heuristiques
  (nerveux, excité, anxieux, fier, fatigué, embarrassé...)
- Score de **dissonance émotionnelle** sur fenêtre glissante
- Résumé comportemental automatique en français

### Analyse vocale
- Extraction des features acoustiques : RMS, Pitch, ZCR, MFCCs
- **Score de stress normalisé** [0.0 – 1.0]
- Analyse par segment temporel configurable

### Transcription & Q/R
- Transcription automatique multilingue via **Whisper**
- Analyse de pertinence sémantique **Question / Réponse**
- Verdict gradué à 4 niveaux (très pertinente → hors sujet)

### Indicateur de sincérité
- Combinaison stress vocal + émotion faciale
- Disclaimer académique systématique sur les limites

### Rapports
- Export **PDF** (10 sections avec images des frames)
- Export **CSV** (détail frame par frame)
- Export **JSON** (données brutes exploitables)

---

## Lancement

### Mode Streamlit
```bash
python run.py
```
Accessible sur `http://localhost:8501`

### Mode API REST
```bash
python api.py
```
Endpoints disponibles sur `http://localhost:8000`

### Docker
```bash
# Build
docker build -t emovision-analyzer .

# Lancer
docker run -p 8501:8501 emovision-analyzer

# Avec docker-compose
docker-compose up
```

---

## Limites

- Les émotions dérivées sont des **approximations heuristiques**
  non validées sur un corpus annoté
- L'indicateur de sincérité ne constitue **pas une preuve de mensonge**
  et ne doit pas être utilisé à des fins légales
- Les performances dépendent de la **qualité vidéo** et de la
  présence d'une piste audio exploitable
- Le système est un **outil d'aide à l'analyse** destiné à un
  professionnel qualifié

---

## Architecture Technique

### Pipeline de traitement

```
Vidéo Input
    ↓
[Video Processing] → Frame extraction + metadata
    ↓
    ├─→ [Emotion Detector] → Frame emotions (7 primaires)
    │       ↓
    │   [Emotion Utils] → Statistics agrégées
    │       ↓
    │   [Behavior Summary] → Résumé textuel FR
    │
    ├─→ [Audio Extraction] → ffmpeg → WAV
    │       ↓
    │   [Stress Analysis] → Acoustic features
    │       ↓
    │   [Speech to Text] → Whisper transcription
    │       ↓
    │   [Truth Detector] → Sincérité score
    │
    └─→ [QA Analyzer] → Cohérence sémantique
    
    ↓
[Report Generator]
    ├─→ PDF (10 sections + visualisations)
    ├─→ CSV (détail par frame)
    └─→ JSON (données brutes)
```

### Composition du répertoire

- **Python**: 96.7% (core logic)
- **Dockerfile**: 3.3% (containerization)

---

## Auteur

Projet réalisé dans le cadre d'un **Projet de Fin d'Études (PFE)**

---

>  Ce système est un outil d'aide à l'analyse comportementale.
> Toute interprétation des résultats doit être réalisée par un
> professionnel qualifié dans le respect du cadre légal applicable.
