import numpy as np
from typing import Dict, List, Tuple
from data.models import RiskAssessment, AcousticFeatures


# Risk thresholds (configurable)
RISK_THRESHOLDS = {
    "Low": (0, 30),
    "Medium": (30, 60),
    "High": (60, 80),
    "Critical": (80, 100),
}


class RiskEngine:

    # Feature weights (sum should be 1.0)
    # Higher weight = more important for security assessment
    FEATURE_WEIGHTS = {
        'rms_energy': 0.20,           # Overall loudness indicates environment clarity
        'spectral_centroid': 0.15,    # High frequencies indicate keyboard/typing sounds
        'spectral_bandwidth': 0.10,   # Spread indicates environmental complexity
        'spectral_rolloff': 0.10,     # High-frequency content
        'zero_crossing_rate': 0.15,   # Indicates impulsive/transient sounds (keys)
        'spectral_flatness': 0.10,    # Noise vs tonal content
        'spectral_contrast': 0.10,    # Clarity of acoustic events
        'high_freq_energy': 0.10,     # High-frequency energy (keyboard range)
    }
    
    def __init__(self):
        """Initialize the risk engine with default configuration."""
        self.thresholds = RISK_THRESHOLDS.copy()
    
    def calculate_risk(
        self,
        features: Dict[str, float],
        acoustic_features: AcousticFeatures
    ) -> RiskAssessment:

        # Calculate individual risk components
        energy_risk = self._assess_energy_risk(features)
        frequency_risk = self._assess_frequency_risk(features)
        clarity_risk = self._assess_clarity_risk(features)
        
        # Calculate weighted composite risk score
        risk_score = self._calculate_composite_score(features)
        
        # Classify risk level
        risk_level = self._classify_risk_level(risk_score)
        
        # Identify contributing factors
        contributing_factors = self._identify_risk_factors(
            features, energy_risk, frequency_risk, clarity_risk
        )
        
        return RiskAssessment(
            risk_score=int(risk_score),
            risk_level=risk_level,
            contributing_factors=contributing_factors
        )
    
    def _assess_energy_risk(self, features: Dict[str, float]) -> float:

        rms = features.get('rms_energy', 0.0)
        
        # Low energy in environment means keystrokes more audible
        # Paradoxically, quiet environments are riskier
        if rms < 0.05:  # Very quiet
            return 80.0
        elif rms < 0.15:  # Quiet
            return 60.0
        elif rms < 0.30:  # Moderate background noise (some protection)
            return 40.0
        else:  # Noisy (masks keystrokes)
            return 20.0
    
    def _assess_frequency_risk(self, features: Dict[str, float]) -> float:

        # Spectral centroid indicates frequency distribution
        centroid = features.get('spectral_centroid', 0.0)
        
        # High spectral centroid = more high-frequency content
        # This is typical of keyboard/typing sounds
        if centroid > 4000:  # High-frequency dominant (keyboard range)
            risk = 75.0
        elif centroid > 2500:
            risk = 55.0
        elif centroid > 1500:
            risk = 35.0
        else:
            risk = 20.0
        
        # High-frequency energy ratio
        high_freq_energy = features.get('high_freq_energy', 0.0)
        if high_freq_energy > 0.4:  # >40% in high frequencies
            risk += 15.0
        elif high_freq_energy > 0.25:
            risk += 10.0
        
        return min(risk, 100.0)
    
    def _assess_clarity_risk(self, features: Dict[str, float]) -> float:

        # Zero crossing rate indicates transient/impulsive content
        zcr = features.get('zero_crossing_rate', 0.0)
        
        # High ZCR indicates many transients (like keystrokes)
        if zcr > 0.25:
            clarity_risk = 70.0
        elif zcr > 0.15:
            clarity_risk = 50.0
        elif zcr > 0.08:
            clarity_risk = 30.0
        else:
            clarity_risk = 15.0
        
        # Spectral flatness (low = tonal/clear, high = noisy/masked)
        flatness = features.get('spectral_flatness', 0.5)
        if flatness < 0.2:  # Tonal/clear environment
            clarity_risk += 20.0
        elif flatness < 0.4:
            clarity_risk += 10.0
        
        # Spectral contrast (high = clear acoustic events)
        contrast = features.get('spectral_contrast', 0.0)
        if contrast > 20.0:
            clarity_risk += 10.0
        
        return min(clarity_risk, 100.0)
    
    def _calculate_composite_score(self, features: Dict[str, float]) -> float:

        # Individual component scores
        energy_risk = self._assess_energy_risk(features)
        frequency_risk = self._assess_frequency_risk(features)
        clarity_risk = self._assess_clarity_risk(features)
        
        # Weighted combination
        composite = (
            energy_risk * 0.35 +
            frequency_risk * 0.40 +
            clarity_risk * 0.25
        )
        
        # Apply modifiers based on additional features
        
        # RMS variability (high variability = typing activity)
        rms_std = features.get('rms_std', 0.0)
        if rms_std > 0.1:
            composite += 5.0
        
        # Spectral rolloff (high = more high-frequency content)
        rolloff = features.get('spectral_rolloff', 0.0)
        if rolloff > 8000:
            composite += 5.0
        
        # Clamp to 0-100 range
        return max(0.0, min(100.0, composite))
    
    def _classify_risk_level(self, risk_score: float) -> str:

        for level, (min_score, max_score) in self.thresholds.items():
            if min_score <= risk_score < max_score:
                return level
        
        # Default to Critical if above all thresholds
        return "Critical"
    
    def _identify_risk_factors(
        self,
        features: Dict[str, float],
        energy_risk: float,
        frequency_risk: float,
        clarity_risk: float
    ) -> List[str]:

        factors = []
        
        # Energy-related factors
        rms = features.get('rms_energy', 0.0)
        if rms < 0.10 and energy_risk > 50:
            factors.append("Very quiet environment - keystrokes highly audible")
        elif rms < 0.20 and energy_risk > 40:
            factors.append("Quiet environment - limited acoustic masking")
        
        # Frequency-related factors
        centroid = features.get('spectral_centroid', 0.0)
        if centroid > 3500 and frequency_risk > 60:
            factors.append("High-frequency dominance detected (typical of keyboard sounds)")
        
        high_freq = features.get('high_freq_energy', 0.0)
        if high_freq > 0.35:
            factors.append("Significant high-frequency energy present")
        
        # Clarity-related factors
        zcr = features.get('zero_crossing_rate', 0.0)
        if zcr > 0.20 and clarity_risk > 50:
            factors.append("High transient activity detected (typing-like patterns)")
        
        flatness = features.get('spectral_flatness', 0.5)
        if flatness < 0.25:
            factors.append("Clear acoustic environment - low background noise")
        
        # Bandwidth factors
        bandwidth = features.get('spectral_bandwidth', 0.0)
        if bandwidth > 5000:
            factors.append("Wide spectral bandwidth - diverse frequency content")
        
        # If no specific factors, add general assessment
        if not factors:
            if energy_risk > 50 or frequency_risk > 50 or clarity_risk > 50:
                factors.append("Elevated acoustic exposure detected")
            else:
                factors.append("Environmental acoustic conditions assessed")
        
        return factors
    
    def get_risk_explanation(self, risk_assessment: RiskAssessment) -> str:

        level = risk_assessment.risk_level
        score = risk_assessment.risk_score
        
        explanations = {
            "Low": f"Low acoustic security risk detected (score: {score}/100). "
                   f"Your current environment provides reasonable acoustic protection.",
            
            "Medium": f"Medium acoustic security risk detected (score: {score}/100). "
                      f"Consider taking additional precautions when entering sensitive information.",
            
            "High": f"High acoustic security risk detected (score: {score}/100). "
                    f"Your environment may allow acoustic side-channel exposure. "
                    f"Enable acoustic masking or move to a more private location.",
            
            "Critical": f"Critical acoustic security risk detected (score: {score}/100). "
                       f"STOP entering sensitive information immediately. "
                       f"Your current environment poses significant acoustic exposure risk."
        }
        
        return explanations.get(level, f"Risk assessment: {level} (score: {score}/100)")


