import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import time
import sys
from pathlib import Path
from typing import Optional


class MaskingEngine:

    
    def __init__(self, sample_rate: int = 44100, audio_file: Optional[str] = None):
 
        self.sample_rate = sample_rate
        self.volume = 0.65
        self.is_playing = False
        self._play_thread = None
        self._stream = None
        self._stop_flag = threading.Event()
        self._audio_buffer = None
        self._buffer_position = 0
        
        # Default audio file path - hardcoded to user's file
        if getattr(sys, "frozen", False):
           resource_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        else:
           resource_dir = Path(__file__).resolve().parent.parent
    
        self.default_audio_file = str(resource_dir / "masking audio.mpeg")
        
        # Load the audio file
        self._load_audio_file(audio_file or self.default_audio_file)
    
    def _load_audio_file(self, file_path: str) -> bool:

        try:
            data, file_sr = sf.read(file_path, dtype='float32')
            
            # Convert to mono if stereo
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = np.mean(data, axis=1)
            
            # Resample if needed
            if file_sr != self.sample_rate:
                ratio = self.sample_rate / file_sr
                new_length = int(len(data) * ratio)
                old_indices = np.linspace(0, len(data) - 1, new_length)
                data = np.interp(old_indices, np.arange(len(data)), data)
            
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(data))
            if max_val > 0:
                data = data / max_val * 0.95
            
            self._audio_buffer = data.astype(np.float32)
            self._buffer_position = 0
            
            print(f"Loaded masking audio: {len(data)/self.sample_rate:.2f}s at {self.sample_rate}Hz")
            return True
            
        except Exception as e:
            print(f"Error loading audio file {file_path}: {e}")
            print("Falling back to generated masking sounds...")
            self._audio_buffer = None
            return False
    
    def set_volume(self, volume: float) -> None:

        self.volume = max(0.0, min(1.0, volume))
    
    def start_masking(self) -> None:
        """Start playing acoustic masking sounds."""
        if self.is_playing:
            return
        
        if self._audio_buffer is None:
            print("No audio buffer loaded, cannot start masking")
            return
        
        self.is_playing = True
        self._stop_flag.clear()
        
        self._play_thread = threading.Thread(target=self._play_masking_loop, daemon=True)
        self._play_thread.start()
    
    def stop_masking(self) -> None:
        """Stop playing acoustic masking sounds."""
        if not self.is_playing:
            return
        
        self.is_playing = False
        self._stop_flag.set()
        
        if self._play_thread:
            self._play_thread.join(timeout=2.0)
        
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
    
    def _play_masking_loop(self) -> None:
        """Background worker that continuously plays the masking audio."""
        try:
            self._stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=4096,
                callback=self._audio_callback
            )
            
            self._stream.start()
            
            while not self._stop_flag.is_set():
                time.sleep(0.1)
            
        except Exception as e:
            print(f"Masking playback error: {e}")
        finally:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
    
    def _audio_callback(self, outdata, frames, time_info, status):

        if status:
            print(f"Stream status: {status}")
        
        if self._audio_buffer is None:
            outdata[:, 0] = 0
            return
        
        remaining = frames
        out_idx = 0
        
        while remaining > 0:
            available = len(self._audio_buffer) - self._buffer_position
            chunk_size = min(remaining, available)
            
            outdata[out_idx:out_idx + chunk_size, 0] = self._audio_buffer[self._buffer_position:self._buffer_position + chunk_size] * self.volume
            
            self._buffer_position += chunk_size
            out_idx += chunk_size
            remaining -= chunk_size
            
            if self._buffer_position >= len(self._audio_buffer):
                self._buffer_position = 0
    
    def get_duration(self) -> float:
        """Get duration of loaded audio in seconds."""
        if self._audio_buffer is not None:
            return len(self._audio_buffer) / self.sample_rate
        return 0.0
    
    def set_audio_file(self, file_path: str) -> bool:

        was_playing = self.is_playing
        if was_playing:
            self.stop_masking()
        
        success = self._load_audio_file(file_path)
        
        if was_playing and success:
            self.start_masking()
        
        return success


