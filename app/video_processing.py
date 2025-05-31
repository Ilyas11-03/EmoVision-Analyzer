import cv2  # Importation de la bibliothèque OpenCV pour le traitement vidéo
import os  # Importation du module os pour la gestion des fichiers et dossiers

def extract_frames(video_path, output_folder, fps=1):
    if not os.path.exists(output_folder):  # Vérifie si le dossier de sortie existe
        os.makedirs(output_folder)  # Crée le dossier de sortie s'il n'existe pas

    vidcap = cv2.VideoCapture(video_path)  # Ouvre la vidéo pour la lecture
    video_fps = vidcap.get(cv2.CAP_PROP_FPS)  # Récupère le nombre d'images par seconde de la vidéo
    frame_interval = int(video_fps // fps)  # Calcule l'intervalle entre les frames à extraire

    count, saved = 0, 0  # Initialise les compteurs de frames lues et sauvegardées
    while True:
        success, frame = vidcap.read()  # Lit une frame de la vidéo
        if not success:  # Si la lecture échoue (fin de vidéo)
            break  # Sort de la boucle
        if count % frame_interval == 0:  # Si la frame doit être extraite selon l'intervalle
            frame_filename = os.path.join(output_folder, f"frame_{saved:04d}.jpg")  # Définit le nom du fichier image
            cv2.imwrite(frame_filename, frame)  # Sauvegarde la frame en tant qu'image
            saved += 1  # Incrémente le compteur de frames sauvegardées
        count += 1  # Incrémente le compteur de frames lues
    vidcap.release()  # Libère la ressource vidéo