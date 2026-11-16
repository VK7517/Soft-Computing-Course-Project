from fuzzy_system import FuzzyAcademicRiskSystem
from data_processor import DataProcessor
from explainability import ExplainabilityEngine
from config import Config
import os

class RiskEngine:
    """
    Unified Prediction Engine for Student Academic Risk Assessment.
    Uses GA-Optimized Fuzzy Logic System.
    """
    def __init__(self, use_optimized=True):
        self.fuzzy_system = FuzzyAcademicRiskSystem()
        self.use_optimized = use_optimized
        
        if use_optimized and os.path.exists(Config.OPTIMIZED_PARAMS_FILE):
            self.fuzzy_system.load_parameters(Config.OPTIMIZED_PARAMS_FILE)
            self.model_status = "GA-Optimized Fuzzy Model"
        else:
            self.model_status = "Baseline Fuzzy Model"

        self.explainer = ExplainabilityEngine(self.fuzzy_system)

    def predict_risk(self, raw_or_norm_inputs, is_normalized=False):
        """
        Accepts dictionary of student inputs.
        If is_normalized is False, converts raw inputs to normalized [0, 1] scale first.
        Returns full risk assessment payload.
        """
        if not is_normalized:
            raw_inputs = raw_or_norm_inputs
            norm_inputs = DataProcessor.normalize_input(raw_inputs)
        else:
            norm_inputs = raw_or_norm_inputs
            raw_inputs = DataProcessor.denormalize_input(norm_inputs)

        # Ensure all required 6 inputs are present with defaults if missing
        for feat in Config.INPUT_FEATURES:
            if feat not in norm_inputs:
                norm_inputs[feat] = 0.5
            if feat not in raw_inputs:
                raw_inputs[feat] = Config.FEATURE_RANGES[feat]['min'] + 0.5 * (Config.FEATURE_RANGES[feat]['max'] - Config.FEATURE_RANGES[feat]['min'])

        # Compute fuzzy inference risk score and activated rules
        risk_score, activated_rules = self.fuzzy_system.evaluate_single(norm_inputs)

        # Categorize risk score
        risk_cat_key, cat_info = self._categorize_risk(risk_score)

        # Calculate factor contributions and explainability
        factor_analysis = self.explainer.analyze_factor_contributions(norm_inputs, raw_inputs, risk_score)

        return {
            'risk_score': round(risk_score, 1),
            'risk_category': cat_info['label'],
            'risk_level_code': risk_cat_key,
            'risk_color': cat_info['color'],
            'raw_inputs': raw_inputs,
            'norm_inputs': norm_inputs,
            'activated_rules': activated_rules,
            'factor_contributions': factor_analysis['contributions'],
            'top_risk_factor': factor_analysis['top_risk_factor'],
            'linguistic_states': factor_analysis['linguistic_states'],
            'explanation': factor_analysis['explanation'],
            'model_used': self.model_status
        }

    def _categorize_risk(self, risk_score):
        """Map 0-100 risk score to configured categories."""
        if risk_score <= 20:
            return 'VERY_LOW', Config.RISK_CATEGORIES['VERY_LOW']
        elif risk_score <= 40:
            return 'LOW', Config.RISK_CATEGORIES['LOW']
        elif risk_score <= 60:
            return 'MODERATE', Config.RISK_CATEGORIES['MODERATE']
        elif risk_score <= 80:
            return 'HIGH', Config.RISK_CATEGORIES['HIGH']
        else:
            return 'VERY_HIGH', Config.RISK_CATEGORIES['VERY_HIGH']
