import cv2
import os

def extract_frames(video_path, output_folder, fps=1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    vidcap = cv2.VideoCapture(video_path)
    video_fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps // fps)

    count, saved = 0, 0
    while True:
        success, frame = vidcap.read()
        if not success:
            break
        if count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{saved:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved += 1
        count += 1
    vidcap.release()