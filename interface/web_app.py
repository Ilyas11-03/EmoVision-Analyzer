import sys  # Importation du module sys pour manipuler le chemin d'accès
import os  # Importation du module os pour la gestion des fichiers et dossiers
import altair as alt  # Importation d'Altair pour la visualisation de données
import pandas as pd  # Importation de pandas pour la manipulation de données tabulaires

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Ajoute le dossier parent au path pour les imports

import streamlit as st  # Importation de Streamlit pour créer l'interface web
from app.video_processing import extract_frames  # Importation de la fonction d'extraction de frames
from app.emotion_detector import detect_emotions_on_image  # Importation de la détection d'émotions
from app.report_generator import ReportGenerator  # Importation du générateur de rapports
from app.voice_emotion import extract_audio_emotions  # Importation de l'analyse des émotions vocales

def main():
    st.title("Détection d'Émotions Faciales")  # Titre de l'application

    uploaded_video = st.file_uploader("Uploader une vidéo", type=["mp4"])  # Widget pour uploader une vidéo
    if uploaded_video:
        with open("temp_video.mp4", "wb") as f:  # Ouvre un fichier temporaire pour écrire la vidéo uploadée
            f.write(uploaded_video.read())  # Écrit le contenu de la vidéo dans le fichier

        extract_frames("temp_video.mp4", "temp_frames", fps=1)  # Extrait les frames de la vidéo à 1 fps

        results = []  # Liste pour stocker les résultats d'émotions par frame
        for frame_file in sorted(os.listdir("temp_frames")):  # Parcourt chaque image extraite
            res = detect_emotions_on_image(os.path.join("temp_frames", frame_file))  # Détecte les émotions sur la frame
            results.append(res)  # Ajoute le résultat à la liste

        #Analyse des émotions vocales
        voice_results = extract_audio_emotions("temp_video.mp4")
        
        report = ReportGenerator(results, video_name="temp_video.mp4")  # Crée un rapport à partir des résultats
        report.to_json("report.json")  # Génère un rapport JSON
        report.to_pdf("report.pdf")  # Génère un rapport PDF

        st.success("Rapport généré avec succès.")  # Affiche un message de succès
        st.download_button("Télécharger JSON", open("report.json", "rb"), file_name="report.json")  # Bouton de téléchargement JSON
        st.download_button("Télécharger PDF", open("report.pdf", "rb"), file_name="report.pdf")  # Bouton de téléchargement PDF

        # Graphe Altair
        emotion_rows = []  # Liste pour stocker les données de chaque émotion par frame
        for idx, r in enumerate(results):
            for emotion, score in r.get("emotions", {}).items():  # Parcourt chaque émotion détectée
                emotion_rows.append({
                    "Frame": idx, 
                    "Emotion": emotion, 
                    "Score": score
                })  # Ajoute la donnée à la liste

        df_emotions = pd.DataFrame(emotion_rows)  # Crée un DataFrame pandas à partir des données
        if not df_emotions.empty:
            st.subheader("📈 Évolution des émotions par frame")  # Sous-titre du graphique
            chart = alt.Chart(df_emotions).mark_line(point=True).encode(
                x=alt.X("Frame:Q", title="Numéro de Frame"),  # Axe X : numéro de frame
                y=alt.Y("Score:Q", title="Score (%)"),  # Axe Y : score de l'émotion
                color=alt.Color("Emotion:N", title="Émotion")  # Couleur par émotion
            ).properties(width=700, height=400).interactive()
            st.altair_chart(chart, use_container_width=True)  # Affiche le graphique dans Streamlit
        else:
            st.warning("Aucune émotion détectée à tracer.")  # Message si aucune émotion détectée

if __name__ == "__main__":
    main()  # Lance l'application Streamlit si le fichier est exécuté directement