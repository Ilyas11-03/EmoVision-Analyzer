import json  # Importation du module json pour la sérialisation des données
from fpdf import FPDF  # Importation de la classe FPDF pour générer des fichiers PDF
import os  # Importation du module os (non utilisé ici mais souvent utile pour la gestion des fichiers)
from collections import Counter  # Pour compter les émotions dominantes
import csv  # Importation du module csv (non utilisé ici mais souvent utile pour la gestion des fichiers Excel)
from datetime import datetime  # Importation du module datetime pour la gestion des dates et heures

class ReportGenerator:

    def __init__(self, results, video_name="temp_video.mp4", voice_results=None,top_emotion_frames=None,behavior_summary=None,truth_analysis=None, qa_analysis=None):

        self.results = results  # Stocke les résultats d'analyse (liste de dictionnaires)
        self.video_name = video_name  # Nom du fichier vidéo analysé'
        self.voice_results = voice_results or {} # Résultats d'analyse audio (optionnel, non utilisé ici)
        self.top_emotion_frames = top_emotion_frames or []
        self.behavior_summary = behavior_summary or "Aucune donné disponible"
        self.truth_analysis = truth_analysis or {}
        self.qa_analysis = qa_analysis or {}


    def to_json(self, output_path="report.json"): # Génère un rapport JSON

        report_data = {
            "video": self.video_name,  # Ajoute le nom de la vidéo au rapport
            "frames_analyzed": len(self.results),  # Nombre de frames analysées
            "results": self.results,  # Résultats détaillés pour chaque frame
            "voice_emotion": self.voice_results,  # Résultats d'analyse audio (optionnel)
            "top_emotion_frames": self.top_emotion_frames, # Liste des frames avec les émotions dominantes
            "behavior_summary": self.behavior_summary,
            "truth_analysis": self.truth_analysis,

        }

        with open(output_path, "w") as f:  # Ouvre le fichier de sortie en écriture
            json.dump(report_data, f, indent=4)  # Écrit les données au format JSON avec indentation

    def to_csv(self, output_path="report.csv"): # Génère un rapport CSV
        
        with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Frame", "Dominant Emotion"]
            
            #Récupérer toutes les émotions possibles
            all_emotions = set()
            for item in self.results:
                all_emotions.update(item.get("emotions", {}).keys())
            fieldnames.extend(sorted(all_emotions))  # Ajoute les émotions comme colonnes

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames) # Crée un objet DictWriter pour écrire des dictionnaires dans le CSV
            writer.writeheader()

            for i, item in enumerate(self.results):
                row = {"Frame": f"Frame {i+1}", "Dominant Emotion": item.get("dominant_emotion", "N/A")}
                row.update(item.get("emotions", {}))
                writer.writerow(row)

    def to_pdf(self, output_path="report.pdf"): # Génère un rapport PDF

        pdf = FPDF()  # Crée un objet PDF
        pdf.add_page()  # Ajoute une page au PDF
        pdf.set_font("Times", style='B', size=12)  # Définit la police et la taille

        pdf.cell(200, 10, txt="Rapport d'Analyse Emotionnelle", ln=True)  # Titre du rapport
        pdf.cell(200, 10, txt=f"Vidéo : {self.video_name}", ln=True)  # Nom de la vidéo
        pdf.cell(200, 10, txt=f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True) # Date de génération du rapport
        pdf.cell(200, 10, txt=f"Nombre de frames analysées : {len(self.results)}", ln=True)  # Nombre de frames
        pdf.ln()  # Saut de ligne

        # ===== 3. Résultats vocaux =====
        if self.voice_results:
            pdf.set_font("Times",style='B', size=12)
            pdf.cell(200, 10, txt=" Analyse vocale :", ln=True)
            pdf.set_font("Times", size=11)
            for k, v in self.voice_results.items():
                pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
            pdf.ln() # Saut de ligne
        
        # ===== 4. Compter les émotions dominantes sur toutes les frames =====
        pdf.set_font("Times", style='B', size=12)
        pdf.cell(200, 10, txt=" Statistiques générales :", ln=True)
        pdf.set_font("Times", size=11)
        dominants = [item.get("dominant_emotion", "N/A") for item in self.results]
        top_emotions = Counter(dominants).most_common(3) # Compter les occurrences de chaque émotion dominante
        for emo, count in top_emotions:
            pdf.cell(200, 10, txt=f" - {emo} ({count} fois)", ln=True) # Affiche les émotions dominantes et leur fréquence
        pdf.ln()

        # ===== 5. Analyse de sincérité =====
        if self.truth_analysis:
         pdf.set_font("Arial", style='B', size=12)
         pdf.cell(200, 10, txt="Analyse de la sincérité :", ln=True)
         pdf.set_font("Arial", size=11)
         score = self.truth_analysis.get("truth_score", "N/A")
         verdict = self.truth_analysis.get("verdict", "Indéterminé")
         explanation = self.truth_analysis.get("explanation", "")

         pdf.cell(200, 10, txt=f"Score de vérité : {score}", ln=True)
         pdf.cell(200, 10, txt=f"Interprétation : {verdict}", ln=True)
         pdf.multi_cell(0, 10, txt=f"Explication : {explanation}")
         pdf.ln()

         # ===== 6. Analyse de pertinence question/réponse =====
        if self.qa_analysis:
          pdf.set_font("Arial", style='B', size=12)
          pdf.cell(200, 10, txt="Analyse de pertinence Q/R :", ln=True)
          pdf.set_font("Arial", size=11)
          question = self.qa_analysis.get("question", "N/A")
          response = self.qa_analysis.get("response", "N/A")
          similarity = self.qa_analysis.get("similarity_score", "N/A")
          verdict = self.qa_analysis.get("verdict", "Indéterminé")
          explanation = self.qa_analysis.get("explanation", "")
    
          pdf.multi_cell(0, 10, txt=f"Question : {question}")
          pdf.multi_cell(0, 10, txt=f"Réponse : {response}")
          pdf.cell(200, 10, txt=f"Similarité : {similarity}", ln=True)
          pdf.cell(200, 10, txt=f"Verdict : {verdict}", ln=True)
          pdf.multi_cell(0, 10, txt=f"Explication : {explanation}")
          pdf.ln()

        # Résumé comportemental
        pdf.set_font("Times", style='B', size=12)
        pdf.cell(200, 10, txt=" Résumé comportemental :", ln=True)
        pdf.set_font("Times", size=11)
        pdf.multi_cell(0, 10, txt=self.behavior_summary)
        pdf.ln()

         # ===== 5. Moments émotionnels forts =====
        if self.top_emotion_frames:
            pdf.set_font("Times",style='B' ,size=12)
            pdf.cell(200, 10, txt=" Frames émotionnelles fortes :", ln=True)
            pdf.set_font("Times", style='B', size=11)
            for item in self.top_emotion_frames:
                pdf.cell(200, 10, txt=f"{item['frame']} -> {item['dominant_emotion']} ({item['intensity']})", ln=True)
            pdf.ln()

        # ===== 6. Détail frame par frame =====
        pdf.set_font("Times", style='B', size=12)
        pdf.cell(200, 10, txt=" Détail par frame :", ln=True)
        pdf.ln()
        
        frames_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp_frames/"))  # Dossier contenant les frames extraites
        for i, item in enumerate(self.results):  # Parcourt chaque résultat de frame
            frame_filename = item.get('frame', f"frame_{i+1}.jpg") # Utilise le nom du fichier si présent
            dominant = item.get("dominant_emotion", "N/A")
            emotions = item.get("emotions", {})

             # Ajout de l'image de la frame si elle existe
            frame_path = os.path.join(frames_dir, frame_filename)
            if os.path.isfile(frame_path) and frame_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                pdf.image(frame_path, w=120)
                pdf.ln(3)

            pdf.ln()  # Saut de ligne après chaque frame
 
            pdf.cell(200, 10, txt=f"Frame {i+1} - {frame_filename}", ln=True)  # Nom de la frame
            pdf.cell(200, 10, txt=f"  Emotion dominante : {dominant}", ln=True)  # Emotion dominante
            for k, v in emotions.items():  # Parcourt chaque émotion et sa valeur
                    pdf.cell(200, 10, txt=f"{k}: {v:.2f}", ln=True)  # Affiche l'émotion et son score
            pdf.ln(5)

        pdf.output(output_path)  # Génère le fichier PDF à l'emplacement spécifié

   