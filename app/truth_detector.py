def analyze_truth_from_stress_and_emotion(stress_data, emotion_label):
    """
    Détermine un score de sincérité basé sur :
    - stress vocal (stress_score, pitch)
    - émotion dominante faciale (ex: 'fear', 'nervous', 'happy')
    """

    if "error" in stress_data:
        return {
            "truth_score": None,
            "verdict": "Indéterminé",
            "explanation": f"Analyse audio impossible : {stress_data['error']}"
        }

    stress = stress_data.get("stress_score", 0)
    pitch = stress_data.get("pitch_mean", 0)

    emotion = emotion_label.lower() if emotion_label else "unknown"

    # Règles simples pour détecter des signes de stress ou de tension
    emotion_suspecte = emotion in ["fear", "nervous", "confused", "angry", "pain"]
    stress_eleve = stress > 0.12
    pitch_élevé = pitch > 160  # fréquence vocale anormalement tendue

    # Combinaison : plus il y a de signaux suspects, plus la sincérité baisse
    score = 1.0
    if emotion_suspecte:
        score -= 0.3
    if stress_eleve:
        score -= 0.4
    if pitch_élevé:
        score -= 0.2

    score = max(0.0, min(1.0, round(score, 2)))  # Clamp 0.0 – 1.0

    # Interprétation
    if score >= 0.8:
        verdict = "Très probablement sincère"
    elif score >= 0.5:
        verdict = "Plutôt sincère"
    elif score >= 0.3:
        verdict = "Probablement pas sincère"
    else:
        verdict = "Mensonge probable"

    return {
        "truth_score": score,
        "verdict": verdict,
        "explanation": f"Emotion : {emotion}, Stress : {stress:.3f}, Pitch : {pitch:.1f} Hz"
    }
