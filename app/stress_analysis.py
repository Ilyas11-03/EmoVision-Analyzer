import librosa  # Pour le traitement audio
import numpy as np  # Pour les calculs numériques
import subprocess  # Pour exécuter la commande ffmpeg
import os  # Pour la gestion des fichiers

def extract_audio_segment(video_path, output_audio_path, start_time, end_time, sample_rate=22050):
    """
    Extrait un segment audio de la vidéo entre start_time et end_time (en secondes).
    Utilise ffmpeg pour extraire l'audio mono à une fréquence donnée.
    """
    duration = end_time - start_time  # Calcule la durée du segment à extraire
    command = [
        "ffmpeg", "-y", "-i", video_path,  # Commande ffmpeg, -y écrase le fichier de sortie, -i spécifie la vidéo source
        "-ss", str(start_time),            # Définit le début du segment à extraire
        "-t", str(duration),               # Définit la durée du segment à extraire
        "-ac", "1",                        # Définit l'audio en mono (1 canal)
        "-ar", str(sample_rate),           # Définit le taux d'échantillonnage
        output_audio_path                  # Chemin du fichier audio de sortie
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # Exécute la commande ffmpeg sans afficher la sortie

def extract_stress_features(audio_path, sample_rate=22050):
    """
    Analyse un fichier audio pour extraire des métriques de stress :
    - pitch moyen
    - énergie (RMS)
    - fréquence de croisement zéro (ZCR)
    - score de stress combiné
    """
    try:
        y, sr = librosa.load(audio_path, sr=sample_rate) # Charge l'audio et le taux d'échantillonnage
        if len(y) == 0:                                  # Vérifie si l'audio est vide
            return {"error": "Audio vide ou inaudible."}

        zcr = librosa.feature.zero_crossing_rate(y)[0]   # Calcule la fréquence de croisement zéro
        rms = librosa.feature.rms(y=y)[0]                # Calcule l'énergie RMS
        pitches, _ = librosa.piptrack(y=y, sr=sr)        # Calcule les hauteurs (pitch) de l'audio
        non_zero_pitches = pitches[pitches > 0]          # Filtre les pitchs non nuls
        pitch_mean = float(np.mean(non_zero_pitches)) if len(non_zero_pitches) > 0 else 0.0 # Moyenne du pitch

        stress_score = round(float(np.mean(zcr)) + float(np.mean(rms)), 3)   # Score de stress combiné

        return {
            "pitch_mean": round(pitch_mean, 2),     # Pitch moyen arrondi
            "rms": round(float(np.mean(rms)), 4),   # RMS moyen arrondi
            "zcr": round(float(np.mean(zcr)), 4),   # ZCR moyen arrondi
            "stress_score": stress_score            # Score de stress
        }

    except Exception as e:
        return {"error": str(e)}                   # Retourne l'erreur en cas de problème

def extract_audio_features(video_path, sample_rate=22050):
    """
    Analyse l’audio complet de la vidéo et renvoie les indicateurs de stress.
    """
    audio_path = "temp_audio.wav"                 # Définit le chemin du fichier audio temporaire
    extract_audio_segment(video_path, audio_path, start_time=0, end_time=9999, sample_rate=sample_rate)  # Extrait tout l'audio
    features = extract_stress_features(audio_path, sample_rate=sample_rate)  # Analyse les caractéristiques de stress
    if os.path.exists(audio_path):              # Vérifie si le fichier temporaire existe
        os.remove(audio_path)                   # Supprime le fichier temporaire
    return features                             # Retourne les caractéristiques extraites

def extract_stress_segment(video_path, start_sec, end_sec, sample_rate=22050):
    """
    Analyse uniquement un segment temporel de la vidéo (ex : réponse à une question spécifique).
    """
    segment_path = "temp_audio_segment.wav"     # Définit le chemin du fichier audio temporaire pour le segment
    extract_audio_segment(video_path, segment_path, start_time=start_sec, end_time=end_sec, sample_rate=sample_rate)  # Extrait le segment audio
    features = extract_stress_features(segment_path, sample_rate=sample_rate)  # Analyse les caractéristiques de stress du segment
    if os.path.exists(segment_path): # Vérifie si le fichier temporaire existe
        os.remove(segment_path)      # Supprime le fichier temporaire
    return features                  # Retourne les caractéristiques extraites
