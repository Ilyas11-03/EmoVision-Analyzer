import pytest
from app.qa_analyzer import analyze_qa_relevance, _error_result

class TestQAAnalyzer:

    def test_empty_question(self):
        """Question vide retourne une erreur."""
        result = analyze_qa_relevance("", "Une réponse")
        assert "error" in result
        assert result["is_relevant"] == False

    def test_empty_response(self):
        """Réponse vide retourne une erreur."""
        result = analyze_qa_relevance("Une question", "")
        assert "error" in result

    def test_similar_texts(self):
        """Textes similaires ont un score élevé."""
        result = analyze_qa_relevance(
            "Parlez-moi de votre expérience professionnelle",
            "J'ai travaillé pendant 5 ans dans le domaine informatique"
        )
        assert result["similarity_score"] > 0.3
        assert "error" not in result

    def test_error_result_structure(self):
        """Structure du résultat d'erreur."""
        result = _error_result("Test erreur")
        assert result["similarity_score"] == 0.0
        assert result["is_relevant"] == False
        assert result["error"] == "Test erreur"