import json  # Importation du module json pour la sérialisation des données
from fpdf import FPDF  # Importation de la classe FPDF pour générer des fichiers PDF
import os  # Importation du module os (non utilisé ici mais souvent utile pour la gestion des fichiers)

class ReportGenerator:
    def __init__(self, results, video_name="temp_video.mp4"):
        self.results = results  # Stocke les résultats d'analyse (liste de dictionnaires)
        self.video_name = video_name  # Nom du fichier vidéo analysé

    def to_json(self, output_path="report.json"):
        report_data = {
            "video": self.video_name,  # Ajoute le nom de la vidéo au rapport
            "frames_analyzed": len(self.results),  # Nombre de frames analysées
            "results": self.results  # Résultats détaillés pour chaque frame
        }
        with open(output_path, "w") as f:  # Ouvre le fichier de sortie en écriture
            json.dump(report_data, f, indent=4)  # Écrit les données au format JSON avec indentation

    def to_pdf(self, output_path="report.pdf"):
        pdf = FPDF()  # Crée un objet PDF
        pdf.add_page()  # Ajoute une page au PDF
        pdf.set_font("Arial", size=12)  # Définit la police et la taille

        pdf.cell(200, 10, txt="Rapport d'Analyse Emotionnelle", ln=True)  # Titre du rapport
        pdf.cell(200, 10, txt=f"Vidéo : {self.video_name}", ln=True)  # Nom de la vidéo
        pdf.cell(200, 10, txt=f"Nombre de frames analysées : {len(self.results)}", ln=True)  # Nombre de frames
        pdf.ln()  # Saut de ligne

        for i, item in enumerate(self.results):  # Parcourt chaque résultat de frame
            pdf.cell(200, 10, txt=f"Frame {i+1} - {item['frame']}", ln=True)  # Nom de la frame
            pdf.cell(200, 10, txt=f"  Emotion dominante : {item['dominant_emotion']}", ln=True)  # Emotion dominante
            emotions = item.get("emotions", {})  # Récupère le dictionnaire des émotions
            if emotions:  # Si des émotions sont présentes
                for k, v in emotions.items():  # Parcourt chaque émotion et sa valeur
                    pdf.cell(200, 10, txt=f"    {k}: {v:.2f}", ln=True)  # Affiche l'émotion et son score
            pdf.ln()  # Saut de ligne après chaque frame
        pdf.output(output_path)  # Génère le fichier PDF à l'emplacement spécifié