from typing import Optional

# ── Constantes ────────────────────────────────────────────────────────────────
# CORRECTION : seuils documentés et regroupés ici pour faciliter
# la calibration future sur un corpus annoté.

# Seuils de stress vocal (à calibrer selon ton corpus)
STRESS_THRESHOLD = 0.12   # Score de stress normalisé (issu de stress_analysis.py)
PITCH_THRESHOLD  = 250.0  # Hz — fréquence vocale anormalement élevée

# Émotions faciales considérées comme signaux de tension
SUSPECT_EMOTIONS = ["fear", "nervous", "confused", "angry", "pain", "disgust","frustated","anxious"]

# Pénalités sur le score de sincérité [0.0 – 1.0]
# CORRECTION : documentées explicitement pour justification académique
PENALTIES = {
    "emotion_suspecte": 0.30,
    "stress_eleve":     0.40,
    "pitch_eleve":      0.20,
}

# Seuils d'interprétation du score final
VERDICT_THRESHOLDS = {
    "tres_sincere":   0.80,
    "plutot_sincere": 0.50,
    "suspect":        0.30,
    # En dessous de 0.30 → tension forte détectée
}


# ── Fonction principale ───────────────────────────────────────────────────────

def analyze_truth_from_stress_and_emotion(
    stress_data:     dict,
    emotion_label:   Optional[str] = None
) -> dict:
    """
    Calcule un indicateur de sincérité basé sur la combinaison de :
    - signaux de stress vocal (stress_score, pitch_mean)
    - émotion faciale dominante

    ⚠️ AVERTISSEMENT ACADÉMIQUE :
    Ce score est un indicateur heuristique expérimental.
    Il ne constitue PAS une preuve de mensonge et ne doit pas être utilisé
    à des fins légales, disciplinaires ou décisionnelles.
    Les seuils sont empiriques et non calibrés sur un corpus annoté.

    Args:
        stress_data   : Dict issu de extract_audio_features() ou
                        extract_stress_segment() — doit contenir
                        "stress_score" et "pitch_mean".
        emotion_label : Émotion faciale dominante (primaire, issue de
                        detect_emotions_on_image()).

    Returns:
        dict : {
            "truth_score"       : float | None,  score [0.0 – 1.0]
            "verdict"           : str,
            "confidence_level"  : str,   (high / medium / low)
            "signals_detected"  : dict,  détail des signaux suspects
            "penalties_applied" : dict,  détail des pénalités
            "explanation"       : str,
            "disclaimer"        : str,   avertissement académique
        }
    """
    # ── Gestion erreur audio ──────────────────────────────────────────────────
    if "error" in stress_data:
        return _indeterminate_result(
            reason=f"Analyse audio impossible : {stress_data['error']}"
        )

    # ── Extraction des signaux ────────────────────────────────────────────────
    stress_score = float(stress_data.get("stress_score", 0.0))
    pitch_mean   = float(stress_data.get("pitch_mean",   0.0))
    emotion      = (emotion_label or "unknown").lower().strip()

    # ── Détection des signaux suspects ────────────────────────────────────────
    emotion_suspecte = emotion in SUSPECT_EMOTIONS
    stress_eleve     = stress_score > STRESS_THRESHOLD
    pitch_eleve      = pitch_mean   > PITCH_THRESHOLD

    signals_detected = {
        "emotion_suspecte": {
            "detected": emotion_suspecte,
            "value":    emotion,
            "reference": f"émotion dans {SUSPECT_EMOTIONS}",
        },
        "stress_eleve": {
            "detected": stress_eleve,
            "value":    round(stress_score, 3),
            "reference": f"> {STRESS_THRESHOLD}",
        },
        "pitch_eleve": {
            "detected": pitch_eleve,
            "value":    round(pitch_mean, 1),
            "reference": f"> {PITCH_THRESHOLD} Hz",
        },
    }

    # ── Calcul du score avec pénalités ────────────────────────────────────────
    # CORRECTION : variable renommée (accent supprimé sur pitch_élevé)
    score              = 1.0
    penalties_applied  = {}

    if emotion_suspecte:
        score -= PENALTIES["emotion_suspecte"]
        penalties_applied["emotion_suspecte"] = PENALTIES["emotion_suspecte"]

    if stress_eleve:
        score -= PENALTIES["stress_eleve"]
        penalties_applied["stress_eleve"] = PENALTIES["stress_eleve"]

    if pitch_eleve:
        score -= PENALTIES["pitch_eleve"]
        penalties_applied["pitch_eleve"] = PENALTIES["pitch_eleve"]

    # Clamp dans [0.0 – 1.0]
    score = max(0.0, min(1.0, round(score, 2)))

    # ── Verdict gradué ────────────────────────────────────────────────────────
    # CORRECTION : 4 niveaux au lieu de 4 seuils mal nommés
    if score >= VERDICT_THRESHOLDS["tres_sincere"]:
        verdict          = "Très probablement sincère"
        confidence_level = "high"
    elif score >= VERDICT_THRESHOLDS["plutot_sincere"]:
        verdict          = "Plutôt sincère"
        confidence_level = "medium"
    elif score >= VERDICT_THRESHOLDS["suspect"]:
        verdict          = "Signaux de tension détectés"
        confidence_level = "low"
    else:
        verdict          = "Tension forte détectée"
        confidence_level = "low"

    # CORRECTION : "Mensonge probable" remplacé par "Tension forte détectée"
    # — terminologie scientifiquement défendable pour un PFE.

    # ── Explication détaillée ─────────────────────────────────────────────────
    signals_list = [
        k for k, v in signals_detected.items() if v["detected"]
    ]
    if signals_list:
        signals_str = ", ".join(signals_list)
        explanation = (
            f"Signaux suspects détectés : {signals_str}. "
            f"Émotion faciale : '{emotion}', "
            f"stress vocal : {stress_score:.3f} (seuil : {STRESS_THRESHOLD}), "
            f"pitch moyen : {pitch_mean:.1f} Hz (seuil : {PITCH_THRESHOLD} Hz). "
            f"Pénalités appliquées : {sum(penalties_applied.values()):.2f}."
        )
    else:
        explanation = (
            f"Aucun signal suspect détecté. "
            f"Émotion : '{emotion}', stress : {stress_score:.3f}, "
            f"pitch : {pitch_mean:.1f} Hz."
        )

    return {
        "truth_score":       score,
        "verdict":           verdict,
        "confidence_level":  confidence_level,
        "signals_detected":  signals_detected,
        "penalties_applied": penalties_applied,
        "explanation":       explanation,
        "disclaimer":        _get_disclaimer(),
    }


