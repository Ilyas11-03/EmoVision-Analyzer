import torchaudio  # Pour charger et traiter les fichiers audio
import torch # Pour utiliser les modèles de deep learning
import os # Pour gérer les fichiers et le système

# Modèle fictif à remplacer par ton vrai modèle entraîné
class DummyEmotionModel(torch.nn.Module):

    def __init__(self):

        super().__init__() # Initialise la classe parente
        self.fc = torch.nn.Linear(40, 10)  # Couche linéaire (entrée: 40, sortie: 10 émotions)

    def forward(self, x):
         # Applique la couche linéaire puis softmax pour obtenir des probabilités
        return torch.softmax(self.fc(x.mean(dim=1)), dim=-1)

# Liste des émotions à détecter
EMOTIONS = ["happy", "sad", "angry", "neutral","bored", "excited", "confused","suprise","disgust","fear"]  # Liste des émotions à détecter

def extract_audio_emotions(video_path):
    try:
         # Chemin temporaire pour sauvegarder l'audio extrait
        audio_path = "temp_audio.wav"
         # Utilise ffmpeg pour extraire l'audio de la vidéo, mono, 16kHz
        os.system(f'ffmpeg -y -i "{video_path}" -ac 1 -ar 16000 "{audio_path}"')
        # Charge l'audio extrait
        waveform, sample_rate = torchaudio.load(audio_path)
         # Extrait les coefficients MFCC (caractéristiques audio)
        mfcc = torchaudio.transforms.MFCC(sample_rate=sample_rate, n_mfcc=40)(waveform)
         # Transpose pour avoir la bonne forme (batch, time, features)
        mfcc = mfcc.transpose(1, 2)

        model = DummyEmotionModel()   # Instancie le modèle (à remplacer par ton vrai modèle)
        with torch.no_grad(): # Désactive le calcul du gradient (inférence)
            output = model(mfcc) # Prédit la distribution des émotions

        scores = output.squeeze().tolist() # Convertit les scores en liste
        dominant_idx = int(torch.argmax(output)) # Trouve l'indice de l'émotion dominante
        dominant_emotion = EMOTIONS[dominant_idx] # Récupère le nom de l'émotion dominante
         # Crée un dictionnaire avec le score de chaque émotion (en %)
        distribution = {EMOTIONS[i]: round(float(scores[i]) * 100, 2) for i in range(len(EMOTIONS))}
        
        # Supprime le fichier audio temporaire
        if os.path.exists(audio_path):
            os.remove(audio_path)
        # Retourne l'émotion dominante et la distribution des scores
        return {
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": distribution
        }
    except Exception as e:
         # En cas d'erreur, retourne le message d'erreur
        return {"error": str(e)}