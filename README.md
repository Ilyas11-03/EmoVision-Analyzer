# EmoVision-Analyzer 🎭📹

## 📦 Prérequis

- **Python 3.11**  
Téléchargez les sources depuis le site officiel Python : https://www.python.org/downloads/source/

Un système d'analyse vidéo par IA pour détecter les émotions et le stress à partir de flux vidéo en temps réel ou de fichiers pré-enregistrés.

## 📚 Bibliothèques Clés

Ce projet utilise ces principales dépendances Python :

### Analyse Vidéo/Image
| Bibliothèque | Version | Usage |
|--------------|---------|-------|
| `opencv-python` | 4.11.0 | Traitement vidéo et détection faciale |
| `imageio` | 2.37.0 | Lecture/écriture des médias |
| `imageio-ffmpeg` | 0.6.0 | Support des codecs vidéo |
| `fer` | 22.5.1 | Détection d'émotions faciales |
| `deepface` | 0.0.93 | Analyse approfondie des expressions |

### Traitement Audio
| `librosa` | 0.11.0 | Extraction des caractéristiques audio |
| `soundfile` | 0.13.1 | Lecture des fichiers audio |

### Data Science
| `numpy` | 1.26.4 | Calculs scientifiques |
| `pandas` | 2.2.3 | Manipulation des données |
| `scikit-learn` | 1.6.1 | Pré-traitement et ML |

### Visualisation
| `matplotlib` | 3.10.3 | Graphiques statiques |
| `altair` | 5.5.0 | Visualisations interactives |

### Interface
| `streamlit` | 1.45.1 | Dashboard web interactif |

### Utilitaires
| `fpdf` | 1.7.2 | Génération de rapports PDF |
| `scipy` | 1.15.3 | Traitement du signal |

> ℹ️ Toutes les dépendances sont listées dans [`requirements.txt`](requirements.txt)

## Fonctionnalités clés

- 🎭 Détection de 7 émotions de base (colère, dégoût, peur, joie, tristesse, surprise, neutre)
- 📊 Analyse du niveau de stress via micro-expressions
- 📄 Génération de rapports PDF/JSON
- 📊 Visualisation des Résultats

Le système génère automatiquement des graphiques d'analyse émotionnelle :

### Graphique Temporel des Émotions
![Exemple de graphique émotionnel]
![image](https://github.com/user-attachments/assets/105539d4-d127-4173-8fe6-e316d2ca9973)

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/Ilyas11-03/EmoVision-Analyzer.git

Installez les dépendances :


bash
pip install -r requirements.txt

2.Executer le script

bash
python run.py
