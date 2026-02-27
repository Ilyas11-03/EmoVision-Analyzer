import os
from app.video_processing import extract_frames
from app.emotion_detector import detect_emotions_on_image
from app.emotion_utils import get_top_emotion_frames
from app.stress_analysis import extract_audio_features, extract_stress_segment
from app.qa_analyzer import analyze_qa_relevance
from app.speech_to_text import transcribe_audio_whisper
from app.truth_detector import analyze_truth_from_stress_and_emotion

# Dossier temporaire pour stocker les frames extraites
TEMP_FRAMES_FOLDER = "temp_frames"

# Pipeline principal — orchestre toutes les analyses (faciale, vocale, transcription, Q/R, sincérité) et retourne un dict complet des résultats
def analyze_video(video_path: str, question: str = None, response: str = None,
                  start_time: float = None, end_time: float = None) -> dict:
    """
    Pipeline complet d'analyse comportementale d'une vidéo.

    Args:
        video_path  : Chemin vers la vidéo à analyser.
        question    : Question posée à l'interviewé (pour l'analyse Q/R).
        response    : Réponse transcrite ou saisie manuellement.
        start_time  : Début du segment à analyser pour la sincérité (en secondes).
        end_time    : Fin du segment à analyser pour la sincérité (en secondes).

    Returns:
        dict : Résultats complets de l'analyse.
    """

    # ── 1. Extraction et analyse des frames ──────────────────────────────────
    frame_paths = extract_frames(video_path, output_folder=TEMP_FRAMES_FOLDER)
    # BUG CORRIGÉ : on accumule tous les résultats dans une liste,
    # puis on appelle get_top_emotion_frames UNE FOIS sur la liste complète.
    emotion_results = []
    for frame_path in frame_paths:
        result = detect_emotions_on_image(frame_path)
        emotion_results.append(result)

    top_frames = get_top_emotion_frames(emotion_results)

    # Émotion dominante globale (pour le truth detector)
    dominant_emotions = [
        r.get("dominant_emotion", "neutral")
        for r in emotion_results
        if r.get("dominant_emotion") not in ("N/A", None)
    ]
    global_dominant_emotion = (
        max(set(dominant_emotions), key=dominant_emotions.count)
        if dominant_emotions else "neutral"
    )

    # ── 2. Analyse du stress vocal ────────────────────────────────────────────
    # BUG CORRIGÉ : on utilise le segment si fourni, sinon toute la vidéo.
    if start_time is not None and end_time is not None:
        stress = extract_stress_segment(video_path, start_time, end_time)
    else:
        stress = extract_audio_features(video_path)

    # ── 3. Transcription audio ────────────────────────────────────────────────
    # BUG CORRIGÉ : le modèle Whisper est chargé une seule fois via le cache
    # défini dans speech_to_text.py (voir correction de ce fichier).
    transcript = transcribe_audio_whisper(video_path)

    # ── 4. Analyse Q/R ────────────────────────────────────────────────────────
    # BUG CORRIGÉ : analyze_qa_relevance attend (question, response),
    # pas seulement la transcription.
    qa_result = None
    if question and response:
        qa_result = analyze_qa_relevance(question, response)
    elif question and transcript:
        # Fallback : on utilise la transcription comme réponse
        qa_result = analyze_qa_relevance(question, transcript)

    # ── 5. Détection de sincérité ─────────────────────────────────────────────
    # BUG CORRIGÉ : analyze_truth_from_stress_and_emotion attend
    # (stress_data: dict, emotion_label: str), pas (video_path, start, end).
    truth = analyze_truth_from_stress_and_emotion(stress, global_dominant_emotion)

    return {
        "emotion_results": emotion_results,       # Détail frame par frame
        "top_emotion_frames": top_frames,          # Frames les plus expressives
        "global_dominant_emotion": global_dominant_emotion,
        "stress_analysis": stress,
        "transcript": transcript,
        "qa_analysis": qa_result,
        "truth_analysis": truth,
    }