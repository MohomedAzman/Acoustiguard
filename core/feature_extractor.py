import numpy as np
import librosa
from typing import Dict, Optional


class FeatureExtractionError(Exception):
    """Custom exception for feature extraction errors."""
    pass


def extract_acoustic_features(
    audio: np.ndarray,
    sample_rate: int = 44100
) -> Dict[str, float]:

    try:
        features = {}
        
        # 1. RMS Energy - Overall loudness/energy
        rms = librosa.feature.rms(y=audio)[0]
        features['rms_energy'] = float(np.mean(rms))
        features['rms_std'] = float(np.std(rms))
        features['rms_max'] = float(np.max(rms))
        
        # 2. Spectral Centroid - "Brightness" of sound
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
        features['spectral_centroid'] = float(np.mean(spectral_centroid))
        features['spectral_centroid_std'] = float(np.std(spectral_centroid))
        
        # 3. Spectral Bandwidth - Spread of spectrum
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
        features['spectral_bandwidth'] = float(np.mean(spectral_bandwidth))
        features['spectral_bandwidth_std'] = float(np.std(spectral_bandwidth))
        
        # 4. Spectral Rolloff - Frequency rolloff point
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate, roll_percent=0.85)[0]
        features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
        features['spectral_rolloff_std'] = float(np.std(spectral_rolloff))
        
        # 5. Zero Crossing Rate - Related to noisiness
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        features['zero_crossing_rate'] = float(np.mean(zcr))
        features['zero_crossing_rate_std'] = float(np.std(zcr))
        
        # 6. Spectral Flatness - Measure of tone vs noise
        spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0]
        features['spectral_flatness'] = float(np.mean(spectral_flatness))
        
        # 7. Tempo estimation - Rhythmic content
        try:
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
            features['tempo'] = float(tempo)
        except Exception:
            features['tempo'] = 0.0
        
        # 8. Chroma features - Harmonic content
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        features['chroma_energy'] = float(np.mean(chroma))
        features['chroma_std'] = float(np.std(chroma))
        
        # 9. Mel-frequency cepstral coefficients (MFCCs) - Spectral shape
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
        for i in range(min(5, mfccs.shape[0])):  # First 5 MFCCs
            features[f'mfcc_{i+1}'] = float(np.mean(mfccs[i]))
        
        # 10. Spectral Contrast - Difference between peaks and valleys
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sample_rate)
        features['spectral_contrast'] = float(np.mean(spectral_contrast))
        
        return features
        
    except Exception as e:
        raise FeatureExtractionError(f"Feature extraction failed: {str(e)}")


def extract_simple_features(
    audio: np.ndarray,
    sample_rate: int = 44100
) -> Dict[str, float]:

    try:
        features = {}
        
        # RMS Energy
        rms = librosa.feature.rms(y=audio)[0]
        features['rms_energy'] = float(np.mean(rms))
        
        # Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
        features['spectral_centroid'] = float(np.mean(spectral_centroid))
        
        # Spectral Bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
        features['spectral_bandwidth'] = float(np.mean(spectral_bandwidth))
        
        # Spectral Rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
        features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
        
        # Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        features['zero_crossing_rate'] = float(np.mean(zcr))
        
        return features
        
    except Exception as e:
        raise FeatureExtractionError(f"Simple feature extraction failed: {str(e)}")


def analyze_frequency_content(
    audio: np.ndarray,
    sample_rate: int = 44100
) -> Dict[str, float]:

    try:
        # Compute FFT
        fft = np.fft.rfft(audio)
        frequencies = np.fft.rfftfreq(len(audio), 1/sample_rate)
        magnitude = np.abs(fft)
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(magnitude)
        dominant_frequency = frequencies[dominant_freq_idx]
        
        # Calculate energy in different frequency bands
        # Low: 0-500 Hz, Mid: 500-2000 Hz, High: 2000+ Hz
        low_band = (frequencies < 500)
        mid_band = (frequencies >= 500) & (frequencies < 2000)
        high_band = (frequencies >= 2000)
        
        total_energy = np.sum(magnitude ** 2)
        
        return {
            'dominant_frequency': float(dominant_frequency),
            'low_freq_energy': float(np.sum(magnitude[low_band] ** 2) / total_energy) if total_energy > 0 else 0.0,
            'mid_freq_energy': float(np.sum(magnitude[mid_band] ** 2) / total_energy) if total_energy > 0 else 0.0,
            'high_freq_energy': float(np.sum(magnitude[high_band] ** 2) / total_energy) if total_energy > 0 else 0.0,
        }
        
    except Exception as e:
        raise FeatureExtractionError(f"Frequency analysis failed: {str(e)}")


def extract_temporal_features(
    audio: np.ndarray,
    sample_rate: int = 44100
) -> Dict[str, float]:

    try:
        # Envelope
        envelope = np.abs(librosa.util.frame(audio, frame_length=2048, hop_length=512).max(axis=0))
        
        # Attack time (time to reach peak)
        peak_idx = np.argmax(envelope)
        attack_time = peak_idx * (512 / sample_rate)  # Convert frames to seconds
        
        # Decay characteristics
        if peak_idx < len(envelope) - 1:
            decay_envelope = envelope[peak_idx:]
            decay_rate = -np.mean(np.diff(decay_envelope)) if len(decay_envelope) > 1 else 0.0
        else:
            decay_rate = 0.0
        
        return {
            'attack_time': float(attack_time),
            'decay_rate': float(decay_rate),
            'envelope_variance': float(np.var(envelope)),
            'envelope_mean': float(np.mean(envelope)),
        }
        
    except Exception as e:
        return {
            'attack_time': 0.0,
            'decay_rate': 0.0,
            'envelope_variance': 0.0,
            'envelope_mean': 0.0,
        }


def get_feature_summary(features: Dict[str, float]) -> str:

    summary_lines = []
    
    # Key features for acoustic security
    if 'rms_energy' in features:
        energy_level = "High" if features['rms_energy'] > 0.3 else "Medium" if features['rms_energy'] > 0.1 else "Low"
        summary_lines.append(f"Energy Level: {energy_level} (RMS: {features['rms_energy']:.4f})")
    
    if 'spectral_centroid' in features:
        brightness = "Bright" if features['spectral_centroid'] > 3000 else "Medium" if features['spectral_centroid'] > 1500 else "Dark"
        summary_lines.append(f"Spectral Character: {brightness} ({features['spectral_centroid']:.0f} Hz)")
    
    if 'zero_crossing_rate' in features:
        noisiness = "Noisy" if features['zero_crossing_rate'] > 0.2 else "Moderate" if features['zero_crossing_rate'] > 0.1 else "Tonal"
        summary_lines.append(f"Signal Type: {noisiness} (ZCR: {features['zero_crossing_rate']:.4f})")
    
    return "\n".join(summary_lines)


