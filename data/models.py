from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class AcousticFeatures:
    """Extracted acoustic features from audio analysis."""
    rms_energy: float = 0.0
    spectral_centroid: float = 0.0
    spectral_bandwidth: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    
    def to_dict(self):
        return {
            'rms_energy': self.rms_energy,
            'spectral_centroid': self.spectral_centroid,
            'spectral_bandwidth': self.spectral_bandwidth,
            'spectral_rolloff': self.spectral_rolloff,
            'zero_crossing_rate': self.zero_crossing_rate,
        }


@dataclass
class RiskAssessment:
    """Result of acoustic risk assessment."""
    risk_score: int  # 0-100
    risk_level: str  # "Low", "Medium", "High", "Critical"
    contributing_factors: list = field(default_factory=list)
    
    def __post_init__(self):
        if not 0 <= self.risk_score <= 100:
            raise ValueError(f"Risk score must be 0-100, got {self.risk_score}")
        valid_levels = ["Low", "Medium", "High", "Critical"]
        if self.risk_level not in valid_levels:
            raise ValueError(f"Risk level must be one of {valid_levels}")


@dataclass
class Recommendation:
    """Security recommendation."""
    recommendation_text: str
    priority: int = 0


@dataclass
class ScanResult:
    """Complete result of an acoustic environment scan."""
    scan_id: Optional[int] = None
    scan_date: str = ""
    scan_time: str = ""
    duration_seconds: float = 0.0
    risk_assessment: Optional[RiskAssessment] = None
    acoustic_features: Optional[AcousticFeatures] = None
    recommendations: list = field(default_factory=list)
    masking_enabled: bool = False
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.scan_date or not self.scan_time:
            now = datetime.now()
            self.scan_date = now.strftime("%d/%m/%Y")
            self.scan_time = now.strftime("%H:%M")
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def risk_score(self):
        return self.risk_assessment.risk_score if self.risk_assessment else 0
    
    @property
    def risk_level(self):
        return self.risk_assessment.risk_level if self.risk_assessment else "Low"
    
    def to_dict(self):
        return {
            'scan_id': self.scan_id,
            'scan_date': self.scan_date,
            'scan_time': self.scan_time,
            'duration_seconds': self.duration_seconds,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'contributing_factors': self.risk_assessment.contributing_factors if self.risk_assessment else [],
            'acoustic_features': self.acoustic_features.to_dict() if self.acoustic_features else {},
            'recommendations': [r.recommendation_text for r in self.recommendations],
            'masking_enabled': self.masking_enabled,
        }


@dataclass
class Settings:
    """Application settings/configuration."""
    microphone_device: str = "default"
    microphone_sensitivity: int = 60
    enable_alerts: bool = True
    enable_alert_sound: bool = True
    history_retention_days: int = 30
    masking_default_volume: int = 65
    
    def to_dict(self):
        return {
            'microphone_device': self.microphone_device,
            'microphone_sensitivity': self.microphone_sensitivity,
            'enable_alerts': self.enable_alerts,
            'enable_alert_sound': self.enable_alert_sound,
            'history_retention_days': self.history_retention_days,
            'masking_default_volume': self.masking_default_volume,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            microphone_device=data.get('microphone_device', 'default'),
            microphone_sensitivity=int(data.get('microphone_sensitivity', 60)),
            enable_alerts=str(data.get('enable_alerts', 'true')).lower() == 'true',
            enable_alert_sound=str(data.get('enable_alert_sound', 'true')).lower() == 'true',
            history_retention_days=int(data.get('history_retention_days', 30)),
            masking_default_volume=int(data.get('masking_default_volume', 65)),
        )


@dataclass
class ScanProgress:
    """Progress during an active scan."""
    stage: str  # "initializing", "capturing", "processing", "analyzing", "complete"
    progress_percent: int  # 0-100
    message: str = ""
