import os
import json
import csv
from collections import Counter
from datetime import datetime
from typing import Optional
from fpdf import FPDF

# ── Constantes ────────────────────────────────────────────────────────────────

REPORT_TITLE = "Rapport d'Analyse Comportementale"
FRAMES_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../temp_frames/")
)

# ── Nettoyage des caractères spéciaux ────────────────────────────────────────


def _clean(text: str) -> str:
    """
    Nettoie le texte pour éviter les crashs d'encodage fpdf.
    Remplace les accents, emojis et caractères spéciaux non supportés.
    """
    if not isinstance(text, str):
        text = str(text)

    replacements = {
        # Accents français
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ä": "a",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ç": "c",
        "É": "E",
        "È": "E",
        "Ê": "E",
        "À": "A",
        "Â": "A",
        "Î": "I",
        "Ô": "O",
        "Ù": "U",
        "œ": "oe",
        "æ": "ae",
        # Ponctuation spéciale
        "\u00ab": '"',
        "\u00bb": '"',  # « »
        "\u2013": "-",
        "\u2014": "-",  # – —
        "\u2026": "...",  # …
        "\u200b": "",  # Zero-width space
        "\u2019": "'",  # '
        "\u2018": "'",  # '
        # Emojis fréquents dans le projet
        "\u2705": "[OK]",  # ✅
        "\u274c": "[X]",  # ❌
        "\u26a0\ufe0f": "[!]",  # ⚠️
        "\u26a0": "[!]",  # ⚠
        "\ufe0f": "",  # Variation selector
        "\U0001f536": "[~]",  # 🔶
        "\U0001f3ad": "",  # 🎭
        "\U0001f4ca": "",  # 📊
        "\U0001f4c8": "",  # 📈
        "\U0001f4ac": "",  # 💬
        "\U0001f9e0": "",  # 🧠
        "\U0001f399\ufe0f": "",  # 🎙️
        "\U0001f4c4": "",  # 📄
        "\U0001f610": "",  # 😶
        "\U0001f4c1": "",  # 📁
        "\u2b07\ufe0f": "",  # ⬇️
        "\u2192": "->",  # →
        "\u2022": "-",  # •
    }

    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Fallback final : supprime tout caractère non ASCII restant
    text = text.encode("latin-1", errors="ignore").decode("latin-1")

    return text


# ── Classe PDF (fallback sans police TTF externe) ─────────────────────────────


class UTF8PDF(FPDF):
    """
    Version fallback utilisant les polices intégrées fpdf (Times).
    Pas de dépendance externe — fonctionne immédiatement.
    Tous les textes passent par _clean() pour éviter les crashs d'encodage.
    """

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Times", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, _clean(REPORT_TITLE), align="R", ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def section_title(self, title: str):
        """Titre de section avec fond gris."""
        self.set_font("Times", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 9, f"  {_clean(title)}", ln=True, fill=True)
        self.ln(2)

    def body_text(self, text: str, size: int = 10):
        self.set_font("Times", "", size)
        self.multi_cell(0, 6, _clean(text))
        self.ln(1)

    def key_value(self, key: str, value: str):
        self.set_font("Times", "B", 10)
        self.cell(55, 7, f"{_clean(key)} :", ln=False)
        self.set_font("Times", "", 10)
        self.multi_cell(0, 7, _clean(str(value)))


# ── Classe principale ─────────────────────────────────────────────────────────


