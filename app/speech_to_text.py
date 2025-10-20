import whisper # Importe la bibliothèque Whisper pour la transcription audio
import os # Importe le module os pour la gestion des fichiers
import tempfile # Importe tempfile pour créer des fichiers temporaires
import subprocess # Importe subprocess pour exécuter des commandes système (ici ffmpeg)

def extract_audio_from_video(video_path, output_audio_path="temp_audio.wav"):
    """
    Utilise ffmpeg pour extraire l'audio d'une vidéo et le sauvegarder en .wav
    """
    command = [
        "ffmpeg", "-y", "-i", video_path, # Commande ffmpeg, -y écrase le fichier de sortie, -i spécifie la vidéo source
        "-ac", "1",                       # Définit l'audio en mono (1 canal)
        "-ar", "16000",                   # Définit le taux d'échantillonnage à 16 kHz
        "-vn",                            # Ignore la vidéo (n'extrait que l'audio)
        output_audio_path                 # Chemin du fichier audio de sortie
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # Exécute la commande ffmpeg sans afficher la sortie
    return output_audio_path # Retourne le chemin du fichier audio extrait

def transcribe_audio_whisper(audio_path, model_size="base"):
    """
    Transcrit l'audio en texte à l'aide de Whisper.
    """
    model = whisper.load_model(model_size) # Charge le modèle Whisper de la taille spécifiée
    result = model.transcribe(audio_path, language="fr")  # Transcrit l'audio en français (ou autre langue si modifié)
    return result.get("text", "")  # Retourne le texte transcrit, ou une chaîne vide si absent

def transcribe_video(video_path, model_size="base"):
    """
    Pipeline complet : extrait l'audio d'une vidéo, puis effectue la transcription.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio: # Crée un fichier temporaire pour stocker l'audio extrait
        audio_path = tmp_audio.name                                             # Récupère le chemin du fichier temporaire

    extract_audio_from_video(video_path, audio_path)                            # Extrait l'audio de la vidéo dans le fichier temporaire
    text = transcribe_audio_whisper(audio_path, model_size)                     # Transcrit l'audio extrait en texte

    if os.path.exists(audio_path):       # Vérifie si le fichier audio temporaire existe
        os.remove(audio_path)            # Supprime le fichier temporaire pour nettoyer
    return text                          # Retourne le texte transcrit
