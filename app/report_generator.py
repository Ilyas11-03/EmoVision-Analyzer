import json
from fpdf import FPDF
import os

class ReportGenerator:
    def __init__(self, results, video_name="temp_video.mp4"):
        self.results = results
        self.video_name = video_name

    def to_json(self, output_path="report.json"):
        report_data = {
            "video": self.video_name,
            "frames_analyzed": len(self.results),
            "results": self.results
        }
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=4)

    def to_pdf(self, output_path="report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Rapport d'Analyse Emotionnelle", ln=True)
        pdf.cell(200, 10, txt=f"Vidéo : {self.video_name}", ln=True)
        pdf.cell(200, 10, txt=f"Nombre de frames analysées : {len(self.results)}", ln=True)
        pdf.ln()

        for i, item in enumerate(self.results):
            pdf.cell(200, 10, txt=f"Frame {i+1} - {item['frame']}", ln=True)
            pdf.cell(200, 10, txt=f"  Emotion dominante : {item['dominant_emotion']}", ln=True)
            emotions = item.get("emotions", {})
            if emotions:
                for k, v in emotions.items():
                    pdf.cell(200, 10, txt=f"    {k}: {v:.2f}", ln=True)
            pdf.ln()
        pdf.output(output_path)