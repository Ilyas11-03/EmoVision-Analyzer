import os
import torch
import torchaudio
from typing import Optional

# ── Émotions supportées ───────────────────────────────────────────────────────
EMOTIONS = [
    "happy", "sad", "angry", "neutral",
    "bored", "excited", "confused",
    "surprise", "disgust", "fear",
    "frustrated", "anxious", "proud"  # ← nouveaux
]

# ── Modèle placeholder ────────────────────────────────────────────────────────
# CORRECTION : DummyEmotionModel clairement documenté comme placeholder.
# À remplacer par un vrai modèle entraîné (ex: wav2vec2 fine-tuné sur RAVDESS,
# CREMA-D ou un corpus francophone annoté).

class DummyEmotionModel(torch.nn.Module):
    """
    Modèle placeholder — NE PAS utiliser en production.
    Retourne des scores aléatoires via une couche linéaire non entraînée.
    Remplacer par un modèle fine-tuné sur un corpus audio émotionnel annoté.
    """
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(40, len(EMOTIONS))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.softmax(self.fc(x.mean(dim=1)), dim=-1)


# ── Singleton modèle ──────────────────────────────────────────────────────────
# CORRECTION : le modèle est instancié une seule fois et mis en cache.

_model_instance: Optional[DummyEmotionModel] = None

def _get_model() -> DummyEmotionModel:
    """Retourne le modèle en cache (chargé une seule fois)."""
    global _model_instance
    if _model_instance is None:
        _model_instance = DummyEmotionModel()
        _model_instance.eval()
    return _model_instance


# ── Extraction audio ──────────────────────────────────────────────────────────

def _extract_audio(video_path: str, audio_path: str, sample_rate: int = 16000):
    """
    Extrait l'audio d'une vidéo via ffmpeg.

    CORRECTION : os.system() remplacé par subprocess pour gérer les erreurs.
    """
    import subprocess
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "1", "-ar", str(sample_rate),
            audio_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg a échoué : {result.stderr.decode(errors='replace')}"
        )


# ── Fonction principale ───────────────────────────────────────────────────────

def extract_audio_emotions(video_path: str) -> dict:
    """
    Analyse les émotions vocales d'une vidéo via extraction MFCC + modèle.

    ⚠️ AVERTISSEMENT : le modèle actuel (DummyEmotionModel) est un placeholder
    non entraîné. Les scores retournés sont aléatoires et ne doivent pas
    être utilisés pour des conclusions réelles.
    À remplacer par un modèle fine-tuné (wav2vec2, HuBERT, etc.).

    Args:
        video_path : Chemin vers la vidéo à analyser.

    Returns:
        dict : {
            "dominant_emotion"    : str,
            "emotion_distribution": dict {émotion: score %},
            "is_placeholder"      : bool,  True tant que DummyModel est utilisé
            "warning"             : str,   avertissement si placeholder actif
        }
    """
    if not os.path.isfile(video_path):
        return {"error": f"Vidéo introuvable : '{video_path}'"}

    audio_path = "temp_voice_emotion.wav"

    try:
        _extract_audio(video_path, audio_path)
        waveform, sample_rate = torchaudio.load(audio_path)

        # Extraction MFCC
        mfcc_transform = torchaudio.transforms.MFCC(
            sample_rate=sample_rate,
            n_mfcc=40
        )
        mfcc = mfcc_transform(waveform).transpose(1, 2)

        model = _get_model()

        with torch.no_grad():
            output = model(mfcc)

        scores        = output.squeeze().tolist()
        dominant_idx  = int(torch.argmax(output))
        dominant_emotion = EMOTIONS[dominant_idx]

        distribution = {
            EMOTIONS[i]: round(float(scores[i]) * 100, 2)
            for i in range(len(EMOTIONS))
        }

        # CORRECTION : flag is_placeholder pour signaler clairement
        # dans le rapport que ces scores ne sont pas fiables
        return {
            "dominant_emotion":     dominant_emotion,
            "emotion_distribution": distribution,
            "is_placeholder":       True,
            "warning": (
                "⚠️ Modèle non entraîné — scores non représentatifs. "
                "Remplacer DummyEmotionModel par un modèle fine-tuné "
                "sur un corpus audio émotionnel annoté (RAVDESS, CREMA-D...)."
            ),
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # CORRECTION : nettoyage garanti via finally
        if os.path.exists(audio_path):
            os.remove(audio_path)