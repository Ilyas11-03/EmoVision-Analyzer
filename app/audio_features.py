import librosa  # Importation de la bibliothèque librosa pour le traitement audio
import numpy as np  # Importation de numpy pour les opérations numériques

def extract_audio_features(file_path):
    y, sr = librosa.load(file_path, sr=None)  # Chargement du fichier audio, y = signal audio, sr = taux d'échantillonnage

    rms = librosa.feature.rms(y=y).mean()  # Calcul de l'énergie RMS moyenne du signal

    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)  # Extraction des hauteurs (pitches) et magnitudes du spectre
    pitch_values = pitches[magnitudes > np.median(magnitudes)]  # Sélection des hauteurs dont la magnitude est supérieure à la médiane
    pitch_mean = pitch_values.mean() if len(pitch_values) > 0 else 0  # Moyenne des hauteurs sélectionnées, 0 si vide
    pitch_std = pitch_values.std() if len(pitch_values) > 0 else 0  # Écart-type des hauteurs sélectionnées, 0 si vide

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # Extraction des 13 premiers coefficients MFCC
    mfccs_mean = mfccs.mean(axis=1)  # Moyenne de chaque coefficient MFCC sur le temps
    mfccs_std = mfccs.std(axis=1)  # Écart-type de chaque coefficient MFCC sur le temps

    zcr = librosa.feature.zero_crossing_rate(y).mean()  # Calcul du taux moyen de passage par zéro

    features = {
        "rms": rms,  # Ajout de l'énergie RMS au dictionnaire de features
        "pitch_mean": pitch_mean,  # Ajout de la moyenne des hauteurs
        "pitch_std": pitch_std,  # Ajout de l'écart-type des hauteurs
        "zcr": zcr,  # Ajout du taux de passage par zéro
    }
    for i in range(13):
        features[f"mfcc{i+1}_mean"] = mfccs_mean[i]  # Ajout de la moyenne du MFCC i+1
        features[f"mfcc{i+1}_std"] = mfccs_std[i]  # Ajout de l'écart-type du MFCC i+1

    return features  # Retourne le dictionnaire des features extraites