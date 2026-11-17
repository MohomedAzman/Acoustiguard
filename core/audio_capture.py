
#Real-time audio capture from microphone 


import numpy as np
import sounddevice as sd
from typing import Optional, Callable
import threading
import time


class AudioCaptureError(Exception):
    """Custom exception for audio capture errors."""
    pass


class AudioCapture:

    #Handles microphone audio capture with progress callbacks.

    
    def __init__(
        self,
        duration: float = 10.0,
        sample_rate: int = 44100,
        device: Optional[int] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ):
        
        #Initialize audio capture.
        
        self.duration = duration
        self.sample_rate = sample_rate
        self.device = device
        self.progress_callback = progress_callback
        
        self.audio_data: Optional[np.ndarray] = None
        self.is_recording = False
        self.is_cancelled = False
        self._capture_thread: Optional[threading.Thread] = None
        self._error: Optional[str] = None
    
    def start_capture(self) -> None:

        if self.is_recording:
            raise AudioCaptureError("Capture already in progress")
        
        self.is_recording = True
        self.is_cancelled = False
        self._error = None
        self.audio_data = None
        
        # Start capture in background thread
        self._capture_thread = threading.Thread(target=self._capture_worker, daemon=True)
        self._capture_thread.start()
    
    def _capture_worker(self) -> None:

        try:
            self._report_progress(0, "Initializing microphone...")
            
            # Calculate number of samples
            num_samples = int(self.duration * self.sample_rate)
            
            self._report_progress(5, "Starting audio capture...")
            
            # Record audio
            # We'll use a callback-based approach for progress updates
            recording = []
            samples_per_chunk = int(self.sample_rate * 0.1)  # 100ms chunks
            num_chunks = int(num_samples / samples_per_chunk)
            
            def audio_callback(indata, frames, time_info, status):
                """Called by sounddevice for each audio chunk."""
                if status:
                    print(f"Audio callback status: {status}")
                recording.append(indata.copy())
            
            # Open stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                device=self.device,
                callback=audio_callback
            ):
                # Record in chunks to update progress
                for chunk_idx in range(num_chunks):
                    if self.is_cancelled:
                        self._report_progress(100, "Capture cancelled")
                        return
                    
                    # Sleep for chunk duration
                    time.sleep(samples_per_chunk / self.sample_rate)
                    
                    # Update progress (10-90% range during capture)
                    progress = 10 + int((chunk_idx / num_chunks) * 80)
                    elapsed = (chunk_idx + 1) * samples_per_chunk / self.sample_rate
                    self._report_progress(
                        progress,
                        f"Capturing audio... {elapsed:.1f}s / {self.duration:.1f}s"
                    )
            
            self._report_progress(90, "Processing captured audio...")
            
            # Concatenate all chunks
            if recording:
                self.audio_data = np.concatenate(recording, axis=0)
                
                # Flatten to 1D array if needed
                if self.audio_data.ndim > 1:
                    self.audio_data = self.audio_data.flatten()
                
                # Normalize to [-1, 1] range
                max_val = np.max(np.abs(self.audio_data))
                if max_val > 0:
                    self.audio_data = self.audio_data / max_val
                
                self._report_progress(100, "Capture complete")
            else:
                raise AudioCaptureError("No audio data captured")
                
        except Exception as e:
            self._error = str(e)
            self._report_progress(0, f"Error: {str(e)}")
        finally:
            self.is_recording = False
    
    def _report_progress(self, percent: int, message: str) -> None:
        """Report progress via callback if provided."""
        if self.progress_callback:
            try:
                self.progress_callback(percent, message)
            except Exception as e:
                print(f"Progress callback error: {e}")
    
    def cancel(self) -> None:
        """Cancel ongoing capture."""
        self.is_cancelled = True
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:

        if self._capture_thread is None:
            return False
        
        self._capture_thread.join(timeout=timeout)
        
        return not self.is_recording and self._error is None
    
    def get_audio_data(self) -> np.ndarray:

        if self.is_recording:
            raise AudioCaptureError("Capture still in progress")
        
        if self._error:
            raise AudioCaptureError(f"Capture failed: {self._error}")
        
        if self.audio_data is None:
            raise AudioCaptureError("No audio data available")
        
        return self.audio_data
    
    def get_audio_info(self) -> dict:
 
        if self.audio_data is None:
            return {}
        
        return {
            'duration_seconds': len(self.audio_data) / self.sample_rate,
            'sample_rate': self.sample_rate,
            'num_samples': len(self.audio_data),
            'rms_level': float(np.sqrt(np.mean(self.audio_data ** 2))),
            'peak_level': float(np.max(np.abs(self.audio_data))),
        }


def capture_audio_simple(
    duration: float = 10.0,
    device: Optional[int] = None,
    sample_rate: int = 44100
) -> np.ndarray:
    """
    Simple blocking audio capture (for testing/simple use cases).
    
    Args:
        duration: Recording duration in seconds
        device: Microphone device index (None for default)
        sample_rate: Sample rate in Hz
        
    Returns:
        numpy array of audio samples
    """
    try:
        num_samples = int(duration * sample_rate)
        
        print(f"Recording {duration}s of audio...")
        recording = sd.rec(
            num_samples,
            samplerate=sample_rate,
            channels=1,
            device=device,
            blocking=True
        )
        
        # Flatten and normalize
        audio = recording.flatten()
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        
        print(f"Capture complete: {len(audio)} samples")
        return audio
        
    except Exception as e:
        raise AudioCaptureError(f"Audio capture failed: {e}")


