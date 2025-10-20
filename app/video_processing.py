import cv2  # Importation de la bibliothèque OpenCV pour le traitement vidéo
import os  # Importation du module os pour la gestion des fichiers et dossiers

def extract_frames(video_path, output_folder, fps=0.3): # 0.1 fps = 1 image toutes les 10 secondes
    
    if not os.path.exists(output_folder):  # Vérifie si le dossier de sortie existe
        os.makedirs(output_folder)  # Crée le dossier de sortie s'il n'existe pas

    vidcap = cv2.VideoCapture(video_path)  # Ouvre la vidéo pour la lecture
    video_fps = vidcap.get(cv2.CAP_PROP_FPS)  # Récupère le nombre d'images par seconde de la vidéo

    if video_fps == 0:
        raise ValueError("Impossible de lire la fréquence de la vidéo.")
    
    frame_interval = max(1, int(video_fps // fps))  # Calcule l'intervalle entre les frames à extraire
 
    count, saved = 0, 0  # Initialise les compteurs de frames lues et sauvegardées
 
    success, image = vidcap.read()  # Lit la première image de la vidéo, 'success' est True si la lecture a réussi, 'image' contient l'image lue.
    while success:  # Boucle tant que la lecture d'une image est réussie.
        if count % frame_interval == 0:  # Si le numéro de l'image est un multiple de 'frame_interval', on sauvegarde cette image.
            filename = os.path.join(output_folder, f"frame_{saved:04d}.jpg")  # Crée le chemin du fichier pour sauvegarder l'image, avec un numéro formaté sur 4 chiffres.
            cv2.imwrite(filename, image)  # Sauvegarde l'image actuelle dans le fichier spécifié.
            saved += 1  # Incrémente le compteur d'images sauvegardées.
        success, image = vidcap.read()  # Lit l'image suivante de la vidéo.
        count += 1  # Incrémente le compteur total d'images lues.
    
    vidcap.release()  # Libère les ressources utilisées par la