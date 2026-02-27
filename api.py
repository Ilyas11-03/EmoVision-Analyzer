from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil, os, uuid
from app.video_processing import extract_frames, get_video_info
from app.emotion_detector import detect_emotions_on_image
from app.emotion_utils import (
    get_top_emotion_frames,
    get_emotion_category_breakdown,
    detect_emotional_dissonance,
)
from app.behavior_summary import generate_behavior_summary
from app.stress_analysis import extract_audio_features, extract_stress_segment
from app.truth_detector import analyze_truth_from_stress_and_emotion
from app.speech_to_text import transcribe_video
from app.qa_analyzer import analyze_qa_relevance
from app.report_generator import ReportGenerator

app = FastAPI(title="Analyse Comportementale API")

# ── CORS : autorise React (port 3000) à appeler l'API ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR  = "uploads"
FRAMES_DIR  = "temp_frames"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Route 1 : Upload vidéo ────────────────────────────────────────────────────
@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Reçoit la vidéo uploadée depuis React,
    la sauvegarde et retourne un video_id unique.
    """
    video_id   = str(uuid.uuid4())
    video_path = os.path.join(UPLOAD_DIR, f"{video_id}.mp4")

    with open(video_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    info = get_video_info(video_path)

    return {
        "video_id":   video_id,
        "video_info": info,
    }


# ── Route 2 : Analyse faciale ─────────────────────────────────────────────────
@app.post("/api/analyze/emotions/{video_id}")
async def analyze_emotions(
    video_id:   str,
    fps:        float = 0.5,
    max_frames: int   = 100
):
    video_path  = os.path.join(UPLOAD_DIR, f"{video_id}.mp4")
    frames_dir  = os.path.join(FRAMES_DIR, video_id)
    frame_paths = extract_frames(video_path, frames_dir,
                                 fps=fps, max_frames=max_frames)

    results = [detect_emotions_on_image(p) for p in frame_paths]

    return {
        "emotion_results":    results,
        "top_frames":         get_top_emotion_frames(results),
        "category_breakdown": get_emotion_category_breakdown(results),
        "dissonance":         detect_emotional_dissonance(results),
        "behavior_summary":   generate_behavior_summary(results),
    }


# ── Route 3 : Analyse vocale ──────────────────────────────────────────────────
@app.post("/api/analyze/stress/{video_id}")
async def analyze_stress(video_id: str):
    video_path = os.path.join(UPLOAD_DIR, f"{video_id}.mp4")
    return extract_audio_features(video_path)


# ── Route 4 : Analyse segment sincérité ──────────────────────────────────────
@app.post("/api/analyze/truth/{video_id}")
async def analyze_truth(
    video_id:  str,
    start_sec: float = 0,
    end_sec:   float = 10,
    emotion:   str   = "neutral"
):
    video_path   = os.path.join(UPLOAD_DIR, f"{video_id}.mp4")
    stress_data  = extract_stress_segment(video_path, start_sec, end_sec)
    return analyze_truth_from_stress_and_emotion(stress_data, emotion)


# ── Route 5 : Transcription + Q/R ────────────────────────────────────────────
@app.post("/api/analyze/qa/{video_id}")
async def analyze_qa(
    video_id: str,
    question: str = Form(...)
):
    video_path = os.path.join(UPLOAD_DIR, f"{video_id}.mp4")
    transcript = transcribe_video(video_path)
    qa_result  = analyze_qa_relevance(question, transcript)
    return {
        "transcript": transcript,
        "qa_result":  qa_result,
    }


# ── Route 6 : Génération rapport PDF ─────────────────────────────────────────
@app.post("/api/report/{video_id}")
async def generate_report(video_id: str, payload: dict):
    output_path = os.path.join(UPLOAD_DIR, f"{video_id}_report.pdf")

    report = ReportGenerator(
        results            = payload.get("emotion_results", []),
        video_name         = f"{video_id}.mp4",
        voice_results      = payload.get("voice_results", {}),
        top_emotion_frames = payload.get("top_frames", []),
        behavior_summary   = payload.get("behavior_summary", ""),
        truth_analysis     = payload.get("truth_analysis", {}),
        qa_analysis        = payload.get("qa_analysis", {}),
        dissonance         = payload.get("dissonance", {}),
        category_breakdown = payload.get("category_breakdown", {}),
    )
    report.to_pdf(output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="rapport_analyse.pdf"
    )