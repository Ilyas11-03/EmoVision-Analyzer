import pytest
import os
from app.report_generator import ReportGenerator, _clean

class TestReportGenerator:

    def test_clean_accents(self):
        """Nettoyage des accents français."""
        assert _clean("éàçü") == "eacu"

    def test_clean_emojis(self):
        """Nettoyage des emojis."""
        assert "[OK]" in _clean("✅ OK")
        assert "[!]" in _clean("⚠️ Attention")

    def test_json_export(self, tmp_path):
        """Export JSON sans erreur."""
        output = str(tmp_path / "report.json")
        rg = ReportGenerator(results=[], video_name="test.mp4")
        rg.to_json(output)
        assert os.path.exists(output)

    def test_csv_export(self, tmp_path):
        """Export CSV sans erreur."""
        output = str(tmp_path / "report.csv")
        rg = ReportGenerator(results=[], video_name="test.mp4")
        rg.to_csv(output)
        assert os.path.exists(output)

    def test_pdf_export(self, tmp_path):
        """Export PDF sans erreur."""
        output = str(tmp_path / "report.pdf")
        rg = ReportGenerator(results=[], video_name="test.mp4")
        rg.to_pdf(output)
        assert os.path.exists(output)