import sys  # Importation du module sys pour manipuler le chemin d'accès
import os  # Importation du module os pour la gestion des fichiers et dossiers
import altair as alt  # Importation d'Altair pour la visualisation de données
import pandas as pd  # Importation de pandas pour la manipulation de données tabulaires
import shutil  # Importation de shutil pour la gestion des fichiers et dossiers
import numpy as np # Importation de numpy pour les opérations numériques
import streamlit as st  # Importation de Streamlit pour créer l'interface web

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Ajoute le dossier parent au path pour les imports


from app.video_processing import extract_frames  # Importation de la fonction d'extraction de frames
from app.emotion_detector import detect_emotions_on_image  # Importation de la détection d'émotions
from app.report_generator import ReportGenerator  # Importation du générateur de rapports

from app.stress_analysis import extract_audio_features , extract_stress_segment
from app.emotion_utils import get_top_emotion_frames
from app.behavior_summary import generate_behavior_summary
from app.truth_detector import analyze_truth_from_stress_and_emotion
from app.speech_to_text import transcribe_video
from app.qa_analyzer import analyze_qa_relevance

def main():

    st.title("Détection d'Émotions Faciales")  # Affiche le titre principal de l'application

    uploaded_video = st.file_uploader("Uploader une vidéo", type=["mp4"])  # Widget pour uploader une vidéo MP4
    
    if uploaded_video:  # Si une vidéo est uploadée

        # Supprime le dossier temp_frames s'il existe déjà
        if os.path.exists("temp_frames"):  # Vérifie si le dossier temp_frames existe
            shutil.rmtree("temp_frames")  # Efface tout le dossier et son contenu
        os.makedirs("temp_frames", exist_ok=True)

        with open("temp_video.mp4", "wb") as f:  # Ouvre un fichier temporaire pour écrire la vidéo uploadée
            f.write(uploaded_video.read())  # Écrit le contenu de la vidéo dans le fichier
        
        st.info(" Extraction des frames...")
        extract_frames("temp_video.mp4", "temp_frames", fps=0.1)  # Extrait 1 image toutes les 10 secondes de la vidéo

        st.info(" Détection des émotions faciales...")
        results = []  # Initialise une liste pour stocker les résultats d'émotions par frame
        frame_files = sorted(os.listdir("temp_frames"))
        progress = st.progress(0) # Initialise une barre de progression

        for i, frame_file in enumerate(frame_files): # Parcourt chaque frame extraite
            frame_path = os.path.join("temp_frames", frame_file)  # Construit le chemin complet du fichier frame
            if os.path.isfile(frame_path): # Vérifie que le fichier existe
                res = detect_emotions_on_image(frame_path) # Détecte les émotions sur la frame
                res["frame"] = frame_file # Ajoute le nom du fichier frame au résultat
                results.append(res) # Ajoute le résultat à la liste
            progress.progress((i + 1) / len(frame_files)) # Met à jour la barre de progression

        st.success(" Détection faciale terminée.") # Affiche un message de succès à la fin de la détection

        st.info(" Analyse de la voix...")
        voice_results = extract_audio_features("temp_video.mp4")
        st.success(" Analyse vocale terminée.")
        
        #Résumé général des émotions
        top_emotion_frames = get_top_emotion_frames(results, top_n=5)
        behavior_summary = generate_behavior_summary(top_emotion_frames)
        
        # ⏱️ Analyse de vérité
        st.subheader(" Analyse de sincérité sur une réponse")
        col1, col2 = st.columns(2)
        with col1:
            start_sec = st.number_input("⏱️ Début (en secondes)", min_value=0, value=5)
        with col2:
            end_sec = st.number_input("⏱️ Fin (en secondes)", min_value=start_sec + 1, value=10)

        truth_stress = extract_stress_segment("temp_video.mp4", start_sec, end_sec)
        # On prend la frame la plus expressive comme base d'émotion
        base_emotion = top_emotion_frames[0]["dominant_emotion"] if top_emotion_frames else "neutral"
        truth_analysis = analyze_truth_from_stress_and_emotion(truth_stress, base_emotion)

        st.markdown(f"**Vérité estimée :** {truth_analysis['verdict']} (score {truth_analysis['truth_score']})")
        st.caption(truth_analysis['explanation'])
 
        st.subheader("🧾 Pertinence de la réponse (Question / Réponse)")
        question = st.text_input("❓ Question posée par le recruteur")

        if question:
            with st.spinner("📝 Transcription automatique en cours..."):
                response_transcript = transcribe_video("temp_video.mp4")

            relevance_result = analyze_qa_relevance(question, response_transcript)
            st.markdown(f"**Pertinence estimée :** {relevance_result['verdict']} (score {relevance_result['similarity_score']})")
            st.caption(relevance_result['explanation'])
        else:
            relevance_result = None
        
        report = ReportGenerator(
            results, 
            video_name="temp_video.mp4",
            voice_results=voice_results,
            top_emotion_frames=top_emotion_frames,
            behavior_summary=behavior_summary,
            truth_analysis=truth_analysis
            )  # Crée un rapport à partir des résultats

        report.to_csv("report_summary.csv")  # Génère un rapport CSV à partir des résultats
        report.to_json("report.json")  # Génère un rapport JSON à partir des résultats
        report.to_pdf("report.pdf")  # Génère un rapport PDF à partir des résultats
        
        # Affiche un message de succès
        st.success("Rapport généré avec succès.")
        st.download_button("Télécharger CSV", open("report_summary.csv", "rb"), file_name="report_summary.csv")  # Bouton de téléchargement du CSV
        st.download_button("Télécharger JSON", open("report.json", "rb"), file_name="report.json")  # Bouton de téléchargement du JSON
        st.download_button("Télécharger PDF", open("report.pdf", "rb"), file_name="report.pdf")  # Bouton de téléchargement du PDF
          

        # 🖼️ Affichage des frames analysées
        st.subheader("🖼️ Frames analysées")
        cols = st.columns(3)
        for i, r in enumerate(results):
            frame_path = os.path.join("temp_frames", r["frame"])
            caption = f"{r['frame']} - {r['dominant_emotion']}"
            if r.get("is_suspect"):
                caption += " ⚠️"
            if os.path.exists(frame_path):
                with cols[i % 3]:
                    st.image(frame_path, caption=caption, width=220)
                    
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

        #Regroupement par tranche de frames (ex: 5 frames)
        group_size = 5 # Modifie selon la densité souhaitée

        if not df_emotions.empty:  # Si le DataFrame n'est pas vide
            df_emotions["FrameGroup"] = (df_emotions["Frame"] // group_size) * group_size # Calcule le groupe de frames pour chaque ligne
            df_grouped = df_emotions.groupby(["FrameGroup", "Emotion"], as_index=False)["Score"].mean() # Calcule la moyenne des scores par groupe et émotion
            st.subheader(" Évolution des émotions par frame (regroupé)") # Affiche le sous-titre du graphique
            chart = alt.Chart(df_grouped).mark_line(point=True).encode(
               x=alt.X("FrameGroup:Q", title=f"Frame (par {group_size})"),  # Axe X : groupe de frames
               y=alt.Y("Score:Q", title="Score (%)"), # Axe Y : score moyen
               color=alt.Color("Emotion:N", title="Émotion") # Couleur par émotion
        ).properties(width=700, height=400).interactive() # Définit la taille et l'interactivité du graphique
            st.altair_chart(chart, use_container_width=True)  # Affiche le graphique dans Streamlit
        else:
            st.warning("Aucune émotion détectée à tracer.")  # Affiche un message si aucune émotion n'a été détectée

if __name__ == "__main__":  # Si le script est exécuté directement
    main()  # Lance l'application Streamlit