from deepface import DeepFace  # Importation de la bibliothèque DeepFace pour l'analyse des émotions

def detect_emotions_on_image(image_path):
    try:
        # Analyse l'image pour détecter les émotions, sans forcer la détection d'un visage
        result = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
        if isinstance(result, list) and len(result) > 0:  # Vérifie si le résultat est une liste non vide
            res = result[0]  # Prend le premier résultat de la liste
            return {
                "frame": image_path.split("/")[-1],  # Nom du fichier image
                "dominant_emotion": res.get("dominant_emotion", "N/A"),  # Récupère l'émotion dominante, "N/A" si absente
                "emotions": res.get("emotion", {})  # Récupère le score de chaque émotion, dictionnaire vide si absent
            }
        # Si aucun résultat, retourne des valeurs par défaut
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}}
    except Exception as e:
        # En cas d'erreur, retourne les valeurs par défaut et le message d'erreur
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}, "error": str(e)}