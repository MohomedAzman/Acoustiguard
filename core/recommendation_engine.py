from typing import List
from data.models import Recommendation, RiskAssessment


class RecommendationEngine:

    def generate_recommendations(
        self,
        risk_assessment: RiskAssessment
    ) -> List[Recommendation]:

        level = risk_assessment.risk_level
        
        if level == "Low":
            return self._low_risk_recommendations(risk_assessment)
        elif level == "Medium":
            return self._medium_risk_recommendations(risk_assessment)
        elif level == "High":
            return self._high_risk_recommendations(risk_assessment)
        else:  # Critical
            return self._critical_risk_recommendations(risk_assessment)
    
    def _low_risk_recommendations(self, risk: RiskAssessment) -> List[Recommendation]:
        recs = [
            Recommendation("Continue normal work practices.", priority=1),
            Recommendation("Remain aware of the surrounding acoustic environment.", priority=0),
            Recommendation("Periodic re-scanning is recommended if the environment changes.", priority=0),
        ]
        return recs
    
    def _medium_risk_recommendations(self, risk: RiskAssessment) -> List[Recommendation]:
        recs = [
            Recommendation("Reduce surrounding noise where possible.", priority=2),
            Recommendation("Consider moving to a quieter, more private environment.", priority=2),
            Recommendation("Exercise additional caution when handling sensitive information.", priority=1),
            Recommendation("Consider enabling Acoustic Masking for added protection.", priority=1),
        ]
        
        # Context-aware additions
        factors = risk.contributing_factors
        for factor in factors:
            f_lower = factor.lower()
            if "quiet" in f_lower:
                recs.insert(0, Recommendation(
                    "Low background noise detected - adding ambient sound may reduce risk.",
                    priority=2
                ))
            if "transient" in f_lower or "typing" in f_lower:
                recs.insert(0, Recommendation(
                    "Typing-like patterns detected. Use a quieter keyboard if available.",
                    priority=2
                ))
        
        return recs
    
    def _high_risk_recommendations(self, risk: RiskAssessment) -> List[Recommendation]:
        recs = [
            Recommendation("Avoid entering highly sensitive information temporarily.", priority=3),
            Recommendation("Consider moving to a more private environment.", priority=3),
            Recommendation("Enable Acoustic Masking to reduce acoustic exposure.", priority=3),
            Recommendation("Close doors and windows if possible.", priority=2),
            Recommendation("Reduce the volume of any speakers in use.", priority=1),
        ]
        
        # Context-aware additions
        factors = risk.contributing_factors
        for factor in factors:
            f_lower = factor.lower()
            if "quiet" in f_lower or "clear" in f_lower:
                recs.insert(0, Recommendation(
                    "Very clear acoustic environment makes keystrokes easily distinguishable.",
                    priority=3
                ))
            if "high-frequency" in f_lower:
                recs.insert(0, Recommendation(
                    "High-frequency content detected in the keyboard typing range.",
                    priority=3
                ))
        
        return recs
    
    def _critical_risk_recommendations(self, risk: RiskAssessment) -> List[Recommendation]:
        recs = [
            Recommendation("STOP entering sensitive information immediately.", priority=5),
            Recommendation("Move to a more private, acoustically isolated environment.", priority=5),
            Recommendation("Enable Acoustic Masking immediately.", priority=4),
            Recommendation("Close all surrounding doors and windows.", priority=3),
            Recommendation("Do not use external speakers during sensitive operations.", priority=3),
            Recommendation("Consider using a different input method for passwords.", priority=2),
        ]
        
        # Context-aware additions
        factors = risk.contributing_factors
        for factor in factors:
            f_lower = factor.lower()
            if "quiet" in f_lower:
                recs.insert(0, Recommendation(
                    "CRITICAL: Extremely quiet environment - all keystrokes are highly exposed.",
                    priority=5
                ))
            if "transient" in f_lower or "typing" in f_lower:
                recs.insert(0, Recommendation(
                    "CRITICAL: Clear typing patterns detected in the acoustic environment.",
                    priority=5
                ))
        
        return recs
    
    def get_short_summary(self, risk_assessment: RiskAssessment) -> str:
        """Get a one-line summary for notifications."""
        summaries = {
            "Low": "Environment is safe for normal work.",
            "Medium": "Moderate risk - consider additional precautions.",
            "High": "High risk - avoid entering sensitive data or enable masking.",
            "Critical": "CRITICAL - stop entering sensitive data immediately.",
        }
        return summaries.get(risk_assessment.risk_level, "Risk assessment complete.")


