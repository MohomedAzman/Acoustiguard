#Audio preprocessing and validation for AcoustiGuard.


import numpy as np
from typing import Tuple, Optional


class AudioProcessingError(Exception):
    """Custom exception for audio processing errors."""
    pass


def validate_audio(audio: np.ndarray, sample_rate: int) -> Tuple[bool, str]:

    try:
        # Check if audio exists
        if audio is None or len(audio) == 0:
            return False, "Audio data is empty"
        
        # Check if audio is too short
        min_duration = 1.0  # Minimum 1 second
        duration = len(audio) / sample_rate
        if duration < min_duration:
            return False, f"Audio too short ({duration:.2f}s), need at least {min_duration}s"
        
        # Check if audio is silent
        rms = np.sqrt(np.mean(audio ** 2))
        if rms < 0.0001:
            return False, "Audio appears to be silent (no signal detected)"
        
        # Check for clipping (values outside [-1, 1])
        if np.max(np.abs(audio)) > 1.1:
            return False, "Audio signal is clipped (values exceed expected range)"
        
        # Check for NaN or Inf values
        if np.any(np.isnan(audio)) or np.any(np.isinf(audio)):
            return False, "Audio contains invalid values (NaN or Inf)"
        
        return True, "Audio validation passed"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def normalize_audio(audio: np.ndarray, target_level: float = 0.8) -> np.ndarray:

    peak = np.max(np.abs(audio))
    if peak > 0:
        return audio * (target_level / peak)
    return audio


def remove_dc_offset(audio: np.ndarray) -> np.ndarray:

    return audio - np.mean(audio)


def apply_simple_noise_reduction(
    audio: np.ndarray,
    threshold_db: float = -40.0
) -> np.ndarray:

    # Convert to dB
    rms = np.sqrt(np.mean(audio ** 2))
    if rms == 0:
        return audio
    
    audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
    threshold_linear = 10 ** (threshold_db / 20.0)
    
    # Apply gate (soft gate with smooth transition)
    mask = np.abs(audio) > threshold_linear
    return audio * mask


def preprocess_audio(
    audio: np.ndarray,
    sample_rate: int,
    remove_dc: bool = True,
    normalize: bool = True,
    noise_gate: bool = False
) -> Tuple[np.ndarray, dict]:

    # Validate input
    is_valid, message = validate_audio(audio, sample_rate)
    if not is_valid:
        raise AudioProcessingError(f"Audio validation failed: {message}")
    
    processed = audio.copy()
    info = {
        'original_duration': len(audio) / sample_rate,
        'original_rms': float(np.sqrt(np.mean(audio ** 2))),
        'original_peak': float(np.max(np.abs(audio))),
        'sample_rate': sample_rate,
    }
    
    # Remove DC offset
    if remove_dc:
        dc_offset = np.mean(processed)
        processed = remove_dc_offset(processed)
        info['dc_offset_removed'] = float(dc_offset)
    
    # Apply noise gate if requested
    if noise_gate:
        original_energy = np.sum(processed ** 2)
        processed = apply_simple_noise_reduction(processed)
        gated_energy = np.sum(processed ** 2)
        info['noise_gate_applied'] = True
        info['energy_reduction'] = float(1.0 - (gated_energy / original_energy)) if original_energy > 0 else 0.0
    
    # Normalize
    if normalize:
        original_peak = np.max(np.abs(processed))
        processed = normalize_audio(processed, target_level=0.8)
        new_peak = np.max(np.abs(processed))
        info['normalized'] = True
        info['normalization_gain'] = float(new_peak / original_peak) if original_peak > 0 else 1.0
    
    # Final stats
    info['processed_rms'] = float(np.sqrt(np.mean(processed ** 2)))
    info['processed_peak'] = float(np.max(np.abs(processed)))
    info['processed_duration'] = len(processed) / sample_rate
    
    return processed, info


def segment_audio(
    audio: np.ndarray,
    sample_rate: int,
    segment_duration: float = 1.0,
    overlap: float = 0.5
) -> list:

    segment_samples = int(segment_duration * sample_rate)
    hop_samples = int(segment_samples * (1 - overlap))
    
    segments = []
    start = 0
    
    while start + segment_samples <= len(audio):
        segment = audio[start:start + segment_samples]
        segments.append(segment)
        start += hop_samples
    
    # Add final partial segment if any
    if start < len(audio):
        segment = audio[start:]
        segments.append(segment)
    
    return segments


def get_audio_statistics(audio: np.ndarray, sample_rate: int) -> dict:

    return {
        'duration_seconds': len(audio) / sample_rate,
        'num_samples': len(audio),
        'sample_rate': sample_rate,
        'rms_level': float(np.sqrt(np.mean(audio ** 2))),
        'peak_level': float(np.max(np.abs(audio))),
        'mean': float(np.mean(audio)),
        'std_dev': float(np.std(audio)),
        'min_value': float(np.min(audio)),
        'max_value': float(np.max(audio)),
    }


