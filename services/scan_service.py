import numpy as np
import time
from datetime import datetime
from typing import Optional, Callable

from core.audio_capture import AudioCapture, AudioCaptureError
from core.audio_processor import preprocess_audio, AudioProcessingError
from core.feature_extractor import extract_acoustic_features, analyze_frequency_content, FeatureExtractionError
from core.risk_engine import RiskEngine
from core.recommendation_engine import RecommendationEngine
from data.models import ScanResult, AcousticFeatures, RiskAssessment, Recommendation, ScanProgress
from data.database import init_database
from data.repository import ScanRepository


class ScanServiceError(Exception):
    """Custom exception for scan service errors."""
    pass


class ScanService:

    def __init__(self):
        self.risk_engine = RiskEngine()
        self.recommendation_engine = RecommendationEngine()
        self._current_scan = None
        self._progress_callback = None
    
    def run_scan(
        self,
        duration: float = 10.0,
        device: Optional[int] = None,
        progress_callback: Optional[Callable] = None,
        save_to_db: bool = True
    ) -> ScanResult:

        self._progress_callback = progress_callback
        start_time = time.time()
        
        try:
            # Stage 1: Audio Capture
            self._report(5, "Initializing microphone...", "capturing")
            
            capturer = AudioCapture(
                duration=duration,
                device=device,
                progress_callback=self._capture_progress_adapter
            )
            
            capturer.start_capture()
            
            if not capturer.wait_for_completion(timeout=duration + 10):
                raise ScanServiceError("Audio capture timed out")
            
            audio_data = capturer.get_audio_data()
            audio_info = capturer.get_audio_info()
            
            # Stage 2: Preprocessing
            self._report(75, "Preprocessing audio signal...", "processing")
            
            processed_audio, proc_info = preprocess_audio(
                audio_data,
                sample_rate=capturer.sample_rate,
                remove_dc=True,
                normalize=True,
                noise_gate=False
            )
            
            # Stage 3: Feature Extraction
            self._report(82, "Extracting acoustic features...", "analyzing")
            
            features = extract_acoustic_features(processed_audio, capturer.sample_rate)
            freq_features = analyze_frequency_content(processed_audio, capturer.sample_rate)
            features.update(freq_features)
            
            acoustic_features = AcousticFeatures(
                rms_energy=features.get('rms_energy', 0.0),
                spectral_centroid=features.get('spectral_centroid', 0.0),
                spectral_bandwidth=features.get('spectral_bandwidth', 0.0),
                spectral_rolloff=features.get('spectral_rolloff', 0.0),
                zero_crossing_rate=features.get('zero_crossing_rate', 0.0),
            )
            
            # Stage 4: Risk Assessment
            self._report(90, "Calculating risk assessment...", "analyzing")
            
            risk_assessment = self.risk_engine.calculate_risk(features, acoustic_features)
            
            # Stage 5: Recommendations
            self._report(95, "Generating recommendations...", "analyzing")
            
            recommendations = self.recommendation_engine.generate_recommendations(risk_assessment)
            
            # Stage 6: Build final result
            elapsed = time.time() - start_time
            now = datetime.now()
            
            scan_result = ScanResult(
                scan_date=now.strftime("%d/%m/%Y"),
                scan_time=now.strftime("%H:%M"),
                duration_seconds=round(elapsed, 2),
                risk_assessment=risk_assessment,
                acoustic_features=acoustic_features,
                recommendations=recommendations,
                masking_enabled=False,
            )
            
            # Stage 7: Save to database
            if save_to_db:
                try:
                    init_database()
                    scan_id = ScanRepository.save_scan(scan_result)
                    scan_result.scan_id = scan_id
                except Exception as e:
                    print(f"Warning: Failed to save scan to database: {e}")
            
            self._report(100, "Scan complete!", "complete")
            
            return scan_result
            
        except AudioCaptureError as e:
            raise ScanServiceError(f"Audio capture failed: {e}")
        except AudioProcessingError as e:
            raise ScanServiceError(f"Audio processing failed: {e}")
        except FeatureExtractionError as e:
            raise ScanServiceError(f"Feature extraction failed: {e}")
        except Exception as e:
            raise ScanServiceError(f"Scan failed: {e}")
    
    def _capture_progress_adapter(self, percent, message):
        """Scale capture progress into the overall scan progress (5-75%)."""
        scaled = 5 + int(percent * 0.70)
        self._report(scaled, message, "capturing")
    
    def _report(self, percent, message, stage=""):
        """Report progress via callback."""
        if self._progress_callback:
            try:
                self._progress_callback(percent, message)
            except Exception:
                pass


