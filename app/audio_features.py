import librosa
import numpy as np

def extract_audio_features(file_path):
    y, sr = librosa.load(file_path, sr=None)

    rms = librosa.feature.rms(y=y).mean()
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_values = pitches[magnitudes > np.median(magnitudes)]
    pitch_mean = pitch_values.mean() if len(pitch_values) > 0 else 0
    pitch_std = pitch_values.std() if len(pitch_values) > 0 else 0

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfccs_mean = mfccs.mean(axis=1)
    mfccs_std = mfccs.std(axis=1)

    zcr = librosa.feature.zero_crossing_rate(y).mean()

    features = {
        "rms": rms,
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "zcr": zcr,
    }
    for i in range(13):
        features[f"mfcc{i+1}_mean"] = mfccs_mean[i]
        features[f"mfcc{i+1}_std"] = mfccs_std[i]

    return features
