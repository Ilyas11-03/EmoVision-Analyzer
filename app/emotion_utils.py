from collections import Counter
from typing import List, Tuple

# ── Catégories d'émotions ─────────────────────────────────────────────────────
EMOTION_CATEGORIES = {
    "positive": [
        "happy",
        "excited",
        "smile",
        "laughter",
        "proud",
        "adorable",
        "focused",
    ],
    "negative": [
        "angry",
        "fear",
        "disgust",
        "sad",
        "nervous",
        "pain",
        "hate",
        "frustrated",
        "anxious",
        "pain",
        "sick",
        "dizzy",
        "embarrassed",
        "pouty",
        "tired",
        "suspicious",
    ],
    "neutral": [
        "neutral",
        "confused",
        "surprise",
        "bored",
        "obligated",
        "daydreaming",
        "shy",
        "arrogant",
        "thinking",
    ],
}


# ── Fonction 1 : Frames les plus expressives ──────────────────────────────────
def get_top_emotion_frames(emotion_results: List[dict], top_n: int = 5) -> List[dict]:
    """
    Retourne les frames ayant le plus fort score émotionnel primaire.

    CORRECTION : travaille sur la liste complète des résultats (pas un seul dict).
    CORRECTION : conserve is_suspect et is_derived_dominant dans le résultat.

    Args:
        emotion_results : Liste de dicts issus de detect_emotions_on_image().
        top_n           : Nombre de frames à retourner.

    Returns:
        Liste triée des frames les plus expressives.
    """
    scored = (
        []
    )  # Liste de dicts avec frame, émotion dominante, intensité, is_suspect, is_derived_dominant

    for item in emotion_results:
        primary_emotions = item.get("emotions", {})  # Scores primaires uniquement

        if not primary_emotions:
            continue

        max_score = max(
            primary_emotions.values()
        )  # Score de l'émotion primaire la plus forte

        scored.append(
            {
                "frame": item.get("frame", "unknown"),
                "dominant_emotion": item.get("dominant_emotion", "N/A"),
                "intensity": round(max_score, 2),
                # CORRECTION : is_suspect était perdu, maintenant conservé
                "is_suspect": item.get("is_suspect", False),
                # CORRECTION : info sur les dérivées conservée pour le rapport
                "is_derived_dominant": item.get("is_derived_dominant", False),
                # Ajout : top 3 des émotions primaires pour enrichir le rapport PDF
                "top_primary_emotions": _get_top_n_emotions(primary_emotions, n=3),
            }
        )

    return sorted(scored, key=lambda x: x["intensity"], reverse=True)[:top_n]


# ── Fonction 2 : Statistiques des émotions dominantes ────────────────────────


def get_dominant_emotion_stats(
    emotion_results: List[dict], top_n: int = 3
) -> List[Tuple[str, int]]:
    """
    Retourne les émotions dominantes les plus fréquentes sur toutes les frames.

    CORRECTION : filtre les résultats sans émotion valide ("N/A", None, erreur).

    Args:
        emotion_results : Liste de dicts issus de detect_emotions_on_image().
        top_n           : Nombre d'émotions à retourner.

    Returns:
        Liste de tuples (émotion, count) triés par fréquence décroissante.
    """
    dominant_list = [
        item.get("dominant_emotion")
        for item in emotion_results
        if item.get("dominant_emotion") not in ("N/A", None) and "error" not in item
    ]

    # Après (suggestion Sourcery)
    return Counter(dominant_list).most_common(top_n) if dominant_list else []


# ── Fonction 3 : Normalisation en 3 catégories ───────────────────────────────


def normalize_emotions(emotions_dict: dict) -> dict:
    """
    Regroupe les scores d'émotions primaires en trois catégories :
    positive, negative, neutral.

    CORRECTION : la fonction était définie mais jamais appelée dans le pipeline.
    Elle est maintenant utilisée par get_emotion_category_breakdown().

    Args:
        emotions_dict : Dict {émotion: score} issu des scores primaires.

    Returns:
        dict : {"positive": float, "negative": float, "neutral": float}
    """
    normalized = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    for emotion, score in emotions_dict.items():
        for category, labels in EMOTION_CATEGORIES.items():
            if emotion.lower() in labels:
                normalized[category] += score
                break

    return normalized


