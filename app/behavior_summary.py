from collections import Counter  # Importe Counter pour compter les émotions dominantes

# Fonction qui génère un résumé du comportement émotionnel à partir des frames les plus expressives
def generate_behavior_summary(top_frames):
    """
    Génère une phrase résumant le comportement émotionnel général
    à partir des frames les plus expressives (top_frames).
    """
    if not top_frames:  # Vérifie si la liste des frames est vide
        return "Aucune émotion détectée de manière significative dans la vidéo."  # Retourne un message si aucune frame expressive
    dominant_emotions = [f["dominant_emotion"] for f in top_frames if f.get("dominant_emotion") != "N/A"]  # Extrait les émotions dominantes sauf 'N/A'
    if not dominant_emotions:  # Vérifie si aucune émotion dominante n'a été trouvée
        return "Le visage semble neutre ou difficile à analyser émotionnellement."  # Retourne un message si aucune émotion détectée

    counts = Counter(dominant_emotions)  # Compte la fréquence de chaque émotion dominante
    most_common = counts.most_common(1)[0]  # Récupère l'émotion la plus fréquente et son nombre d'occurrences

    emotion = most_common[0]  # Récupère le nom de l'émotion dominante
    count = most_common[1]  # Récupère le nombre d'occurrences de cette émotion

    # Modèles de phrases simples pour chaque émotion
    summary_templates = {
        "happy": "La personne montre des signes de joie ou d'excitation.",  # Phrase pour l'émotion 'happy'
        "sad": "La personne paraît triste ou mélancolique.",  # Phrase pour l'émotion 'sad'
        "angry": "La personne manifeste de l'agacement ou de la colère.",  # Phrase pour l'émotion 'angry'
        "fear": "La personne semble inquiet ou effrayé.",  # Phrase pour l'émotion 'fear'
        "neutral": "La personne semble calme ou indifférent.",  # Phrase pour l'émotion 'neutral'
        "surprise": "La personne réagit de manière étonnée ou inattendue.",  # Phrase pour l'émotion 'surprise'
        "confused": "La personne paraît désorienté ou indécis.",  # Phrase pour l'émotion 'confused'
        "nervous": "La personne semble stressé ou tendu.",  # Phrase pour l'émotion 'nervous'
        "excited": "La personne montre de l'enthousiasme ou de l'énergie.",  # Phrase pour l'émotion 'excited'
        "bored": "La personne semble peu impliqué ou désintéressé.",  # Phrase pour l'émotion 'bored'
        "silly": "La personne adopte une attitude légère ou exagérée.",  # Phrase pour l'émotion 'silly'
        "pain": "La personne manifeste un inconfort ou une douleur.",  # Phrase pour l'émotion 'pain'
        "hate": "La personne présente des signes de rejet ou de mépris.",  # Phrase pour l'émotion 'hate'
        "smile": "La personne affiche des sourires fréquents.",  # Phrase pour l'émotion 'smile'
        "laughter": "La personne rit fréquemment ou semble très détendu."  # Phrase pour l'émotion 'laughter'
    }

    phrase = summary_templates.get(emotion, f"La personne exprime principalement l’émotion '{emotion}'.")  # Sélectionne la phrase correspondant à l'émotion dominante
    return f"{phrase} (dominante dans {count} frame(s) expressive(s))."  # Retourne le résumé avec le nombre de frames où l'émotion est dominante