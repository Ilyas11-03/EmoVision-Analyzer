import pytest
import os
from app.stress_analysis import extract_stress_segment

class TestStressAnalysis:

    def test_invalid_segment(self, tmp_path):
        """Segment invalide retourne une erreur."""
        result = extract_stress_segment("video.mp4", 10, 5)
        assert "error" in result
        assert "Segment invalide" in result["error"]

    def test_missing_video(self):
        """Vidéo inexistante lève FileNotFoundError."""
        from app.stress_analysis import extract_audio_segment
        with pytest.raises(FileNotFoundError):
            extract_audio_segment("inexistant.mp4", "out.wav")