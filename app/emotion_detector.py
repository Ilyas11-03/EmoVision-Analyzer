from deepface import DeepFace  # Importation de la bibliothèque DeepFace pour l'analyse des émotions

def detect_emotions_on_image(image_path):
    try:
        # Analyse l'image pour détecter les émotions, sans forcer la détection d'un visage
        result = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
        if isinstance(result, list) and len(result) > 0:  # Vérifie si le résultat est une liste non vide
            res = result[0]  # Prend le premier résultat de la liste
            emotions = res.get("emotion", {})

            #Ajout d'émotions dérivées
            emotions["excited"] = round(emotions.get("happy",0) * 0.6, 2)
            emotions["bored"] = round(emotions.get("sad",0) * 0.5, 2)
            emotions["confused"] = round(emotions.get("neutral",0)* 0.4, 2)

            dominant_emotion = max(emotions, key=emotions.get)
            return {
                 "frame": image_path.split("/")[-1],
                "dominant_emotion": dominant_emotion,
                "emotions": emotions
            }
        # Si aucun résultat, retourne des valeurs par défaut
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}}
    except Exception as e:
        # En cas d'erreur, retourne les valeurs par défaut et le message d'erreur
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}, "error": str(e)}