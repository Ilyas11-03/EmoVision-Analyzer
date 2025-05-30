import librosa
import numpy as np
import subprocess
import os

def extract_audio_features(video_path):
    try:
        
        # 1. Extraire l'audio avec ffmpeg
        audio_path = "temp_audio.wav"
        command = f"ffmpeg -y -i \"{video_path}\" -ac 1 -ar 22050 \"{audio_path}\""
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 2. Lire l’audio avec librosa
        y, sr = librosa.load(audio_path)

        # 3. Extraire des features audio
        zcr = np.mean(librosa.feature.zero_crossing_rate(y)[0])
        rms = np.mean(librosa.feature.rms(y=y)[0])
        pitches, _ = librosa.piptrack(y=y, sr=sr)
        pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0

        # 4. Calcul d’un score de stress simple
        stress_score = np.clip((zcr + rms + pitch / 500) / 3, 0, 1)

        # 5. Nettoyage (optionnel)
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {
            "stress_score": round(float(stress_score), 3),
            "zero_crossing_rate": round(float(zcr), 4),
            "rms": round(float(rms), 4),
            "pitch": round(float(pitch), 2)
        }

    except Exception as e:
        return {"error": str(e)}
