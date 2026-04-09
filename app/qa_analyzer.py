import threading
from typing import Optional
from sentence_transformers import SentenceTransformer, util

# ── Chargement du modèle (singleton thread-safe) ──────────────────────────────

_model_lock = threading.Lock()
_model_cache: Optional[SentenceTransformer] = None

# ── Seuils de pertinence ──────────────────────────────────────────────────────
# CORRECTION : déplacés AVANT _get_confidence_level() qui les utilise

THRESHOLDS = {
    "high": 0.70,
    "medium": 0.50,
    "low": 0.30,
}


# ── Fonctions internes ────────────────────────────────────────────────────────


def _get_model() -> SentenceTransformer:
    """Retourne le modèle en cache, ou le charge si nécessaire."""
    global _model_cache
    if _model_cache is None:
        with _model_lock:
            if _model_cache is None:
                _model_cache = SentenceTransformer(
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
    return _model_cache


def _get_confidence_level(similarity_score: float, threshold: float) -> tuple:
    """
    Détermine le niveau de confiance et le verdict selon le score de similarité.
    Extrait de analyze_qa_relevance() — suggestion Sourcery (extract-method).

    Returns:
        tuple : (verdict, confidence_level, is_relevant)
    """
    if similarity_score >= THRESHOLDS["high"]:
        verdict, confidence_level = "Tres pertinente [OK]", "high"
    elif similarity_score >= THRESHOLDS["medium"]:
        verdict, confidence_level = "Partiellement pertinente [~]", "medium"
    elif similarity_score >= THRESHOLDS["low"]:
        verdict, confidence_level = "Faiblement liee [/]", "low"
    else:
        verdict, confidence_level = "Hors sujet [X]", "off-topic"

    return verdict, confidence_level, similarity_score >= threshold


def _error_result(reason: str) -> dict:
    """Résultat d'erreur standardisé."""
    return {
        "question": "",
        "response": "",
        "similarity_score": 0.0,
        "verdict": "Erreur [X]",
        "confidence_level": "none",
        "explanation": reason,
        "is_relevant": False,
        "error": reason,
    }


# Fonction extraite (suggérée par Sourcery)
def _compute_similarity(question: str, response: str) -> float:
    """
    Encode question et réponse et calcule la similarité cosinus.
    Extrait de analyze_qa_relevance() — suggestion Sourcery (extract-method).

    Args:
        question : Question nettoyée.
        response : Réponse nettoyée.

    Returns:
        float : Score de similarité cosinus arrondi à 3 décimales.
    """
    model = _get_model()
    embeddings = model.encode([question, response], convert_to_tensor=True)
    return round(float(util.cos_sim(embeddings[0], embeddings[1]).item()), 3)


# ── Fonction principale ───────────────────────────────────────────────────────


# Fonction principale simplifiée
def analyze_qa_relevance(
    question: str, response: str, threshold: float = THRESHOLDS["medium"]
) -> dict:
    """
    Analyse la pertinence sémantique d'une réponse par rapport à une question.

    Args:
        question  : La question posée à l'interviewé.
        response  : La réponse donnée.
        threshold : Seuil de pertinence (défaut : 0.50).

    Returns:
        dict : Résultat complet de l'analyse de pertinence.
    """
    if not question or not question.strip():
        return _error_result("La question est vide ou manquante.")
    if not response or not response.strip():
        return _error_result("La reponse est vide ou manquante.")

    try:
        # CORRECTION Sourcery : encodage extrait dans _compute_similarity()
        similarity_score = _compute_similarity(question.strip(), response.strip())

        verdict, confidence_level, is_relevant = _get_confidence_level(
            similarity_score, threshold
        )

        explanation = (
            f"La similarite semantique entre la question et la reponse est de "
            f"{similarity_score:.2f} (seuil : {threshold}). "
            f"Niveau de confiance : {confidence_level}. "
            f"La reponse est jugee "
            f"{'pertinente' if is_relevant else 'non pertinente'} "
            f"par rapport a la question posee."
        )

        return {
            "question": question.strip(),
            "response": response.strip(),
            "similarity_score": similarity_score,
            "verdict": verdict,
            "confidence_level": confidence_level,
            "explanation": explanation,
            "is_relevant": is_relevant,
        }

    except Exception as e:
        return _error_result(str(e))


# ── Analyse de plusieurs paires Q/R ──────────────────────────────────────────


def analyze_multiple_qa(pairs: list, threshold: float = THRESHOLDS["medium"]) -> list:
    """
    Analyse une liste de paires question/réponse.

    Args:
        pairs     : Liste de dicts [{"question": str, "response": str}, ...]
        threshold : Seuil de pertinence commun.

    Returns:
        Liste de résultats issus de analyze_qa_relevance().
    """
    return [
        analyze_qa_relevance(
            pair.get("question", ""), pair.get("response", ""), threshold
        )
        for pair in pairs
    ]


# ── Score de cohérence globale Q/R ───────────────────────────────────────────
def get_qa_coherence_score(qa_results: list) -> dict:
    """
    Calcule un score de cohérence globale à partir de plusieurs analyses Q/R.

    Args:
        qa_results : Liste de résultats issus de analyze_qa_relevance().

    Returns:
        dict : {
            "mean_similarity"  : float,
            "coherence_score"  : float,
            "relevant_count"   : int,
            "total_count"      : int,
            "relevance_rate"   : float (%),
            "interpretation"   : str,
        }
    """
    valid = [r for r in qa_results if "error" not in r]

    if not valid:
        return {"error": "Aucun resultat valide a analyser."}

    scores = [r["similarity_score"] for r in valid]
    mean_sim = round(sum(scores) / len(scores), 3)
    relevant = sum(bool(r.get("is_relevant")) for r in valid)
    total = len(valid)
    relevance_rate = round(relevant / total * 100, 1)

    if mean_sim >= THRESHOLDS["high"]:
        interpretation = (
            "Les reponses sont globalement tres coherentes avec les questions."
        )
    elif mean_sim >= THRESHOLDS["medium"]:
        interpretation = (
            "Les reponses sont partiellement coherentes — quelques ecarts notables."
        )
    else:
        interpretation = (
            "Les reponses presentent une faible coherence avec les questions posees."
        )

    return {
        "mean_similarity": mean_sim,
        "coherence_score": mean_sim,
        "relevant_count": relevant,
        "total_count": total,
        "relevance_rate": relevance_rate,
        "interpretation": interpretation,
    }
