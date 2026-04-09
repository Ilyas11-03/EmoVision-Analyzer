import os
import tempfile
import subprocess
from typing import Optional
import whisper

# ── Singleton Whisper (cache du modèle) ───────────────────────────────────────
# CORRECTION : le modèle était rechargé à chaque appel — très coûteux.
# On le met en cache global pour toute la durée de la session.

_whisper_cache: dict = {}


def _get_whisper_model(model_size: str = "base") -> whisper.Whisper:
    """
    Retourne le modèle Whisper en cache.
    Si le modèle demandé n'est pas encore chargé, il est chargé une seule fois.

    Args:
        model_size : Taille du modèle ("tiny", "base", "small", "medium", "large").

    Returns:
        Instance du modèle Whisper.
    """
    if model_size not in _whisper_cache:
        _whisper_cache[model_size] = whisper.load_model(model_size)
    return _whisper_cache[model_size]


# ── Extraction audio depuis une vidéo ─────────────────────────────────────────


def extract_audio_from_video(
    video_path: str, output_audio_path: Optional[str] = None, sample_rate: int = 16000
) -> str:
    """
    Extrait l'audio d'une vidéo en mono WAV via ffmpeg.

    CORRECTION : vérification que ffmpeg est disponible avant l'appel.
    CORRECTION : output_audio_path optionnel — un fichier temporaire est créé
    automatiquement si non fourni.

    Args:
        video_path        : Chemin vers la vidéo source.
        output_audio_path : Chemin de sortie du WAV (optionnel).
        sample_rate       : Fréquence d'échantillonnage (défaut : 16 kHz pour Whisper).

    Returns:
        str : Chemin du fichier audio extrait.

    Raises:
        FileNotFoundError : Si la vidéo source n'existe pas.
        RuntimeError      : Si ffmpeg échoue.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : '{video_path}'")

    # Crée un fichier temporaire si aucun chemin de sortie n'est fourni
    if output_audio_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        output_audio_path = tmp.name
        tmp.close()

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-ac",
        "1",  # Mono
        "-ar",
        str(sample_rate),  # Fréquence d'échantillonnage
        "-vn",  # Ignore la piste vidéo
        output_audio_path,
    ]

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    # CORRECTION : vérification du code de retour ffmpeg
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg a échoué pour '{video_path}' :\n"
            f"{result.stderr.decode(errors='replace')}"
        )

    return output_audio_path


# ── Transcription d'un fichier audio ──────────────────────────────────────────


def transcribe_audio_whisper(
    audio_path: str, model_size: str = "base", language: Optional[str] = "fr"
) -> str:
    """
    Transcrit un fichier audio en texte via Whisper.

    CORRECTION : le modèle est récupéré depuis le cache (singleton).
    CORRECTION : language est maintenant un paramètre optionnel.
                 Si None, Whisper détecte automatiquement la langue.

    Args:
        audio_path  : Chemin vers le fichier audio (.wav).
        model_size  : Taille du modèle Whisper.
        language    : Code langue ISO ("fr", "en", ...) ou None pour auto-détection.

    Returns:
        str : Texte transcrit (chaîne vide si échec).
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Fichier audio introuvable : '{audio_path}'")

    try:
        model = _get_whisper_model(model_size)

        # CORRECTION : language=None active la détection automatique de langue
        transcribe_kwargs = {"task": "transcribe"}
        if language:
            transcribe_kwargs["language"] = language

        result = model.transcribe(audio_path, **transcribe_kwargs)
        return result.get("text", "").strip()

    except Exception as e:
        # On retourne une chaîne vide plutôt que de crasher le pipeline
        print(f"[speech_to_text] Erreur Whisper : {e}")
        return ""


# ── Pipeline complet vidéo → texte ────────────────────────────────────────────


def transcribe_video(
    video_path: str, model_size: str = "base", language: Optional[str] = "fr"
) -> str:
    """
    Pipeline complet : extrait l'audio d'une vidéo puis le transcrit en texte.
    Le fichier audio temporaire est supprimé après transcription.

    Args:
        video_path  : Chemin vers la vidéo source.
        model_size  : Taille du modèle Whisper.
        language    : Code langue ou None pour auto-détection.

    Returns:
        str : Texte transcrit.
    """
    audio_path = None
    try:
        audio_path = extract_audio_from_video(video_path)
        return transcribe_audio_whisper(audio_path, model_size, language)

    finally:
        # CORRECTION : nettoyage garanti même en cas d'exception
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


# ── Transcription avec métadonnées (timestamps) ───────────────────────────────


def transcribe_video_with_segments(
    video_path: str, model_size: str = "base", language: Optional[str] = "fr"
) -> dict:
    """
    Transcrit une vidéo et retourne le texte complet ainsi que
    les segments horodatés (utiles pour l'analyse Q/R par segment).

    Utile pour détecter automatiquement les plages temporelles des réponses
    et les passer à extract_stress_segment().

    Args:
        video_path  : Chemin vers la vidéo source.
        model_size  : Taille du modèle Whisper.
        language    : Code langue ou None pour auto-détection.

    Returns:
        dict : {
            "text"     : str,   texte complet
            "segments" : list,  [{"start": float, "end": float, "text": str}, ...]
            "language" : str,   langue détectée
        }
    """
    audio_path = None
    try:
        audio_path = extract_audio_from_video(video_path)
        model = _get_whisper_model(model_size)

        transcribe_kwargs = {"task": "transcribe"}
        if language:
            transcribe_kwargs["language"] = language

        result = model.transcribe(audio_path, **transcribe_kwargs)

        segments = [
            {
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip(),
            }
            for seg in result.get("segments", [])
        ]

        return {
            "text": result.get("text", "").strip(),
            "segments": segments,
            "language": result.get("language", "unknown"),
        }

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
