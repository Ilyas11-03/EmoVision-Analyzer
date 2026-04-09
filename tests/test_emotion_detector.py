import pytest
from app.emotion_detector import detect_emotions_on_image, _empty_result

class TestEmotionDetector:

    def test_empty_result_structure(self):
        """Vérifie la structure du résultat vide."""
        result = _empty_result("test.jpg", "No face")
        assert result["frame"] == "test.jpg"
        assert result["dominant_emotion"] == "N/A"
        assert result["emotions"] == {}
        assert result["derived_emotions"] == {}
        assert result["is_suspect"] == False

    def test_invalid_image_returns_empty(self):
        """Une image inexistante retourne un résultat vide."""
        result = detect_emotions_on_image("inexistant.jpg")
        assert result["dominant_emotion"] == "N/A"
        assert "error" in result