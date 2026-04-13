from collections import Counter
from typing import List

# ── Catégories d'émotions ─────────────────────────────────────────────────────
EMOTION_CATEGORIES = {
    "positive": ["happy", "excited", "smile", "laughter"],
    "negative": ["angry", "fear", "disgust", "sad", "nervous", "pain", "hate"],
    "neutral": ["neutral", "confused", "surprise", "bored"],
}

# ── Distinction émotions primaires vs dérivées ────────────────────────────────
# Important pour la transparence académique : les émotions dérivées sont
# calculées par heuristique, pas détectées directement par DeepFace.

PRIMARY_EMOTIONS = ["happy", "sad", "angry", "fear", "disgust", "neutral", "surprise"]
DERIVED_EMOTIONS = ["excited", "bored", "confused", "nervous", "silly"]

# ── Templates de phrases (accord grammatical corrigé) ────────────────────────

SUMMARY_TEMPLATES = {
    "happy": "La personne montre des signes de joie ou d'enthousiasme.",
    "sad": "La personne paraît triste ou mélancolique.",
    "angry": "La personne manifeste de l'agacement ou de la colère.",
    "fear": "La personne semble inquiète ou effrayée.",
    "disgust": "La personne exprime du dégoût ou du rejet.",
    "neutral": "La personne semble calme et peu expressive.",
    "surprise": "La personne réagit de manière étonnée ou inattendue.",
    "excited": "La personne semble enthousiaste. (émotion inférée)",
    "bored": "La personne paraît désintéressée. (émotion inférée)",
    "confused": "La personne paraît désorientée. (émotion inférée)",
    "nervous": "La personne semble tendue. (émotion inférée)",
    "silly": "La personne adopte une attitude légère. (émotion inférée)",
    "pain": "La personne manifeste un inconfort ou une douleur.",
    "hate": "La personne présente des signes de rejet ou de mépris.",
    "smile": "La personne affiche des sourires fréquents.",
    "laughter": "La personne rit fréquemment ou semble détendue.",
    "frustrated": (
        "La personne manifeste des signes de frustration "
        "ou d'impatience. (émotion inférée)"
    ),
    "anxious": "La personne semble anxieuse. (émotion inférée)",
    "proud": "La personne affiche une attitude fière. (émotion inférée)",
    "pouty": "La personne semble bouder légèrement.",
    "sick": "La personne semble éprouver un malaise physique.",
    "dizzy": "La personne semble désorientée ou déstabilisée.",
    "obligated": "La personne semble agir par obligation.",
    "daydreaming": "La personne semble absente dans ses pensées.",
    "shy": "La personne semble timide ou mal à l'aise.",
    "arrogant": "La personne adopte une attitude distante.",
    "adorable": "La personne exprime une émotion douce.",
    "focused": "La personne semble concentrée et attentive.",
    "thinking": "La personne semble en train de réfléchir.",
    "suspicious": "La personne manifeste de la méfiance.",
    "tired": "La personne semble fatiguée ou épuisée.",
    "embarrassed": "La personne semble gênée.",
}


# ── Fonction principale ───────────────────────────────────────────────────────
def generate_behavior_summary(emotion_results, category_breakdown=None) -> str:
    """
    Génère un résumé textuel du comportement émotionnel global
    à partir de la liste complète des résultats frame par frame.

    CORRECTION : reçoit maintenant emotion_results (liste complète)
    au lieu de top_frames uniquement, pour une analyse plus représentative.
    Génère un résumé multi-émotions au lieu d'une seule émotion dominante.

    Args:
        emotion_results : Liste de dicts issus de detect_emotions_on_image().

    Returns:
        str : Résumé comportemental en français.
    """
    # ── 1. Collecter les émotions dominantes ──────────────────────────────────
    dominant_list = [
        r.get("dominant_emotion", "N/A")
        for r in emotion_results
        if r.get("dominant_emotion") not in ("N/A", None)
    ]

    if not dominant_list:
        return "Le visage semble neutre ou difficile à analyser émotionnellement."

    counter = Counter(dominant_list)
    total = len(dominant_list)
    top_3 = counter.most_common(3)

    # ── 2. Catégorie dominante globale ────────────────────────────────────────
    # CORRECTION : category_breakdown fourni → on l'utilise directement
    # Sinon on le calcule depuis emotion_results
    if category_breakdown:
        dominant_category = category_breakdown.get("dominant_category", "neutral")
    else:
        # Calcul local si category_breakdown non fourni
        category_scores = {"positive": 0, "negative": 0, "neutral": 0}
        for emotion, count in counter.items():
            for category, labels in EMOTION_CATEGORIES.items():
                if emotion.lower() in labels:
                    category_scores[category] += count
                    break
        dominant_category = max(category_scores, key=category_scores.get)

    category_phrases = {
        "positive": "Le comportement général est plutôt positif et ouvert.",
        "negative": "Le comportement général présente des signaux de tension ou d'inconfort.",
        "neutral": "Le comportement général est neutre et contrôlé.",
    }

    # ── 3. Détection d'alternance émotionnelle ────────────────────────────────
    unique_categories_seen = set()
    for emotion in dominant_list:
        for cat, labels in EMOTION_CATEGORIES.items():
            if emotion.lower() in labels:
                unique_categories_seen.add(cat)
                break

    alternance_note = (
        " Une alternance entre des émotions de polarités différentes "
        "a été observée, ce qui peut indiquer une dissonance émotionnelle."
        if len(unique_categories_seen) >= 2
        else ""
    )

    # ── 4. Assemblage ─────────────────────────────────────────────────────────
    lines = [category_phrases[dominant_category]]

    for emotion, count in top_3:
        pct = round(count / total * 100, 1)
        template = SUMMARY_TEMPLATES.get(
            emotion, f"La personne exprime principalement l'émotion '{emotion}'."
        )
        lines.append(f"• {template} ({pct}% des frames)")

    if alternance_note:
        lines.append(alternance_note)

    top_emotion_name = top_3[0][0]
    if top_emotion_name in DERIVED_EMOTIONS:
        lines.append(
            "Note : l'emotion dominante est une valeur inferee par heuristique, "
            "non detectee directement par le modele de vision."
        )

    return "\n".join(lines)


# ── Fonction utilitaire pour le rapport ───────────────────────────────────────
def get_emotion_distribution_summary(emotion_results: List[dict]) -> dict:
    """
    Retourne un résumé statistique de la distribution émotionnelle.
    Utile pour le rapport PDF et les métriques du PFE.

    Returns:
        dict : {
            "top_emotions"        : [(émotion, count), ...],
            "category_breakdown"  : {"positive": %, "negative": %, "neutral": %},
            "total_frames"        : int,
            "dominant_emotion"    : str,
            "dominant_category"   : str,
        }
    """
    dominant_list = [
        r.get("dominant_emotion", "N/A")
        for r in emotion_results
        if r.get("dominant_emotion") not in ("N/A", None)
    ]

    if not dominant_list:
        return {}

    counter = Counter(dominant_list)
    total = len(dominant_list)

    category_counts = {"positive": 0, "negative": 0, "neutral": 0}
    for emotion, count in counter.items():
        for cat, labels in EMOTION_CATEGORIES.items():
            if emotion.lower() in labels:
                category_counts[cat] += count
                break

    category_breakdown = {
        cat: round(cnt / total * 100, 1) for cat, cnt in category_counts.items()
    }

    return {
        "top_emotions": counter.most_common(3),
        "category_breakdown": category_breakdown,
        "total_frames": total,
        "dominant_emotion": counter.most_common(1)[0][0],
        "dominant_category": max(category_counts, key=category_counts.get),
    }