# ── Analyse comparative sur plusieurs segments ────────────────────────────────
def compare_truth_segments(segments_stress: list, emotion_label: str) -> list:
    """
    Calcule l'indicateur de sincérité sur plusieurs segments temporels.
    Utile pour suivre l'évolution de la tension au fil de l'entretien.

    Args:
        segments_stress : Liste de dicts issus de compare_stress_segments(),
                          chaque dict contient {"label", "start", "end", "features"}.
        emotion_label   : Émotion faciale dominante globale.

    Returns:
        Liste de résultats d'analyse par segment.
    """
    results = []
    for seg in segments_stress:
        features = seg.get("features", {})
        analysis = analyze_truth_from_stress_and_emotion(features, emotion_label)
        results.append({
            "label":    seg.get("label", "segment"),
            "start":    seg.get("start", 0),
            "end":      seg.get("end",   0),
            "analysis": analysis,
        })
    return results


# ── Résultats standardisés ────────────────────────────────────────────────────
def _indeterminate_result(reason: str) -> dict:
    return {
        "truth_score":       None,
        "verdict":           "Indéterminé",
        "confidence_level":  "none",
        "signals_detected":  {},
        "penalties_applied": {},
        "explanation":       reason,
        "disclaimer":        _get_disclaimer(),
    }


def _get_disclaimer() -> str:
    return (
        "⚠️ Ce score est un indicateur heuristique expérimental basé sur des "
        "signaux de stress vocal et facial. Il ne constitue pas une preuve de "
        "mensonge et ne doit en aucun cas être utilisé à des fins légales, "
        "disciplinaires ou décisionnelles. Les seuils utilisés sont empiriques "
        "et nécessitent une calibration sur un corpus annoté pour être validés."
    )