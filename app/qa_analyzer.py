# Importe les classes SentenceTransformer et util de la bibliothèque sentence_transformers.
from sentence_transformers import SentenceTransformer, util

# Chargement du modèle de similarité sémantique
# 'paraphrase-multilingual-MiniLM-L12-v2' est un modèle pré-entraîné efficace pour comparer des textes dans plusieurs langues.
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2') 

# Définit la fonction pour analyser la pertinence d'une réponse par rapport à une question.
def analyze_qa_relevance(question: str, response: str, threshold: float = 0.5) -> dict:
    """
    Analyse si la réponse est pertinente par rapport à la question.

    Args:
        question (str): La question posée.
        response (str): La réponse donnée.
        threshold (float): Le seuil de pertinence (entre 0 et 1) pour juger si la réponse est pertinente.

    Returns:
        dict: Dictionnaire contenant le score de similarité, un verdict et une explication.
    """
    # Convertit la question et la réponse en vecteurs numériques (embeddings) que le modèle peut comprendre.
    embeddings = model.encode([question, response], convert_to_tensor=True)
    # Calcule la similarité cosinus entre les deux vecteurs. .item() extrait la valeur numérique du tenseur.
    similarity_score = util.cos_sim(embeddings[0], embeddings[1]).item()

    # Détermine si la réponse est "Pertinente" ou "Hors sujet" en comparant le score au seuil.
    verdict = "Pertinente ✅" if similarity_score >= threshold else "Hors sujet ❌"
    # Crée une phrase d'explication dynamique basée sur le score de similarité.
    explanation = f"La similarité est de {similarity_score:.2f}, ce qui indique que la réponse est {'pertinente' if similarity_score >= threshold else 'hors sujet'}."

    # Retourne un dictionnaire structuré avec les résultats de l'analyse.
    return {
        "similarity_score": round(similarity_score, 2), # Le score de similarité arrondi à 2 décimales.
        "verdict": verdict, # Le verdict final.
        "explanation": explanation # L'explication textuelle.
    }
