import librosa # Importation de la bibliothèque librosa pour le traitement audio
import numpy as np # Importation de numpy pour les calculs numériques
import subprocess # Importation de la bibliothèque subprocess pour exécuter des commandes système
import os # Importation du module os pour la gestion des fichiers

def extract_audio_features(video_path): # Définition de la fonction pour extraire les features audio d'une vidéo
    try: # Bloc try pour gérer les exceptions
        
        # 1. Extraire l'audio avec ffmpeg
        audio_path = "temp_audio.wav" # Chemin du fichier audio temporaire
        command = f"ffmpeg -y -i \"{video_path}\" -ac 1 -ar 22050 \"{audio_path}\"" # Commande ffmpeg pour extraire l'audio en mono à 22050 Hz
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # Exécution de la commande sans afficher la sortie
        
        if not os.path.exists(audio_path): # Vérifie si le fichier audio a bien été créé
            return {"error": "Échec extraction audio avec ffmpeg."} # Retourne une erreur si l'extraction a échoué
        
        # 2. Lire l’audio avec librosa
        y, sr = librosa.load(audio_path) # Charge le fichier audio et retourne le signal et le taux d'échantillonnage
        
        # 3. Extraire des features audio
        zcr = np.mean(librosa.feature.zero_crossing_rate(y)[0]) # Calcule la moyenne du taux de passage par zéro
        rms = np.mean(librosa.feature.rms(y=y)[0]) # Calcule la moyenne de l'énergie du signal (RMS)
        pitches, _ = librosa.piptrack(y=y, sr=sr) # Extrait les hauteurs (pitch) du signal audio

        # Traitement du pitch : moyenne des fréquences positives
        non_zero_pitches = pitches[pitches > 0] # Sélectionne les valeurs de pitch supérieures à zéro
        pitch_mean = float(np.mean(non_zero_pitches)) if len(non_zero_pitches) > 0 else 0.0 # Calcule la moyenne des pitches non nuls

        # 4. Calcul d’un score de stress simple
        stress_score = round(float(np.mean(zcr)) + float(np.mean(rms)), 3) # Additionne zcr et rms pour obtenir un score de stress

        # 5. Nettoyage (optionnel)
        if os.path.exists(audio_path): # Vérifie si le fichier audio existe
            os.remove(audio_path) # Supprime le fichier audio temporaire

        return { # Retourne les features extraites sous forme de dictionnaire
            "pitch_mean": round(pitch_mean, 2), # Moyenne du pitch arrondie à 2 décimales
            "rms": round(float(np.mean(rms)), 4), # RMS arrondi à 4 décimales
            "zcr": round(float(np.mean(zcr)), 4), # ZCR arrondi à 4 décimales
            "stress_score": stress_score # Score de stress calculé
        }

    except Exception as e:
        return {"error": str(e)}