# ── Fonction 4 : Répartition catégorielle sur toutes les frames ───────────────


def get_emotion_category_breakdown(emotion_results: List[dict]) -> dict:
    """
    Calcule la répartition en pourcentage des trois catégories émotionnelles
    (positive / negative / neutral) sur l'ensemble des frames.

    CORRECTION : normalize_emotions() est maintenant effectivement utilisée.
    Utile pour le rapport PDF et les métriques du PFE.

    Args:
        emotion_results : Liste de dicts issus de detect_emotions_on_image().

    Returns:
        dict : {
            "positive" : float (%),
            "negative" : float (%),
            "neutral"  : float (%),
            "dominant_category" : str
        }
    """
    totals = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    valid_frames = 0

    for item in emotion_results:
        primary_emotions = item.get("emotions", {})
        if not primary_emotions:
            continue

        frame_normalized = normalize_emotions(primary_emotions)
        for cat in totals:
            totals[cat] += frame_normalized[cat]
        valid_frames += 1

    if valid_frames == 0:
        return {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 0.0,
            "dominant_category": "N/A",
        }

    # Normalisation en pourcentage
    grand_total = sum(totals.values())
    breakdown = {
        cat: round(val / grand_total * 100, 1) if grand_total > 0 else 0.0
        for cat, val in totals.items()
    }
    breakdown["dominant_category"] = max(
        ["positive", "negative", "neutral"], key=lambda c: breakdown[c]
    )

    return breakdown


# ── Fonction 5 : Détection de dissonance émotionnelle ────────────────────────


def detect_emotional_dissonance(
    emotion_results: List[dict], window_size: int = 5
) -> dict:
    """
    Détecte les alternances fréquentes entre catégories émotionnelles opposées
    sur une fenêtre glissante — indicateur de dissonance émotionnelle.

    Concept utilisable directement dans le mémoire PFE :
    une dissonance élevée peut signaler un état de stress ou d'inconfort.

    Args:
        emotion_results : Liste de dicts issus de detect_emotions_on_image().
        window_size     : Taille de la fenêtre glissante (en frames).

    Returns:
        dict : {
            "dissonance_score" : float (0.0 à 1.0),
            "interpretation"   : str
        }
    """
    categories = []
    for item in emotion_results:
        emotion = item.get("dominant_emotion", "N/A")
        cat = next(
            (
                c
                for c, labels in EMOTION_CATEGORIES.items()
                if emotion.lower() in labels
            ),
            "unknown",
        )
        categories.append(cat)

    if len(categories) < 2:
        return {"dissonance_score": 0.0, "interpretation": "Données insuffisantes."}

    # Compte les changements de catégorie dans les fenêtres glissantes
    transitions = 0
    total_windows = 0

    for i in range(len(categories) - window_size + 1):
        window = categories[i : i + window_size]
        # Après (suggestion Sourcery)
        unique = {w for w in window if w != "unknown"}
        if len(unique) >= 2:
            transitions += 1
        total_windows += 1

    dissonance_score = (
        round(transitions / total_windows, 2) if total_windows > 0 else 0.0
    )

    if dissonance_score >= 0.7:
        interpretation = "Dissonance émotionnelle élevée — alternances fréquentes entre états opposés."
    elif dissonance_score >= 0.4:
        interpretation = "Dissonance modérée — quelques transitions entre états émotionnels différents."
    else:
        interpretation = (
            "Faible dissonance — comportement émotionnel stable et cohérent."
        )

    return {
        "dissonance_score": dissonance_score,
        "interpretation": interpretation,
    }


# ── Utilitaire interne ────────────────────────────────────────────────────────


def _get_top_n_emotions(emotions_dict: dict, n: int = 3) -> List[Tuple[str, float]]:
    """
    Retourne les n émotions avec les scores les plus élevés.

    Args:
        emotions_dict : Dict {émotion: score}.
        n             : Nombre d'émotions à retourner.

    Returns:
        Liste de tuples (émotion, score) triés par score décroissant.
    """
    return sorted(emotions_dict.items(), key=lambda x: x[1], reverse=True)[:n]
