import sys
import os
import altair as alt
import pandas as pd
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.video_processing import extract_frames, clear_frames, get_video_info
from app.emotion_detector import detect_emotions_on_image
from app.emotion_utils import (
    get_top_emotion_frames,
    get_emotion_category_breakdown,
    detect_emotional_dissonance,
)
from app.behavior_summary import generate_behavior_summary, get_emotion_distribution_summary
from app.stress_analysis import extract_audio_features, extract_stress_segment
from app.truth_detector import analyze_truth_from_stress_and_emotion
from app.speech_to_text import transcribe_video
from app.qa_analyzer import analyze_qa_relevance
from app.report_generator import ReportGenerator

# ── Configuration de la page ──────────────────────────────────────────────────

st.set_page_config(
    page_title="Analyse Comportementale",
    page_icon="🎭",
    layout="wide"
)

TEMP_VIDEO   = "temp_video.mp4"
TEMP_FRAMES  = "temp_frames"
REPORT_CSV   = "report_summary.csv"
REPORT_JSON  = "report.json"
REPORT_PDF   = "report.pdf"


# ── Utilitaires ───────────────────────────────────────────────────────────────

def cleanup_temp_files():
    """Supprime les fichiers temporaires entre deux analyses."""
    clear_frames(TEMP_FRAMES)
    for f in [TEMP_VIDEO, REPORT_CSV, REPORT_JSON, REPORT_PDF]:
        if os.path.exists(f):
            os.remove(f)


def save_uploaded_video(uploaded_file) -> str:
    """Sauvegarde la vidéo uploadée dans un fichier temporaire."""
    with open(TEMP_VIDEO, "wb") as f:
        f.write(uploaded_file.read())
    return TEMP_VIDEO


# ── Section : Analyse faciale ─────────────────────────────────────────────────

def run_facial_analysis(video_path: str, fps: float) -> list:
    """
    Extrait les frames et détecte les émotions.
    CORRECTION : utilise les chemins retournés par extract_frames()
    au lieu de relire le dossier avec os.listdir().
    """
    with st.spinner("Extraction des frames..."):
        frame_paths = extract_frames(video_path, TEMP_FRAMES, fps=fps)

    if not frame_paths:
        st.error("Aucune frame extraite. Vérifiez la vidéo uploadée.")
        return []

    st.info(f"{len(frame_paths)} frame(s) extraite(s) — détection des émotions en cours...")

    results = []
    progress = st.progress(0)

    for i, frame_path in enumerate(frame_paths):
        res = detect_emotions_on_image(frame_path)
        results.append(res)
        progress.progress((i + 1) / len(frame_paths))

    progress.empty()
    st.success(f"Détection faciale terminée — {len(results)} frame(s) analysée(s).")
    return results


# ── Section : Analyse vocale ──────────────────────────────────────────────────

def run_vocal_analysis(video_path: str) -> dict:
    with st.spinner("Analyse vocale en cours..."):
        voice_results = extract_audio_features(video_path)

    if "error" in voice_results:
        st.warning(f"Analyse vocale : {voice_results['error']}")
    else:
        st.success("Analyse vocale terminée.")

    return voice_results


# ── Section : Sincérité ───────────────────────────────────────────────────────

def run_truth_analysis(video_path: str, top_emotion_frames: list) -> dict:
    """
    CORRECTION : les inputs start_sec / end_sec sont validés
    avant l'appel à extract_stress_segment().
    """
    st.subheader("🔍 Analyse de sincérité sur un segment")

    col1, col2 = st.columns(2)
    with col1:
        start_sec = st.number_input("Début du segment (secondes)", min_value=0, value=0)
    with col2:
        end_sec = st.number_input("Fin du segment (secondes)", min_value=1, value=10)

    # CORRECTION : validation avant appel
    if end_sec <= start_sec:
        st.error("La fin du segment doit être supérieure au début.")
        return {}

    with st.spinner("Analyse du stress vocal sur le segment..."):
        truth_stress = extract_stress_segment(video_path, start_sec, end_sec)

    base_emotion = (
        top_emotion_frames[0]["dominant_emotion"]
        if top_emotion_frames else "neutral"
    )
    truth_analysis = analyze_truth_from_stress_and_emotion(truth_stress, base_emotion)

    # Affichage
    score   = truth_analysis.get("truth_score", "N/A")
    verdict = truth_analysis.get("verdict", "Indéterminé")

    # CORRECTION : indicateur visuel selon le score
    if isinstance(score, float):
        if score >= 0.8:
            st.success(f"**{verdict}** (score : {score})")
        elif score >= 0.5:
            st.info(f"**{verdict}** (score : {score})")
        else:
            st.warning(f"**{verdict}** (score : {score})")
    else:
        st.info(f"**{verdict}**")

    st.caption(truth_analysis.get("explanation", ""))

    # Avertissement académique
    st.caption(truth_analysis.get("disclaimer", ""))

    return truth_analysis


# ── Section : Analyse Q/R ─────────────────────────────────────────────────────

