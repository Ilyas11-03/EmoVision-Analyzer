from collections import Counter  # Importe Counter pour compter les émotions

# Catégories des émotions regroupées par type
EMOTION_CATEGORIES = {
     "positive": ["happy", "excited", "smile", "laughter"],  # Émotions positives
     "negative": ["angry", "fear", "disgust", "sad", "nervous", "pain", "hate"],  # Émotions négatives
     "neutral": ["neutral", "confused", "surprise", "bored", "obligated"]  # Émotions neutres
}

# Fonction pour obtenir les frames les plus expressives
# Retourne les 3–5 frames ayant le score émotionnel le plus élevé
def get_top_emotion_frames(results, top_n=5):
    """
    Retourne les frames ayant le plus fort score émotionnel.
    """
    scored = []  # Liste pour stocker les frames et leur score
    for item in results:  # Parcourt chaque résultat
        emotions = item.get("emotions", {})  # Récupère le dictionnaire des émotions pour la frame
        if emotions:  # Vérifie si des émotions sont présentes
            max_score = max(emotions.values())  # Prend le score maximal parmi les émotions
            scored.append({
                "frame": item.get("frame", "unknown"),  # Nom ou numéro de la frame
                "dominant_emotion": item.get("dominant_emotion", "N/A"),  # Émotion dominante détectée
                "intensity": round(max_score, 2)  # Intensité de l'émotion dominante, arrondie à 2 décimales
            })
    return sorted(scored, key=lambda x: x["intensity"], reverse=True)[:top_n]  # Trie et retourne les frames les plus intenses

# Fonction pour obtenir les émotions dominantes les plus fréquentes
# Utilisée pour la section "Top émotions dominantes" du PDF
def get_dominant_emotion_stats(results, top_n=3):
    """
    Retourne les émotions dominantes les plus fréquentes (statistiques globales).
    """
    dominant_list = [item.get("dominant_emotion", "N/A") for item in results]  # Liste des émotions dominantes pour chaque frame
    counter = Counter(dominant_list)  # Compte la fréquence de chaque émotion
    return counter.most_common(top_n)  # Retourne les top_n émotions les plus fréquentes

# Fonction pour classifier les émotions en 3 grandes familles
# Regroupe les scores détaillés en catégories principales
def normalize_emotions(emotions_dict):
    """
    Regroupe les émotions détaillées en trois grandes catégories : positive, negative, neutral.
    """
    normalized = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}  # Initialise les scores pour chaque catégorie
    for emotion, score in emotions_dict.items():  # Parcourt chaque émotion et son score
        for category, labels in EMOTION_CATEGORIES.items():  # Parcourt chaque catégorie et ses labels
            if emotion.lower() in labels:  # Vérifie si l'émotion appartient à la catégorie
                normalized[category] += score  # Ajoute le score à la catégorie correspondante
                break  # Passe à l'émotion suivante
    return normalized  # Retourne le dictionnaire des scores par catégorie