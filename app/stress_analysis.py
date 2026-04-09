import os
import subprocess  # CORRECTION : import subprocess pour l'extraction audio segmentée
from typing import Optional

import librosa
import numpy as np
import soundfile as sf

# ── Constantes de normalisation ───────────────────────────────────────────────
RMS_REF = 0.05
ZCR_REF = 0.10

STRESS_WEIGHTS = {
    "rms": 0.6,
    "zcr": 0.4,
}

PITCH_MIN = 50.0  # Hz — voix grave masculine
PITCH_MAX = 400.0  # Hz — voix aiguë féminine


# ── Extraction audio via ffmpeg ───────────────────────────────────────────────
# CORRECTION : extraction segmentée avec gestion des erreurs via subprocess.
def extract_audio_segment(
    video_path: str,
    output_audio_path: str,
    start_time: float = 0,
    end_time: Optional[float] = None,
    sample_rate: int = 22050,
):
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video introuvable : '{video_path}'")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-ss",
        str(start_time),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-vn",
    ]

    if end_time is not None:
        duration = max(0, end_time - start_time)
        command += ["-t", str(duration)]

    command.append(output_audio_path)

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg a echoue pour '{video_path}' :\n"
            f"{result.stderr.decode(errors='replace')}"
        )


# ── Chargement audio robuste ──────────────────────────────────────────────────
def _load_audio(audio_path: str, sample_rate: int = 22050):
    """
    Charge un fichier audio en évitant le bug librosa/audioread sur Windows.

    CORRECTION : tente soundfile en premier (plus stable sur Windows),
    puis fallback sur librosa si soundfile échoue.

    Returns:
        tuple : (y: np.ndarray, sr: int)
    """
    # ── Tentative 1 : soundfile (backend stable sur Windows) ─────────────────
    try:
        y, sr = sf.read(audio_path, dtype="float32", always_2d=False)

        # Resample si la fréquence ne correspond pas
        if sr != sample_rate:
            import resampy

            y = resampy.resample(y, sr, sample_rate)
            sr = sample_rate

        return y, sr

    except Exception:
        pass

    # ── Tentative 2 : librosa avec backend explicite ──────────────────────────
    try:
        y, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
        return y, sr

    except Exception as e:
        raise RuntimeError(f"Impossible de charger l'audio '{audio_path}' : {e}")


# ── Extraction des features acoustiques ──────────────────────────────────────
def extract_acoustic_features(audio_path: str, sample_rate: int = 22050) -> dict:
    """
    Extrait un ensemble complet de features acoustiques depuis un fichier audio.

    Features extraites :
    - RMS          : énergie du signal (intensité vocale)
    - Pitch        : hauteur tonale (moyenne + écart-type)
    - ZCR          : taux de passage par zéro (richesse spectrale)
    - MFCCs        : 13 coefficients cepstraux (timbre vocal)
    - stress_score : score combiné normalisé [0.0 – 1.0]

    CORRECTION : utilise _load_audio() au lieu de librosa.load() directement
    pour éviter le bug 'parent' de audioread sur Windows.
    """
    try:
        # CORRECTION : chargement via _load_audio() robuste
        y, sr = _load_audio(audio_path, sample_rate)

        if len(y) == 0:
            return {"error": "Audio vide ou inaudible."}

        # ── RMS ───────────────────────────────────────────────────────────────
        rms_frames = librosa.feature.rms(y=y)[0]
        rms_mean = float(np.mean(rms_frames))

        # ── Pitch ─────────────────────────────────────────────────────────────
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]

        # CORRECTION : on ne garde que les pitchs dans la plage vocale humaine
        pitch_values = pitch_values[
            (pitch_values >= PITCH_MIN) & (pitch_values <= PITCH_MAX)
        ]

        pitch_mean = float(pitch_values.mean()) if len(pitch_values) > 0 else 0.0
        pitch_std = float(pitch_values.std()) if len(pitch_values) > 0 else 0.0

        # ── ZCR ───────────────────────────────────────────────────────────────
        zcr_frames = librosa.feature.zero_crossing_rate(y)[0]
        zcr_mean = float(np.mean(zcr_frames))

        # ── MFCCs ─────────────────────────────────────────────────────────────
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfccs_mean = mfccs.mean(axis=1)
        mfccs_std = mfccs.std(axis=1)

        # ── Score de stress normalisé ─────────────────────────────────────────
        rms_norm = min(rms_mean / RMS_REF, 1.0)
        zcr_norm = min(zcr_mean / ZCR_REF, 1.0)
        stress_score = round(
            STRESS_WEIGHTS["rms"] * rms_norm + STRESS_WEIGHTS["zcr"] * zcr_norm, 3
        )

        # ── Assemblage ────────────────────────────────────────────────────────
        features = {
            "rms": round(rms_mean, 4),
            "pitch_mean": round(pitch_mean, 2),
            "pitch_std": round(pitch_std, 2),
            "zcr": round(zcr_mean, 4),
            "stress_score": stress_score,
        }

        for i in range(13):
            features[f"mfcc{i + 1}_mean"] = round(float(mfccs_mean[i]), 4)
            features[f"mfcc{i + 1}_std"] = round(float(mfccs_std[i]), 4)

        return features

    except Exception as e:
        return {"error": str(e)}


# ── Fonctions publiques du pipeline ──────────────────────────────────────────
# Analyse l'audio complet d'une vidéo — appelle extract_audio_segment + extract_acoustic_features
def extract_audio_features(video_path: str, sample_rate: int = 22050) -> dict:
    """Analyse l'audio complet d'une vidéo."""
    audio_path = "temp_audio_full.wav"
    try:
        extract_audio_segment(
            video_path, audio_path, start_time=0, end_time=None, sample_rate=sample_rate
        )
        return extract_acoustic_features(audio_path, sample_rate)
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


# Analyse uniquement un segment temporel (ex: réponse à une question spécifique)
def extract_stress_segment(
    video_path: str, start_sec: float, end_sec: float, sample_rate: int = 22050
) -> dict:
    """Analyse uniquement un segment temporel de la vidéo."""
    if end_sec <= start_sec:
        return {"error": f"Segment invalide : start={start_sec} >= end={end_sec}"}

    segment_path = "temp_audio_segment.wav"
    try:
        extract_audio_segment(
            video_path,
            segment_path,
            start_time=start_sec,
            end_time=end_sec,
            sample_rate=sample_rate,
        )
        return extract_acoustic_features(segment_path, sample_rate)
    finally:
        if os.path.exists(segment_path):
            os.remove(segment_path)


# Compare le stress sur plusieurs segments — utile pour suivre l'évolution question par question
def compare_stress_segments(
    video_path: str, segments: list, sample_rate: int = 22050
) -> list:
    """Compare le niveau de stress sur plusieurs segments temporels."""
    results = []
    for seg in segments:
        label = seg.get("label", "segment")
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        features = extract_stress_segment(video_path, start, end, sample_rate)
        results.append(
            {
                "label": label,
                "start": start,
                "end": end,
                "features": features,
            }
        )
    return results
