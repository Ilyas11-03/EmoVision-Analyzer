from deepface import DeepFace

def detect_emotions_on_image(image_path):
    try:
        result = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
        if isinstance(result, list) and len(result) > 0:
            res = result[0]
            return {
                "frame": image_path.split("/")[-1],
                "dominant_emotion": res.get("dominant_emotion", "N/A"),
                "emotions": res.get("emotion", {})
            }
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}}
    except Exception as e:
        return {"frame": image_path.split("/")[-1], "dominant_emotion": "N/A", "emotions": {}, "error": str(e)}