from app.video_processing import extract_frames
from app.emotion_detector import detect_emotions_on_image
from app.emotion_utils import get_top_emotion_frames
from app.stress_analysis import extract_audio_features
from app.qa_analyzer import analyze_qa_relevance
from app.speech_to_text import transcribe_audio_whisper
from app.truth_detector import analyze_truth_from_stress_and_emotion

def analyze_video(video_path: str, start_time=None, end_time=None) -> dict:
   
    # Émotions
    frames = extract_frames(video_path)
    emotions = []
    for frame in frames:
        result = detect_emotions_on_image(frame)
        emotions.append(get_top_emotion_frames(result))

    # Stress vocal
    stress = extract_audio_features(video_path)

    # Transcription et QA
    transcript = transcribe_audio_whisper(video_path)
    qa_pairs = analyze_qa_relevance(transcript)

    # Détection de vérité (si l'intervalle est fourni)
    truth = None
    if start_time and end_time:
        truth = analyze_truth_from_stress_and_emotion(video_path, start_time, end_time)

    return {
        "emotion_analysis": emotions,
        "stress_analysis": stress,
        "transcript": transcript,
        "qa_analysis": qa_pairs,
        "truth_analysis": truth
    }