def run_qa_analysis(video_path: str) -> dict:
    """
    CORRECTION : la transcription n'est lancée que si une question est saisie,
    et le résultat est affiché avec les 4 niveaux de pertinence.
    """
    st.subheader("🧾 Pertinence de la réponse (Question / Réponse)")

    question = st.text_input("Question posée à l'interviewé")

    if not question:
        st.info("Saisissez une question pour lancer l'analyse de pertinence.")
        return {}

    with st.spinner("Transcription automatique en cours (Whisper)..."):
        transcript = transcribe_video(video_path)

    if not transcript:
        st.warning("Transcription vide — vérifiez la piste audio de la vidéo.")
        return {}

    st.text_area("Transcription automatique", transcript, height=100)

    relevance = analyze_qa_relevance(question, transcript)

    # CORRECTION : couleur selon le niveau de confiance
    level = relevance.get("confidence_level", "none")
    if level == "high":
        st.success(f"**{relevance['verdict']}** (similarité : {relevance['similarity_score']})")
    elif level == "medium":
        st.info(f"**{relevance['verdict']}** (similarité : {relevance['similarity_score']})")
    elif level == "low":
        st.warning(f"**{relevance['verdict']}** (similarité : {relevance['similarity_score']})")
    else:
        st.error(f"**{relevance['verdict']}** (similarité : {relevance['similarity_score']})")

    st.caption(relevance.get("explanation", ""))

    return relevance


# ── Section : Visualisations ──────────────────────────────────────────────────

