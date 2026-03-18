import os
from deepface import DeepFace

# ── Émotions primaires détectées directement par DeepFace ────────────────────
PRIMARY_EMOTIONS = ["happy", "sad", "angry", "fear", "disgust", "neutral", "surprise"]

# Ajouter un filtre de confiance minimale
CONFIDENCE_THRESHOLD = 50.0  # Score minimum pour accepter le résultat

# ── Émotions dérivées par heuristique (signalées comme telles) ───────────────
# Ces valeurs sont des approximations, pas des détections directes.
# Pondérations issues d'une approximation raisonnée — à mentionner dans le mémoire.
DERIVED_EMOTION_RULES = {
    "excited":  lambda e: e.get("happy", 0) * 0.6,
    "bored":    lambda e: e.get("sad", 0)   * 0.5,
    "confused": lambda e: e.get("neutral", 0) * 0.4,
    "silly":    lambda e: e.get("happy", 0) * 0.3 + e.get("surprise", 0) * 0.2,
    "nervous":  lambda e: e.get("fear", 0)  * 0.6 + e.get("surprise", 0) * 0.2,
     # ── Nouvelles émotions ──────────────────────────────────────────────────
    "frustrated": lambda e: e.get("angry", 0) * 0.5 + e.get("disgust", 0) * 0.3,
    "anxious":    lambda e: e.get("fear", 0)  * 0.7 + e.get("neutral", 0) * 0.2,
    "proud":      lambda e: e.get("happy", 0) * 0.4 + e.get("surprise", 0) * 0.3,
}

# ── Émotions considérées comme "suspectes" (signaux de tension) ───────────────
SUSPECT_EMOTIONS = ["nervous", "fear", "confused", "pain", "angry", "disgust", "hate", "frustrated", "anxious"]

# ── Utilitaire : extraction du nom de fichier cross-platform ─────────────────
def _get_filename(path: str) -> str:
    """Extrait le nom de fichier de manière fiable sur Windows et Linux."""
    return os.path.basename(path)

# ── Fonction principale ───────────────────────────────────────────────────────
def detect_emotions_on_image(image_path: str) -> dict:
    """
    Analyse une image pour détecter les émotions faciales.

    - Les émotions primaires sont détectées par DeepFace.
    - Les émotions dérivées sont calculées par heuristique et clairement
      marquées comme telles dans le résultat.
    - L'émotion dominante est déterminée uniquement sur les émotions primaires
      pour éviter que les valeurs dérivées ne biaisent le résultat.
    - Les frames sans visage détecté avec confiance suffisante sont filtrées.

    Args:
        image_path : Chemin vers l'image à analyser.

    Returns:
        dict : {
            "frame"              : str,  nom du fichier
            "dominant_emotion"   : str,  émotion primaire dominante
            "emotions"           : dict, scores primaires (DeepFace)
            "derived_emotions"   : dict, scores dérivés (heuristique)
            "is_suspect"         : bool, True si dominante dans SUSPECT_EMOTIONS
            "is_derived_dominant": bool, True si la dominante globale est dérivée
        }
    """
    filename = _get_filename(image_path)

    try:
        result = DeepFace.analyze(
            img_path          = image_path,
            actions           = ["emotion"],
            enforce_detection = False,
            silent            = True
        )

        # CORRECTION : vérification de la structure AVANT tout accès à result[0]
        if not isinstance(result, list) or len(result) == 0:
            return _empty_result(filename, reason="Aucun résultat retourné par DeepFace.")

        raw = result[0]

        # CORRECTION : vérification face_confidence APRÈS validation de la structure
        face_confidence = raw.get("face_confidence", 1.0)
        if face_confidence < 0.5:
            return _empty_result(
                filename,
                reason="Visage non détecté avec suffisamment de confiance."
            )

        primary_emotions = raw.get("emotion", {})

        # Garder uniquement les émotions primaires reconnues
        primary_scores = {
            k: round(float(v), 2)
            for k, v in primary_emotions.items()
            if k in PRIMARY_EMOTIONS
        }

        if not primary_scores:
            return _empty_result(filename, reason="Scores d'émotions primaires vides.")

        # ── Émotions dérivées ─────────────────────────────────────────────────
        # CORRECTION : séparées des primaires pour ne pas biaiser la dominante
        derived_scores = {
            name: round(rule(primary_scores), 2)
            for name, rule in DERIVED_EMOTION_RULES.items()
        }

        # ── Émotion dominante sur primaires uniquement ────────────────────────
        dominant_emotion = max(primary_scores, key=primary_scores.get)

        # Vérification transparence : la dominante serait-elle différente
        # si on incluait les dérivées ?
        all_scores          = primary_scores | derived_scores
        dominant_overall    = max(all_scores, key=all_scores.get)
        is_derived_dominant = dominant_overall != dominant_emotion

        return {
            "frame":               filename,
            "dominant_emotion":    dominant_emotion,
            "emotions":            primary_scores,
            "derived_emotions":    derived_scores,
            "is_suspect":          dominant_emotion in SUSPECT_EMOTIONS,
            "is_derived_dominant": is_derived_dominant,
        }

    except Exception as e:
        return _empty_result(filename, reason=str(e))
# ── Résultat vide standardisé ─────────────────────────────────────────────────

def _empty_result(filename: str, reason: str = "") -> dict:
    """Retourne un résultat vide standardisé en cas d'échec."""
    return {
        "frame":               filename,
        "dominant_emotion":    "N/A",
        "emotions":            {},
        "derived_emotions":    {},
        "is_suspect":          False,
        "is_derived_dominant": False,
        "error":               reason,
    }


# ── Fonction utilitaire : analyse d'un lot d'images ──────────────────────────

def detect_emotions_batch(image_paths: list) -> list:
    """
    Analyse un lot d'images et retourne la liste des résultats.
    Utile pour traiter toutes les frames extraites d'une vidéo.

    Args:
        image_paths : Liste de chemins vers les images.

    Returns:
        list : Liste de dicts issus de detect_emotions_on_image().
    """
    return [detect_emotions_on_image(path) for path in image_paths]