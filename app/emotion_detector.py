from deepface import DeepFace  # Importation de la bibliothèque DeepFace pour l'analyse des émotions

def detect_emotions_on_image(image_path):

    try:
        # Analyse l'image pour détecter les émotions, sans forcer la détection d'un visage
        result = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
        if isinstance(result, list) and len(result) > 0:  # Vérifie si le résultat est une liste non vide
            res = result[0]  # Prend le premier résultat de la liste
            emotions = res.get("emotion", {}) # Récupère le dictionnaire des scores d'émotions

            #Ajout d'émotions dérivées
            emotions["excited"] = round(emotions.get("happy",0) * 0.6, 2) # Calcule 'excited' à partir de 'happy'
            emotions["bored"] = round(emotions.get("sad",0) * 0.5, 2) # Calcule 'bored' à partir de 'sad'
            emotions["confused"] = round(emotions.get("neutral",0)* 0.4, 2) # Calcule 'confused' à partir de 'neutral'
            emotions["silly"] = round(emotions.get("happy", 0) * 0.3 + emotions.get("surprise", 0) * 0.2, 2) # Calcule 'silly' à partir de 'happy' et 'surprise'
            emotions["nervous"] = round(emotions.get("fear", 0) * 0.6 + emotions.get("surprise", 0) * 0.2, 2) # Calcule 'nervous' à partir de 'fear' et 'surprise'

            dominant_emotion = max(emotions, key=emotions.get) # Détermine l'émotion dominante (score le plus élevé)
            return {
                 "frame":  image_path.split("/")[-1] if "/" in image_path else image_path.split("\\")[-1],  # Récupère le nom de la frame depuis le chemin
                "dominant_emotion": dominant_emotion, # Émotion dominante détectée
                "emotions": emotions # Dictionnaire des scores d'émotions
            }
        # Si aucun résultat, retourne des valeurs par défaut
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}}
    except Exception as e:
        # En cas d'erreur, retourne les valeurs par défaut et le message d'erreur
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}, "error": str(e)}
    