def show_emotion_chart(results: list):
    """
    CORRECTION : utilise les scores primaires uniquement (clé 'emotions'),
    pas les dérivées — graphique plus fiable académiquement.
    CORRECTION : regroupement paramétrable via slider.
    """
    st.subheader("📈 Évolution des émotions par frame")

    emotion_rows = []
    for idx, r in enumerate(results):
        for emotion, score in r.get("emotions", {}).items():
            emotion_rows.append({
                "Frame":   idx,
                "Emotion": emotion,
                "Score":   round(float(score), 2),
            })

    if not emotion_rows:
        st.warning("Aucune émotion détectée à tracer.")
        return

    df = pd.DataFrame(emotion_rows)

    group_size = st.slider("Regroupement (frames)", min_value=1, max_value=10, value=5)
    df["FrameGroup"] = (df["Frame"] // group_size) * group_size
    df_grouped = df.groupby(["FrameGroup", "Emotion"], as_index=False)["Score"].mean()

    chart = (
        alt.Chart(df_grouped)
        .mark_line(point=True)
        .encode(
            x=alt.X("FrameGroup:Q", title=f"Frame (groupes de {group_size})"),
            y=alt.Y("Score:Q",      title="Score moyen (%)"),
            color=alt.Color("Emotion:N", title="Émotion"),
            tooltip=["FrameGroup", "Emotion", "Score"],
        )
        .properties(width=700, height=400)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


def show_category_breakdown(category_breakdown: dict):
    """Affiche la répartition positive/négative/neutre sous forme de barres."""
    if not category_breakdown:
        return

    st.subheader("📊 Répartition émotionnelle globale")
    df_cat = pd.DataFrame([
        {"Catégorie": k.capitalize(), "Pourcentage": v}
        for k, v in category_breakdown.items()
        if k != "dominant_category"
    ])

    chart = (
        alt.Chart(df_cat)
        .mark_bar()
        .encode(
            x=alt.X("Catégorie:N", title="Catégorie"),
            y=alt.Y("Pourcentage:Q", title="%"),
            color=alt.Color("Catégorie:N", scale=alt.Scale(
                domain=["Positive", "Negative", "Neutral"],
                range=["#2ecc71", "#e74c3c", "#95a5a6"]
            )),
            tooltip=["Catégorie", "Pourcentage"],
        )
        .properties(width=400, height=300)
    )
    st.altair_chart(chart, use_container_width=False)
    st.caption(
        f"Catégorie dominante : **{category_breakdown.get('dominant_category', 'N/A').capitalize()}**"
    )


def show_frames_grid(results: list):
    """Affiche les frames analysées en grille 3 colonnes."""
    st.subheader("🖼️ Frames analysées")
    cols = st.columns(3)
    for i, r in enumerate(results):
        frame_path = os.path.join(TEMP_FRAMES, r.get("frame", ""))
        if not os.path.exists(frame_path):
            continue
        caption = f"{r['frame']} — {r.get('dominant_emotion', 'N/A')}"
        if r.get("is_suspect"):
            caption += " ⚠️"
        if r.get("is_derived_dominant"):
            caption += " (inférée)"
        with cols[i % 3]:
            st.image(frame_path, caption=caption, width=220)


# ── Section : Rapport ─────────────────────────────────────────────────────────

def generate_and_download_reports(
    results, voice_results, top_emotion_frames,
    behavior_summary, truth_analysis, qa_result,
    dissonance, category_breakdown
):
    """
    CORRECTION : ReportGenerator reçoit maintenant tous les paramètres
    disponibles incluant dissonance et category_breakdown.
    """
    report = ReportGenerator(
        results=results,
        video_name=TEMP_VIDEO,
        voice_results=voice_results,
        top_emotion_frames=top_emotion_frames,
        behavior_summary=behavior_summary,
        truth_analysis=truth_analysis,
        qa_analysis=qa_result,
        dissonance=dissonance,
        category_breakdown=category_breakdown,
    )

    with st.spinner("Génération des rapports..."):
        report.to_csv(REPORT_CSV)
        report.to_json(REPORT_JSON)
        report.to_pdf(REPORT_PDF)

    st.success("Rapports générés avec succès.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "⬇️ Télécharger CSV",
            open(REPORT_CSV, "rb"),
            file_name=REPORT_CSV,
            mime="text/csv"
        )
    with col2:
        st.download_button(
            "⬇️ Télécharger JSON",
            open(REPORT_JSON, "rb"),
            file_name=REPORT_JSON,
            mime="application/json"
        )
    with col3:
        st.download_button(
            "⬇️ Télécharger PDF",
            open(REPORT_PDF, "rb"),
            file_name=REPORT_PDF,
            mime="application/pdf"
        )


# ── Application principale ────────────────────────────────────────────────────

def main():

    st.title("🎭 Analyse Comportementale Multimodale")
    st.caption(
        "Analyse des émotions faciales, du stress vocal et de la cohérence "
        "des réponses à partir d'une vidéo d'entretien."
    )

    # ── Sidebar : paramètres ──────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Paramètres")
        fps = st.slider(
            "Fréquence d'extraction (frames/sec)",
            min_value=0.1, max_value=2.0, value=0.3, step=0.1,
            help="0.3 = 1 frame toutes les 3 secondes"
        )
        st.markdown("---")
        st.caption(
            "⚠️ Ce système est un outil d'aide à l'analyse. "
            "Les résultats ne constituent pas une preuve et "
            "ne doivent pas être utilisés à des fins légales."
        )

    # ── Upload vidéo ──────────────────────────────────────────────────────────
    uploaded_video = st.file_uploader(
        "📁 Uploader une vidéo d'entretien",
        type=["mp4", "avi", "mov", "mkv"]
    )

    if not uploaded_video:
        st.info("Uploadez une vidéo pour démarrer l'analyse.")
        return

    # CORRECTION : nettoyage avant chaque nouvelle analyse
    cleanup_temp_files()
    video_path = save_uploaded_video(uploaded_video)

    # Infos vidéo
    try:
        info = get_video_info(video_path)
        st.info(
            f"Vidéo chargée — Durée : {info['duration_sec']}s | "
            f"FPS : {info['fps']} | Résolution : {info['resolution']}"
            f"Resolution : {info['resolution']}"
        )
    except Exception:
        pass

    # ── Analyse faciale ───────────────────────────────────────────────────────
    st.header("😶 Analyse faciale")
    results = run_facial_analysis(video_path, fps)
    if not results:
        return

    # Calculs globaux
    top_emotion_frames = get_top_emotion_frames(results, top_n=5)
    category_breakdown = get_emotion_category_breakdown(results)
    dissonance         = detect_emotional_dissonance(results)
    behavior_summary   = generate_behavior_summary(results)
    dist_summary       = get_emotion_distribution_summary(results)

    # Résumé comportemental
    st.subheader("📝 Résumé comportemental")
    st.markdown(behavior_summary)

    # Dissonance émotionnelle
    st.subheader("🔀 Dissonance émotionnelle")
    d_score = dissonance.get("dissonance_score", 0)
    st.metric("Score de dissonance", f"{d_score:.2f} / 1.0")
    st.caption(dissonance.get("interpretation", ""))

    # ── Analyse vocale ────────────────────────────────────────────────────────
    st.header("🎙️ Analyse vocale")
    voice_results = run_vocal_analysis(video_path)

    if voice_results and "error" not in voice_results:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Stress score",  voice_results.get("stress_score", "N/A"))
        col2.metric("Pitch moyen",   f"{voice_results.get('pitch_mean', 0):.1f} Hz")
        col3.metric("RMS",           f"{voice_results.get('rms', 0):.4f}")
        col4.metric("ZCR",           f"{voice_results.get('zcr', 0):.4f}")

    # ── Sincérité ─────────────────────────────────────────────────────────────
    st.header("🧠 Sincérité")
    truth_analysis = run_truth_analysis(video_path, top_emotion_frames)

    # ── Analyse Q/R ───────────────────────────────────────────────────────────
    st.header("💬 Pertinence Question / Réponse")
    qa_result = run_qa_analysis(video_path)

    # ── Visualisations ────────────────────────────────────────────────────────
    st.header("📊 Visualisations")
    show_category_breakdown(category_breakdown)
    show_emotion_chart(results)
    show_frames_grid(results)

    # ── Rapports ──────────────────────────────────────────────────────────────
    st.header("📄 Rapports")
    generate_and_download_reports(
        results, voice_results, top_emotion_frames,
        behavior_summary, truth_analysis, qa_result,
        dissonance, category_breakdown
    )


if __name__ == "__main__":
    main()