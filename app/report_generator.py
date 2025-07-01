import json  # Importation du module json pour la sérialisation des données
from fpdf import FPDF  # Importation de la classe FPDF pour générer des fichiers PDF
import os  # Importation du module os (non utilisé ici mais souvent utile pour la gestion des fichiers)
from collections import Counter  # Pour compter les émotions dominantes
import csv  # Importation du module csv (non utilisé ici mais souvent utile pour la gestion des fichiers Excel)


class ReportGenerator:

    def __init__(self, results, video_name="temp_video.mp4", voice_results=None):

        self.results = results  # Stocke les résultats d'analyse (liste de dictionnaires)
        self.video_name = video_name  # Nom du fichier vidéo analysé'
        self.voice_results = voice_results # Résultats d'analyse audio (optionnel, non utilisé ici)

    def to_json(self, output_path="report.json"): # Génère un rapport JSON

        report_data = {
            "video": self.video_name,  # Ajoute le nom de la vidéo au rapport
            "frames_analyzed": len(self.results),  # Nombre de frames analysées
            "results": self.results,  # Résultats détaillés pour chaque frame
            "voice_emotion": self.voice_results  # Résultats d'analyse audio (optionnel)
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
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i, item in enumerate(self.results):
                row = {"Frame": f"Frame {i+1}", "Dominant Emotion": item["dominant_emotion"]}
                row.update(item.get("emotions", {}))
                writer.writerow(row)

    def to_pdf(self, output_path="report.pdf"): # Génère un rapport PDF

        pdf = FPDF()  # Crée un objet PDF
        pdf.add_page()  # Ajoute une page au PDF
        pdf.set_font("Arial", size=12)  # Définit la police et la taille
        pdf.cell(200, 10, txt="Rapport d'Analyse Emotionnelle", ln=True)  # Titre du rapport
        pdf.cell(200, 10, txt=f"Vidéo : {self.video_name}", ln=True)  # Nom de la vidéo
        pdf.cell(200, 10, txt=f"Nombre de frames analysées : {len(self.results)}", ln=True)  # Nombre de frames
        pdf.ln()  # Saut de ligne

        #Résultats vocaux
        if self.voice_results:
            pdf.cell(200, 10, txt="Analyse émotionnelle vocale :", ln=True)
            for k, v in self.voice_results.items():
                pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
            pdf.ln() # Saut de ligne
        
        # Compter les émotions dominantes sur toutes les frames
        dominants = [item["dominant_emotion"] for item in self.results]
        counter = Counter(dominants) # Compter les occurrences de chaque émotion dominante
        most_common = counter.most_common(1)[0]  # ('neutral', 8) par exemple
        pdf.cell(200, 10, txt=f"Emotion dominante la plus fréquente : {most_common[0]} ({most_common[1]} fois)", ln=True) # Affiche l'émotion dominante la plus fréquente
        pdf.ln()
        
        frames_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp_frames/"))  # Dossier contenant les frames extraites
        for i, item in enumerate(self.results):  # Parcourt chaque résultat de frame
            frame_filename = item.get('frame', f"frame_{i+1}.jpg") # Utilise le nom du fichier si présent

             # Ajout de l'image de la frame si elle existe
            frame_img_path = os.path.join(frames_dir, frame_filename)
            if os.path.exists(frame_img_path):
                pdf.image(frame_img_path, w=120)  # Ajuste la largeur selon besoin
                pdf.ln(5)  # Saut de ligne après l'image

            pdf.ln()  # Saut de ligne après chaque frame
 
            pdf.cell(200, 10, txt=f"Frame {i+1} - {frame_filename}", ln=True)  # Nom de la frame
            pdf.cell(200, 10, txt=f"  Emotion dominante : {item['dominant_emotion']}", ln=True)  # Emotion dominante
            emotions = item.get("emotions", {})  # Récupère le dictionnaire des émotions
            if emotions:  # Si des émotions sont présentes
                for k, v in emotions.items():  # Parcourt chaque émotion et sa valeur
                    pdf.cell(200, 10, txt=f"{k}: {v:.2f}", ln=True)  # Affiche l'émotion et son score

        pdf.output(output_path)  # Génère le fichier PDF à l'emplacement spécifié

   