import os
import cv2
from typing import List

# ── Constantes ────────────────────────────────────────────────────────────────

DEFAULT_FPS    = 0.3   # 1 frame toutes les ~3 secondes
FRAME_FORMAT   = "jpg" # Format de fichier pour les frames extraites (jpg ou png)


# ── Fonction principale ───────────────────────────────────────────────────────
def extract_frames(
    video_path:     str,
    output_folder:  str,
    fps:            float = DEFAULT_FPS
) -> List[str]:
    """
    Extrait des frames d'une vidéo à intervalle régulier.

    CORRECTION : la fonction retourne maintenant la liste des chemins
    des frames extraites — indispensable pour analyzer.py qui doit
    savoir où se trouvent les images à analyser.

    CORRECTION : ajout d'un bloc try/finally pour libérer la capture
    vidéo même en cas d'exception.

    CORRECTION : vérification que la vidéo source existe avant ouverture.

    Args:
        video_path    : Chemin vers la vidéo source.
        output_folder : Dossier de destination des frames extraites.
        fps           : Nombre de frames à extraire par seconde de vidéo.
                        0.3 = 1 frame toutes les ~3 secondes.
                        1.0 = 1 frame par seconde.

    Returns:
        List[str] : Liste ordonnée des chemins absolus des frames extraites.

    Raises:
        FileNotFoundError : Si la vidéo source n'existe pas.
        ValueError        : Si la fréquence de la vidéo est illisible.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : '{video_path}'")

    os.makedirs(output_folder, exist_ok=True)

    vidcap = cv2.VideoCapture(video_path)

    try:
        video_fps = vidcap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0:
            raise ValueError(
                f"Impossible de lire la fréquence de '{video_path}'. "
                f"Vérifiez que le fichier est une vidéo valide."
            )

        # Intervalle entre les frames à extraire
        frame_interval = max(1, int(round(video_fps / fps)))

        frame_paths: List[str] = []
        count  = 0
        saved  = 0

        success, image = vidcap.read()

        while success:
            if count % frame_interval == 0:
                filename   = f"frame_{saved:04d}.{FRAME_FORMAT}"
                frame_path = os.path.join(output_folder, filename)
                cv2.imwrite(frame_path, image)
                # CORRECTION : on accumule le chemin absolu de chaque frame
                frame_paths.append(os.path.abspath(frame_path))
                saved += 1

            success, image = vidcap.read()
            count += 1

    finally:
        # CORRECTION : libération garantie même en cas d'exception
        vidcap.release()

    return frame_paths


# ── Nettoyage des frames temporaires ─────────────────────────────────────────

def clear_frames(output_folder: str):
    """
    Supprime toutes les frames extraites du dossier temporaire.
    À appeler après l'analyse pour libérer l'espace disque.

    Args:
        output_folder : Dossier contenant les frames à supprimer.
    """
    if not os.path.isdir(output_folder):
        return

    removed = 0
    for filename in os.listdir(output_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            file_path = os.path.join(output_folder, filename)
            try:
                os.remove(file_path)
                removed += 1
            except OSError as e:
                print(f"[video_processing] Impossible de supprimer '{file_path}' : {e}")

    print(f"[video_processing] {removed} frame(s) supprimée(s) de '{output_folder}'.")


# ── Informations sur la vidéo ─────────────────────────────────────────────────

def get_video_info(video_path: str) -> dict:
    """
    Retourne les métadonnées principales d'une vidéo.
    Utile pour afficher les informations dans l'interface Streamlit
    et pour calibrer l'extraction de frames.

    Args:
        video_path : Chemin vers la vidéo.

    Returns:
        dict : {
            "duration_sec"  : float,  durée totale en secondes
            "fps"           : float,  fréquence d'images native
            "total_frames"  : int,    nombre total de frames
            "width"         : int,    largeur en pixels
            "height"        : int,    hauteur en pixels
            "resolution"    : str,    ex: "1920x1080"
        }
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : '{video_path}'")

    vidcap = cv2.VideoCapture(video_path)
    try:
        fps          = vidcap.get(cv2.CAP_PROP_FPS)
        total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        width        = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height       = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration_sec = round(total_frames / fps, 2) if fps > 0 else 0.0

        return {
            "duration_sec":  duration_sec,
            "fps":           round(fps, 2),
            "total_frames":  total_frames,
            "width":         width,
            "height":        height,
            "resolution":    f"{width}x{height}",
        }
    finally:
        vidcap.release()