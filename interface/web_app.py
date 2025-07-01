import sys  # Importation du module sys pour manipuler le chemin d'accès
import os  # Importation du module os pour la gestion des fichiers et dossiers
import altair as alt  # Importation d'Altair pour la visualisation de données
import pandas as pd  # Importation de pandas pour la manipulation de données tabulaires
import shutil  # Importation de shutil pour la gestion des fichiers et dossiers

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Ajoute le dossier parent au path pour les imports

import streamlit as st  # Importation de Streamlit pour créer l'interface web
from app.video_processing import extract_frames  # Importation de la fonction d'extraction de frames
from app.emotion_detector import detect_emotions_on_image  # Importation de la détection d'émotions
from app.report_generator import ReportGenerator  # Importation du générateur de rapports


def main():

    st.title("Détection d'Émotions Faciales")  # Affiche le titre principal de l'application

    uploaded_video = st.file_uploader("Uploader une vidéo", type=["mp4"])  # Widget pour uploader une vidéo MP4
    if uploaded_video:  # Si une vidéo est uploadée

        # Supprime le dossier temp_frames s'il existe déjà
        if os.path.exists("temp_frames"):  # Vérifie si le dossier temp_frames existe
            shutil.rmtree("temp_frames")  # Efface tout le dossier et son contenu

        with open("temp_video.mp4", "wb") as f:  # Ouvre un fichier temporaire pour écrire la vidéo uploadée
            f.write(uploaded_video.read())  # Écrit le contenu de la vidéo dans le fichier

        extract_frames("temp_video.mp4", "temp_frames", fps=0.1)  # Extrait 1 image toutes les 10 secondes de la vidéo

        results = []  # Initialise une liste pour stocker les résultats d'émotions par frame
        for frame_file in sorted(os.listdir("temp_frames")):  # Parcourt chaque image extraite, triée par nom
            res = detect_emotions_on_image(os.path.join("temp_frames", frame_file))  # Détecte les émotions sur la frame
            res["frame"] = frame_file  # Ajoute le nom de la frame au résultat
            results.append(res)  # Ajoute le résultat à la liste des résultats

        report = ReportGenerator(results, video_name="temp_video.mp4")  # Crée un rapport à partir des résultats

        report.to_csv("report_summary.csv")  # Génère un rapport CSV à partir des résultats
        report.to_json("report.json")  # Génère un rapport JSON à partir des résultats
        report.to_pdf("report.pdf")  # Génère un rapport PDF à partir des résultats

        st.download_button("Télécharger CSV", open("report_summary.csv", "rb"), file_name="report_summary.csv")  # Bouton de téléchargement du CSV
        st.download_button("Télécharger JSON", open("report.json", "rb"), file_name="report.json")  # Bouton de téléchargement du JSON
        st.download_button("Télécharger PDF", open("report.pdf", "rb"), file_name="report.pdf")  # Bouton de téléchargement du PDF
        st.success("Rapport généré avec succès.")  # Affiche un message de succès

        # Graphe Altair
        emotion_rows = []  # Initialise une liste pour stocker les données de chaque émotion par frame
        for idx, r in enumerate(results):  # Parcourt chaque résultat par frame
            for emotion, score in r.get("emotions", {}).items():  # Parcourt chaque émotion détectée dans la frame
                emotion_rows.append({
                    "Frame": idx,  # Numéro de la frame
                    "Emotion": emotion,  # Nom de l'émotion détectée
                    "Score": score  # Score de l'émotion détectée
                })  # Ajoute la donnée à la liste

        df_emotions = pd.DataFrame(emotion_rows)  # Crée un DataFrame pandas à partir des données collectées
        if not df_emotions.empty:  # Si le DataFrame n'est pas vide
            st.subheader("📈 Évolution des émotions par frame")  # Affiche un sous-titre pour le graphique
            chart = alt.Chart(df_emotions).mark_line(point=True).encode(
                x=alt.X("Frame:Q", title="Numéro de Frame"),  # Axe X : numéro de frame
                y=alt.Y("Score:Q", title="Score (%)"),  # Axe Y : score de l'émotion
                color=alt.Color("Emotion:N", title="Émotion")  # Couleur par émotion
            ).properties(width=700, height=400).interactive()  # Définit la taille et l'interactivité du graphique
            st.altair_chart(chart, use_container_width=True)  # Affiche le graphique dans Streamlit
        else:
            st.warning("Aucune émotion détectée à tracer.")  # Affiche un message si aucune émotion n'a été détectée

if __name__ == "__main__":  # Si le script est exécuté directement
    main()  # Lance l'application Streamlit