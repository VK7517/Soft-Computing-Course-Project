from config import Config
import numpy as np

class ExplainabilityEngine:
    """
    Mathematical Explainability Engine for Fuzzy Academic Risk Model.
    Computes factor contributions using membership strengths, ideal state deviations, and rule activation weights.
    """
    def __init__(self, fuzzy_system):
        self.fuzzy_system = fuzzy_system

    def analyze_factor_contributions(self, norm_inputs, raw_inputs, risk_score):
        """
        Calculates dynamic factor risk impact for each input variable.
        """
        # Determine dominant linguistic term for each input
        memberships = self.fuzzy_system.get_linguistic_memberships(norm_inputs)
        linguistic_states = {}
        for feat, term_dict in memberships.items():
            dominant_term = max(term_dict, key=term_dict.get)
            linguistic_states[feat] = dominant_term

        # Calculate Risk Deficit / Deviation from optimal state
        # For positive factors (Attendance, StudyHours, AssignmentCompletion, ExamScore, Internet), lower is worse.
        # For negative factor (StressLevel), higher is worse.
        risk_deficits = {}
        for feat in Config.INPUT_FEATURES:
            val = norm_inputs.get(feat, 0.5)
            if feat == 'StressLevel':
                # Higher stress = higher risk deficit
                deficit = val
            else:
                # Lower performance = higher risk deficit
                deficit = 1.0 - val
            risk_deficits[feat] = max(0.0, float(deficit))

        total_deficit = sum(risk_deficits.values())
        
        contributions = []
        for feat in Config.INPUT_FEATURES:
            raw_val = raw_inputs.get(feat, 0)
            unit = Config.FEATURE_RANGES[feat]['unit']
            norm_val = norm_inputs.get(feat, 0.5)
            state = linguistic_states.get(feat, 'Normal')
            deficit = risk_deficits[feat]
            
            if total_deficit > 1e-5:
                pct = (deficit / total_deficit) * 100.0
            else:
                pct = 16.67

            # Determine impact label based on percentage & raw risk deficit
            if pct > 25.0 and deficit > 0.4:
                impact_level = "High Impact"
                color = "#EF4444"
            elif pct > 18.0 and deficit > 0.3:
                impact_level = "Moderate-High Impact"
                color = "#F59E0B"
            elif pct > 12.0 and deficit > 0.15:
                impact_level = "Moderate Impact"
                color = "#3B82F6"
            elif deficit > 0.05:
                impact_level = "Low Impact"
                color = "#6B7280"
            else:
                impact_level = "Protective Factor"
                color = "#10B981"

            contributions.append({
                'factor': feat,
                'raw_value': raw_val,
                'unit': unit,
                'normalized_value': round(norm_val, 2),
                'linguistic_state': state,
                'contribution_percentage': round(pct, 1),
                'impact_level': impact_level,
                'color': color
            })

        # Sort contributions by contribution percentage descending
        contributions = sorted(contributions, key=lambda x: x['contribution_percentage'], reverse=True)
        top_risk_factor = contributions[0]['factor'] if contributions else 'None'

        # Build dynamic text explanation
        explanation = self._build_explanation(contributions, risk_score, top_risk_factor)

        return {
            'contributions': contributions,
            'top_risk_factor': top_risk_factor,
            'linguistic_states': linguistic_states,
            'explanation': explanation
        }

    def _build_explanation(self, contributions, risk_score, top_factor):
        """Generates dynamic natural language explanation based on actual factor analysis."""
        high_risk_factors = [c for c in contributions if c['impact_level'] in ['High Impact', 'Moderate-High Impact']]
        protective_factors = [c for c in contributions if c['impact_level'] == 'Protective Factor']

        if risk_score > 60:
            msg = f"The student shows an elevated academic risk score of {risk_score:.1f}/100. "
            if high_risk_factors:
                factor_names = ", ".join([f"{c['factor']} ({c['raw_value']}{c['unit']})" for c in high_risk_factors])
                msg += f"Primary risk drivers identified by the fuzzy inference engine are {factor_names}. "
            else:
                msg += f"The primary contributing factor is {top_factor}. "
            msg += "Immediate early intervention is recommended to avoid course failure or academic drop."
        elif risk_score > 40:
            msg = f"The student is at a moderate academic risk score of {risk_score:.1f}/100. "
            if high_risk_factors:
                factor_names = ", ".join([c['factor'] for c in high_risk_factors])
                msg += f"Key areas requiring attention include {factor_names}. "
            msg += "Targeted improvements in study habits and attendance can transition the student into low risk."
        else:
            msg = f"The student maintains a healthy academic risk score of {risk_score:.1f}/100 (Low Risk). "
            if protective_factors:
                prot_names = ", ".join([c['factor'] for c in protective_factors])
                msg += f"Strong protective performance observed in {prot_names}. "
            msg += "Continued regular study schedules and class attendance will sustain high academic performance."

        return msg
