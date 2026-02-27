import librosa
import numpy as np
import subprocess
import os

# ── Extraction audio via ffmpeg ───────────────────────────────────────────────
def extract_audio_segment(video_path: str, output_audio_path: str,
                           start_time: float = 0, end_time: float = None,
                           sample_rate: int = 22050):
    """
    Extrait un segment audio d'une vidéo avec ffmpeg.
    Si end_time est None, extrait jusqu'à la fin de la vidéo.
    """
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-ss", str(start_time),
        "-ac", "1",
        "-ar", str(sample_rate),
    ]

    # CORRECTION : on n'utilise plus end_time=9999 (hack non robuste).
    # Si end_time est fourni, on calcule la durée réelle du segment.
    if end_time is not None:
        duration = end_time - start_time
        command += ["-t", str(duration)]

    command.append(output_audio_path)

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg a échoué pour '{video_path}' : {result.stderr.decode()}"
        )

# ── Extraction des features audio ────────────────────────────────────────────

def extract_audio_features(audio_path: str, sample_rate: int = 22050) -> dict:
    """
    Extrait un ensemble complet de features acoustiques depuis un fichier audio :
    - RMS (énergie)
    - Pitch moyen et écart-type
    - ZCR (taux de passage par zéro)
    - MFCCs (13 coefficients, moyenne + écart-type)
    - Score de stress normalisé

    Returns:
        dict : Dictionnaire des features extraites.
    """
    try:
        # CORRECTION : plus de duration=60 — on analyse tout le fichier.
        y, sr = librosa.load(audio_path, sr=sample_rate)

        if len(y) == 0:
            return {"error": "Audio vide ou inaudible."}

        # ── RMS ──────────────────────────────────────────────────────────────
        rms_frames = librosa.feature.rms(y=y)[0]
        rms_mean = float(np.mean(rms_frames))

        # ── Pitch ─────────────────────────────────────────────────────────────
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        # On filtre les pitchs dont la magnitude dépasse la médiane
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        pitch_mean = float(pitch_values.mean()) if len(pitch_values) > 0 else 0.0
        pitch_std  = float(pitch_values.std())  if len(pitch_values) > 0 else 0.0

        # ── ZCR ───────────────────────────────────────────────────────────────
        zcr_frames = librosa.feature.zero_crossing_rate(y)[0]
        zcr_mean = float(np.mean(zcr_frames))

        # ── MFCCs ─────────────────────────────────────────────────────────────
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfccs_mean = mfccs.mean(axis=1)
        mfccs_std  = mfccs.std(axis=1)

        # ── Score de stress normalisé ─────────────────────────────────────────
        # CORRECTION : au lieu de ZCR + RMS (échelles différentes),
        # on normalise chaque composante dans [0, 1] avant combinaison.
        # Valeurs de référence issues de la littérature sur la parole stressée :
        # RMS ref ≈ 0.05, ZCR ref ≈ 0.1
        rms_norm = min(rms_mean / 0.05, 1.0)
        zcr_norm = min(zcr_mean / 0.10, 1.0)
        # Pondération : RMS contribue plus au stress perceptible
        stress_score = round(0.6 * rms_norm + 0.4 * zcr_norm, 3)

        # ── Assemblage du dictionnaire ────────────────────────────────────────
        features = {
            "rms":          round(rms_mean,   4),
            "pitch_mean":   round(pitch_mean, 2),
            "pitch_std":    round(pitch_std,  2),
            "zcr":          round(zcr_mean,   4),
            "stress_score": stress_score,
        }

        # MFCCs ajoutés dynamiquement
        for i in range(13):
            features[f"mfcc{i+1}_mean"] = round(float(mfccs_mean[i]), 4)
            features[f"mfcc{i+1}_std"]  = round(float(mfccs_std[i]),  4)

        return features

    except Exception as e:
        return {"error": str(e)}

# ── Fonctions publiques du pipeline ──────────────────────────────────────────

def get_audio_features_from_video(video_path: str, sample_rate: int = 22050) -> dict:
    """
    Analyse l'audio complet d'une vidéo.
    Remplace l'ancienne extract_audio_features(video_path) de stress_analysis.py
    """
    audio_path = "temp_audio_full.wav"
    try:
        extract_audio_segment(video_path, audio_path,
                               start_time=0, end_time=None,
                               sample_rate=sample_rate)
        return extract_audio_features(audio_path, sample_rate)
    finally:
        # CORRECTION : nettoyage garanti même en cas d'exception
        if os.path.exists(audio_path):
            os.remove(audio_path)

def get_audio_features_from_segment(video_path: str, start_sec: float,
                                     end_sec: float, sample_rate: int = 22050) -> dict:
    """
    Analyse uniquement un segment temporel de la vidéo.
    Remplace l'ancienne extract_stress_segment() de stress_analysis.py.
    """
    segment_path = "temp_audio_segment.wav"
    try:
        extract_audio_segment(video_path, segment_path,
                               start_time=start_sec, end_time=end_sec,
                               sample_rate=sample_rate)
        return extract_audio_features(segment_path, sample_rate)
    finally:
        if os.path.exists(segment_path):
            os.remove(segment_path)