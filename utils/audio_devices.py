"""
utils/audio_devices.py
Audio device enumeration and management for AcoustiGuard.
Handles microphone detection, selection, and availability checking.
"""

import sounddevice as sd
from typing import List, Dict, Optional, Tuple


class AudioDeviceError(Exception):
    """Custom exception for audio device related errors."""
    pass


def get_available_microphones() -> List[Dict]:
    """
    Get list of available input (microphone) devices.
    
    Returns:
        List of dictionaries containing device information:
        - index: Device index
        - name: Device name
        - channels: Number of input channels
        - sample_rate: Default sample rate
    """
    try:
        devices = sd.query_devices()
        microphones = []
        
        for idx, device in enumerate(devices):
            # Only include devices with input channels (microphones)
            if device['max_input_channels'] > 0:
                microphones.append({
                    'index': idx,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': int(device['default_samplerate']),
                    'is_default': idx == sd.default.device[0]
                })
        
        return microphones
        
    except Exception as e:
        raise AudioDeviceError(f"Failed to query audio devices: {e}")


def get_default_microphone() -> Optional[Dict]:
    """
    Get the default input device (microphone).
    
    Returns:
        Dictionary with default microphone info, or None if not available
    """
    try:
        default_input_idx = sd.default.device[0]
        if default_input_idx is None:
            return None
            
        device_info = sd.query_devices(default_input_idx)
        
        return {
            'index': default_input_idx,
            'name': device_info['name'],
            'channels': device_info['max_input_channels'],
            'sample_rate': int(device_info['default_samplerate']),
            'is_default': True
        }
        
    except Exception as e:
        return None


def check_microphone_available(device_index: Optional[int] = None) -> Tuple[bool, str]:
    """
    Check if a microphone is available and working.
    
    Args:
        device_index: Specific device index to check, or None for default
        
    Returns:
        Tuple of (is_available, message)
    """
    try:
        # Try to query the device
        if device_index is not None:
            device = sd.query_devices(device_index)
        else:
            default_idx = sd.default.device[0]
            if default_idx is None:
                return False, "No default microphone found"
            device = sd.query_devices(default_idx)
        
        # Check if device has input channels
        if device['max_input_channels'] < 1:
            return False, f"Device '{device['name']}' has no input channels"
        
        # Try a quick test recording to verify it actually works
        try:
            test_duration = 0.1  # 100ms test
            sample_rate = int(device['default_samplerate'])
            sd.rec(
                int(test_duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                device=device_index,
                blocking=True
            )
            return True, f"Microphone '{device['name']}' is available"
            
        except Exception as e:
            return False, f"Microphone found but cannot record: {str(e)}"
            
    except Exception as e:
        return False, f"Error checking microphone: {str(e)}"


def get_microphone_names() -> List[str]:
    """
    Get list of microphone names for UI dropdown.
    
    Returns:
        List of microphone names (first one is default if available)
    """
    try:
        microphones = get_available_microphones()
        
        if not microphones:
            return ["No microphone found"]
        
        # Sort so default is first
        microphones.sort(key=lambda x: (not x['is_default'], x['name']))
        
        names = []
        for mic in microphones:
            prefix = "[Default] " if mic['is_default'] else ""
            names.append(f"{prefix}{mic['name']}")
        
        return names
        
    except Exception:
        return ["Error detecting microphones"]


def get_microphone_by_name(name: str) -> Optional[int]:
    """
    Get device index by microphone name.
    
    Args:
        name: Microphone name (with or without [Default] prefix)
        
    Returns:
        Device index or None if not found
    """
    # Remove [Default] prefix if present
    clean_name = name.replace("[Default] ", "")
    
    try:
        microphones = get_available_microphones()
        for mic in microphones:
            if mic['name'] == clean_name:
                return mic['index']
        return None
    except Exception:
        return None


def test_microphone(device_index: Optional[int] = None, duration: float = 1.0) -> Tuple[bool, str, Optional[float]]:
    """
    Perform a test recording to verify microphone functionality.
    
    Args:
        device_index: Device to test (None for default)
        duration: Test duration in seconds
        
    Returns:
        Tuple of (success, message, rms_level)
    """
    try:
        # Get device info
        if device_index is not None:
            device = sd.query_devices(device_index)
        else:
            default_idx = sd.default.device[0]
            if default_idx is None:
                return False, "No microphone found", None
            device = sd.query_devices(default_idx)
            device_index = default_idx
        
        sample_rate = int(device['default_samplerate'])
        
        # Record test audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            device=device_index,
            blocking=True
        )
        
        # Calculate RMS level to verify audio is being captured
        import numpy as np
        rms = float(np.sqrt(np.mean(recording**2)))
        
        if rms < 0.0001:
            return True, f"Microphone '{device['name']}' works but no sound detected", rms
        else:
            return True, f"Microphone '{device['name']}' is working correctly", rms
            
    except Exception as e:
        return False, f"Microphone test failed: {str(e)}", None


# Quick diagnostic function
def print_audio_info():
    """Print audio device information for debugging."""
    print("\n=== Audio Device Information ===\n")
    
    try:
        microphones = get_available_microphones()
        print(f"Found {len(microphones)} microphone(s):\n")
        
        for i, mic in enumerate(microphones, 1):
            default_marker = " [DEFAULT]" if mic['is_default'] else ""
            print(f"{i}. {mic['name']}{default_marker}")
            print(f"   Index: {mic['index']}")
            print(f"   Channels: {mic['channels']}")
            print(f"   Sample Rate: {mic['sample_rate']} Hz")
            
            # Test availability
            available, msg = check_microphone_available(mic['index'])
            status = "OK" if available else "UNAVAILABLE"
            print(f"   Status: {status} - {msg}")
            print()
            
    except Exception as e:
        print(f"Error querying audio devices: {e}")
    
    print("=" * 35)


if __name__ == "__main__":
    # Run diagnostics when executed directly
    print_audio_info()
    
    # Test default microphone
    print("\nTesting default microphone (1 second)...")
    success, message, rms = test_microphone(duration=1.0)
    print(f"Result: {message}")
    if rms is not None:
        print(f"RMS Level: {rms:.6f}")