class ReportGenerator:

    def __init__(
        self,
        results: list,
        video_name: str = "video.mp4",
        voice_results: Optional[dict] = None,
        top_emotion_frames: Optional[list] = None,
        behavior_summary: Optional[str] = None,
        truth_analysis: Optional[dict] = None,
        qa_analysis: Optional[dict] = None,
        dissonance: Optional[dict] = None,
        category_breakdown: Optional[dict] = None,
    ):
        self.results = results
        self.video_name = video_name
        self.voice_results = voice_results or {}
        self.top_emotion_frames = top_emotion_frames or []
        self.behavior_summary = behavior_summary or "Aucune donnee disponible."
        self.truth_analysis = truth_analysis or {}
        self.qa_analysis = qa_analysis or {}
        self.dissonance = dissonance or {}
        self.category_breakdown = category_breakdown or {}

    # ── Export JSON ───────────────────────────────────────────────────────────

    def to_json(self, output_path: str = "report.json"):
        report_data = {
            "video": self.video_name,
            "generated_at": datetime.now().isoformat(),
            "frames_analyzed": len(self.results),
            "results": self.results,
            "voice_results": self.voice_results,
            "top_emotion_frames": self.top_emotion_frames,
            "behavior_summary": self.behavior_summary,
            "truth_analysis": self.truth_analysis,
            "qa_analysis": self.qa_analysis,
            "dissonance": self.dissonance,
            "category_breakdown": self.category_breakdown,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

    # ── Export CSV ────────────────────────────────────────────────────────────

    def to_csv(self, output_path: str = "report.csv"):
        all_emotions = set()
        for item in self.results:
            all_emotions.update(item.get("emotions", {}).keys())

        fieldnames = ["Frame", "Dominant Emotion", "Is Suspect"] + sorted(all_emotions)

        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for i, item in enumerate(self.results):
                row = {
                    "Frame": f"Frame {i + 1}",
                    "Dominant Emotion": item.get("dominant_emotion", "N/A"),
                    "Is Suspect": item.get("is_suspect", False),
                }
                for emotion, score in item.get("emotions", {}).items():
                    row[emotion] = round(float(score), 2)
                writer.writerow(row)

    # ── Export PDF ────────────────────────────────────────────────────────────

    def to_pdf(self, output_path: str = "report.pdf"):

        pdf = UTF8PDF()
        pdf.add_page()

        # ── 1. En-tête ────────────────────────────────────────────────────────
        pdf.set_font("Times", "B", 16)
        pdf.cell(0, 12, _clean(REPORT_TITLE), ln=True, align="C")
        pdf.ln(2)
        pdf.key_value("Video analysee", self.video_name)
        pdf.key_value("Date de generation", datetime.now().strftime("%d/%m/%Y a %H:%M"))
        pdf.key_value("Frames analysees", str(len(self.results)))
        pdf.ln(4)

        # ── 2. Analyse vocale ─────────────────────────────────────────────────
        if self.voice_results and "error" not in self.voice_results:
            pdf.section_title("Analyse vocale")
            vocal_keys = ["rms", "pitch_mean", "pitch_std", "zcr", "stress_score"]
            for k in vocal_keys:
                if k in self.voice_results:
                    pdf.key_value(k, str(self.voice_results[k]))
            pdf.ln(3)

        # ── 3. Répartition émotionnelle ───────────────────────────────────────
        pdf.section_title("Statistiques emotionnelles")

        dominants = [
            item.get("dominant_emotion", "N/A")
            for item in self.results
            if item.get("dominant_emotion") not in ("N/A", None)
        ]
        top_emotions = Counter(dominants).most_common(3)
        pdf.set_font("Times", "B", 10)
        pdf.cell(0, 7, "Top 3 emotions dominantes :", ln=True)
        pdf.set_font("Times", "", 10)
        for emo, count in top_emotions:
            pct = round(count / len(dominants) * 100, 1) if dominants else 0
            pdf.cell(0, 6, f"  - {_clean(emo)} : {count} frame(s) ({pct}%)", ln=True)

        if self.category_breakdown:
            pdf.ln(2)
            pdf.set_font("Times", "B", 10)
            pdf.cell(0, 7, "Repartition par categorie :", ln=True)
            pdf.set_font("Times", "", 10)
            for cat in ["positive", "negative", "neutral"]:
                val = self.category_breakdown.get(cat, 0.0)
                pdf.cell(0, 6, f"  - {cat.capitalize()} : {val}%", ln=True)
            dominant_cat = self.category_breakdown.get("dominant_category", "N/A")
            pdf.set_font("Times", "B", 10)
            pdf.cell(0, 7, f"  Categorie dominante : {_clean(dominant_cat)}", ln=True)
        pdf.ln(3)

        # ── 4. Dissonance émotionnelle ────────────────────────────────────────
        if self.dissonance:
            pdf.section_title("Dissonance emotionnelle")
            pdf.key_value(
                "Score de dissonance",
                str(self.dissonance.get("dissonance_score", "N/A")),
            )
            pdf.body_text(self.dissonance.get("interpretation", ""))
            pdf.ln(2)

        # ── 5. Résumé comportemental ──────────────────────────────────────────
        pdf.section_title("Resume comportemental")
        pdf.body_text(self.behavior_summary)
        pdf.ln(2)

        # ── 6. Analyse de sincérité ───────────────────────────────────────────
        if self.truth_analysis:
            pdf.section_title("Indicateur de sincerite")
            score = self.truth_analysis.get("truth_score", "N/A")
            verdict = self.truth_analysis.get("verdict", "Indetermine")
            expl = self.truth_analysis.get("explanation", "")
            disclaimer = self.truth_analysis.get("disclaimer", "")
            pdf.key_value("Score", str(score))
            pdf.key_value("Verdict", verdict)
            pdf.body_text(f"Explication : {expl}")
            if disclaimer:
                pdf.set_font("Times", "I", 9)
                pdf.multi_cell(0, 5, _clean(disclaimer))
            pdf.ln(2)

        # ── 7. Analyse Q/R ────────────────────────────────────────────────────
        if self.qa_analysis and "error" not in self.qa_analysis:
            pdf.section_title("Analyse de pertinence Question / Reponse")
            pdf.key_value("Question", self.qa_analysis.get("question", "N/A"))
            pdf.key_value("Reponse", self.qa_analysis.get("response", "N/A"))
            pdf.key_value(
                "Similarite", str(self.qa_analysis.get("similarity_score", "N/A"))
            )
            pdf.key_value("Verdict", self.qa_analysis.get("verdict", "N/A"))
            pdf.body_text(self.qa_analysis.get("explanation", ""))
            pdf.ln(2)

        # ── 8. Frames émotionnelles fortes ────────────────────────────────────
        if self.top_emotion_frames:
            pdf.section_title("Frames emotionnelles les plus expressives")
            for item in self.top_emotion_frames:
                suspect_tag = " [!]" if item.get("is_suspect") else ""
                derived_tag = " (inferee)" if item.get("is_derived_dominant") else ""
                pdf.body_text(
                    f"- {item['frame']} -> {item['dominant_emotion']}"
                    f"{suspect_tag}{derived_tag} (intensite : {item['intensity']})"
                )
            pdf.ln(2)

        # ── 9. Détail frame par frame ─────────────────────────────────────────
        pdf.section_title("Detail par frame")

        for i, item in enumerate(self.results):
            frame_filename = item.get("frame", f"frame_{i + 1}.jpg")
            dominant = item.get("dominant_emotion", "N/A")
            emotions = item.get("emotions", {})
            derived = item.get("derived_emotions", {})
            is_suspect = item.get("is_suspect", False)

            # Image de la frame si disponible
            frame_path = os.path.join(FRAMES_FOLDER, frame_filename)
            if os.path.isfile(frame_path) and frame_path.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                if pdf.y > 200:
                    pdf.add_page()
                try:
                    pdf.image(frame_path, w=100)
                    pdf.ln(2)
                except Exception:
                    pass  # Image corrompue → on l'ignore sans crasher

            suspect_tag = "  [!] Emotion suspecte" if is_suspect else ""
            pdf.set_font("Times", "B", 10)
            pdf.cell(
                0, 7, _clean(f"Frame {i + 1} - {frame_filename}{suspect_tag}"), ln=True
            )
            pdf.set_font("Times", "", 10)
            pdf.cell(0, 6, _clean(f"  Emotion dominante : {dominant}"), ln=True)

            for k, v in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
                pdf.cell(0, 5, f"    {_clean(k)} : {round(float(v), 2)}", ln=True)

            if derived:
                pdf.set_font("Times", "I", 9)
                pdf.cell(0, 5, "  Emotions inferees (heuristique) :", ln=True)
                for k, v in derived.items():
                    pdf.cell(0, 5, f"    {_clean(k)} : {round(float(v), 2)}", ln=True)
                pdf.set_font("Times", "", 10)

            pdf.ln(4)

        # ── 10. Limites de l'analyse ──────────────────────────────────────────
        pdf.add_page()
        pdf.section_title("Limites de l'analyse")
        limits = [
            "- Les emotions dites 'inferees' (nervous, excited, confused...) sont "
            "calculees par des regles heuristiques et non detectees directement par "
            "un modele entraine. Elles constituent des approximations.",
            "- L'indicateur de sincerite repose sur des seuils empiriques non "
            "calibres sur un corpus annote. Il ne constitue pas une preuve de "
            "mensonge et ne doit pas etre utilise a des fins legales.",
            "- L'analyse faciale peut etre affectee par la qualite video, "
            "l'eclairage, l'angle de la camera et les occultations du visage.",
            "- La transcription Whisper peut contenir des erreurs sur les noms "
            "propres, les accents regionaux ou en environnement bruite.",
            "- L'analyse de pertinence Q/R mesure une similarite semantique, "
            "pas une verite factuelle.",
            "- Ce systeme est un outil d'aide a l'analyse et non un systeme de "
            "detection automatisee du mensonge. Toute interpretation doit etre "
            "faite par un professionnel qualifie.",
        ]
        for limit in limits:
            pdf.body_text(limit)
            pdf.ln(1)

        pdf.output(output_path)
