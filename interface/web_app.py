import sys
import os
import altair as alt
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from app.video_processing import extract_frames
from app.emotion_detector import detect_emotions_on_image
from app.report_generator import ReportGenerator

def main():
    st.title("Détection d'Émotions Faciales (Sans Audio)")

    uploaded_video = st.file_uploader("Uploader une vidéo", type=["mp4"])
    if uploaded_video:
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_video.read())

        extract_frames("temp_video.mp4", "temp_frames", fps=1)

        results = []
        for frame_file in sorted(os.listdir("temp_frames")):
            res = detect_emotions_on_image(os.path.join("temp_frames", frame_file))
            results.append(res)

        report = ReportGenerator(results, video_name="temp_video.mp4")
        report.to_json("report.json")
        report.to_pdf("report.pdf")

        st.success("Rapport généré avec succès.")
        st.download_button("Télécharger JSON", open("report.json", "rb"), file_name="report.json")
        st.download_button("Télécharger PDF", open("report.pdf", "rb"), file_name="report.pdf")

        # Graphe Altair
        emotion_rows = []
        for idx, r in enumerate(results):
            for emotion, score in r.get("emotions", {}).items():
                emotion_rows.append({"Frame": idx, "Emotion": emotion, "Score": score})

        df_emotions = pd.DataFrame(emotion_rows)
        if not df_emotions.empty:
            st.subheader("📈 Évolution des émotions par frame")
            chart = alt.Chart(df_emotions).mark_line(point=True).encode(
                x=alt.X("Frame:Q", title="Numéro de Frame"),
                y=alt.Y("Score:Q", title="Score (%)"),
                color=alt.Color("Emotion:N", title="Émotion")
            ).properties(width=700, height=400).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Aucune émotion détectée à tracer.")

if __name__ == "__main__":
    main()