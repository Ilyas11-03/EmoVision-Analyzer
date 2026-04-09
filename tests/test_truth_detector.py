import pytest
from app.truth_detector import analyze_truth_from_stress_and_emotion

class TestTruthDetector:

    def test_low_stress_happy(self):
        """Faible stress + happy = score élevé."""
        stress = {"stress_score": 0.05, "pitch_mean": 120.0}
        result = analyze_truth_from_stress_and_emotion(stress, "happy")
        assert result["truth_score"] >= 0.7

    def test_high_stress_fear(self):
        """Stress élevé + fear = score bas."""
        stress = {"stress_score": 0.80, "pitch_mean": 300.0}
        result = analyze_truth_from_stress_and_emotion(stress, "fear")
        assert result["truth_score"] <= 0.5

    def test_disclaimer_present(self):
        """Disclaimer toujours présent."""
        stress = {"stress_score": 0.1, "pitch_mean": 150.0}
        result = analyze_truth_from_stress_and_emotion(stress, "neutral")
        assert "disclaimer" in result
        assert len(result["disclaimer"]) > 0