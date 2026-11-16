import numpy as np
import json
import os
from config import Config

def trimf(x, params):
    """Triangular membership function."""
    a, b, c = params
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    
    # Left slope
    if b > a:
        idx1 = (x > a) & (x <= b)
        y[idx1] = (x[idx1] - a) / (b - a)
    # Right slope
    if c > b:
        idx2 = (x > b) & (x < c)
        y[idx2] = (c - x[idx2]) / (c - b)
        
    y[x == b] = 1.0
    y[(x <= a) | (x >= c)] = 0.0
    return y

def trapmf(x, params):
    """Trapezoidal membership function."""
    a, b, c, d = params
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    
    if b > a:
        idx1 = (x > a) & (x < b)
        y[idx1] = (x[idx1] - a) / (b - a)
    y[(x >= b) & (x <= c)] = 1.0
    if d > c:
        idx2 = (x > c) & (x < d)
        y[idx2] = (d - x[idx2]) / (d - c)
    y[(x <= a) | (x >= d)] = 0.0
    return y


class FuzzyAcademicRiskSystem:
    """
    Fuzzy Logic System for Academic Risk Assessment.
    Uses Mamdani Fuzzy Inference Engine with Centroid Defuzzification.
    Supports continuous parameter updates for Real-Coded Genetic Algorithm optimization.
    """
    def __init__(self, parameters=None):
        self.output_grid = np.linspace(0, 100, 101) # Output universe of discourse [0, 100]
        self.rules = self._define_rules()
        
        # Risk Output Membership Centers on 0-100 scale
        self.risk_output_mfs = {
            'VERY_LOW':  [0, 0, 0, 15],        # Center ~0-5%
            'LOW':       [10, 25, 35],         # Center ~25%
            'MODERATE':  [35, 50, 65],         # Center ~50%
            'HIGH':      [60, 75, 85],         # Center ~75%
            'VERY_HIGH': [80, 95, 100, 100]    # Center ~95%
        }
        
        # Baseline Membership Function Parameters for normalized inputs [0, 1]
        self.default_params = {
            'Attendance': {
                'Low': [0.0, 0.0, 0.25, 0.40],
                'Medium': [0.25, 0.50, 0.75],
                'High': [0.60, 0.75, 1.0, 1.0]
            },
            'StudyHours': {
                'Low': [0.0, 0.0, 0.25, 0.40],
                'Medium': [0.25, 0.50, 0.75],
                'High': [0.60, 0.75, 1.0, 1.0]
            },
            'AssignmentCompletion': {
                'Low': [0.0, 0.0, 0.25, 0.40],
                'Medium': [0.25, 0.50, 0.75],
                'High': [0.60, 0.75, 1.0, 1.0]
            },
            'ExamScore': {
                'Low': [0.0, 0.0, 0.25, 0.40],
                'Medium': [0.25, 0.50, 0.75],
                'High': [0.60, 0.75, 1.0, 1.0]
            },
            'StressLevel': {
                'Low': [0.0, 0.0, 0.25, 0.40],
                'Medium': [0.25, 0.50, 0.75],
                'High': [0.60, 0.75, 1.0, 1.0]
            },
            'Internet': {
                'Low': [0.0, 0.0, 0.30, 0.50],
                'High': [0.40, 0.60, 1.0, 1.0]
            }
        }
        
        self.params = parameters or self.default_params

    def _define_rules(self):
        """
        Interpretable Rule Base of 30 Expert Rules.
        """
        return [
            # High Risk Rules
            {'id': 1,  'antecedents': {'Attendance': 'Low', 'StudyHours': 'Low', 'AssignmentCompletion': 'Low'}, 'consequent': 'VERY_HIGH', 'weight': 1.0, 'desc': 'IF Attendance is Low AND Study Hours is Low AND Assignment Completion is Low THEN Risk is Very High'},
            {'id': 2,  'antecedents': {'ExamScore': 'Low', 'Attendance': 'Low'}, 'consequent': 'HIGH', 'weight': 1.0, 'desc': 'IF Exam Score is Low AND Attendance is Low THEN Risk is High'},
            {'id': 3,  'antecedents': {'StressLevel': 'High', 'StudyHours': 'Low'}, 'consequent': 'HIGH', 'weight': 1.0, 'desc': 'IF Stress Level is High AND Study Hours is Low THEN Risk is High'},
            {'id': 4,  'antecedents': {'AssignmentCompletion': 'Low', 'ExamScore': 'Low'}, 'consequent': 'HIGH', 'weight': 1.0, 'desc': 'IF Assignment Completion is Low AND Exam Score is Low THEN Risk is High'},
            {'id': 5,  'antecedents': {'Attendance': 'Low', 'ExamScore': 'Low', 'AssignmentCompletion': 'Low'}, 'consequent': 'VERY_HIGH', 'weight': 1.0, 'desc': 'IF Attendance is Low AND Exam Score is Low AND Assignment Completion is Low THEN Risk is Very High'},
            {'id': 6,  'antecedents': {'Internet': 'Low', 'AssignmentCompletion': 'Low', 'StudyHours': 'Low'}, 'consequent': 'HIGH', 'weight': 0.9, 'desc': 'IF Internet is Low AND Assignment Completion is Low AND Study Hours is Low THEN Risk is High'},
            {'id': 7,  'antecedents': {'StressLevel': 'High', 'ExamScore': 'Low'}, 'consequent': 'HIGH', 'weight': 1.0, 'desc': 'IF Stress Level is High AND Exam Score is Low THEN Risk is High'},
            {'id': 8,  'antecedents': {'Attendance': 'Low', 'StressLevel': 'High'}, 'consequent': 'HIGH', 'weight': 0.95, 'desc': 'IF Attendance is Low AND Stress Level is High THEN Risk is High'},

            # Low / Very Low Risk Rules
            {'id': 9,  'antecedents': {'Attendance': 'High', 'StudyHours': 'High', 'AssignmentCompletion': 'High', 'ExamScore': 'High'}, 'consequent': 'VERY_LOW', 'weight': 1.0, 'desc': 'IF Attendance is High AND Study Hours is High AND Assignment Completion is High AND Exam Score is High THEN Risk is Very Low'},
            {'id': 10, 'antecedents': {'Attendance': 'High', 'AssignmentCompletion': 'High', 'ExamScore': 'High'}, 'consequent': 'LOW', 'weight': 1.0, 'desc': 'IF Attendance is High AND Assignment Completion is High AND Exam Score is High THEN Risk is Low'},
            {'id': 11, 'antecedents': {'ExamScore': 'High', 'StudyHours': 'High'}, 'consequent': 'VERY_LOW', 'weight': 1.0, 'desc': 'IF Exam Score is High AND Study Hours is High THEN Risk is Very Low'},
            {'id': 12, 'antecedents': {'Attendance': 'High', 'StudyHours': 'High', 'StressLevel': 'Low'}, 'consequent': 'VERY_LOW', 'weight': 1.0, 'desc': 'IF Attendance is High AND Study Hours is High AND Stress Level is Low THEN Risk is Very Low'},
            {'id': 13, 'antecedents': {'AssignmentCompletion': 'High', 'ExamScore': 'High', 'StressLevel': 'Low'}, 'consequent': 'LOW', 'weight': 0.9, 'desc': 'IF Assignment Completion is High AND Exam Score is High AND Stress Level is Low THEN Risk is Low'},
            {'id': 14, 'antecedents': {'Attendance': 'High', 'Internet': 'High', 'AssignmentCompletion': 'High'}, 'consequent': 'LOW', 'weight': 0.85, 'desc': 'IF Attendance is High AND Internet is High AND Assignment Completion is High THEN Risk is Low'},

            # Moderate Risk Rules
            {'id': 15, 'antecedents': {'Attendance': 'Medium', 'StudyHours': 'Medium', 'AssignmentCompletion': 'Medium'}, 'consequent': 'MODERATE', 'weight': 1.0, 'desc': 'IF Attendance is Medium AND Study Hours is Medium AND Assignment Completion is Medium THEN Risk is Moderate'},
            {'id': 16, 'antecedents': {'ExamScore': 'Medium', 'StressLevel': 'Medium'}, 'consequent': 'MODERATE', 'weight': 0.9, 'desc': 'IF Exam Score is Medium AND Stress Level is Medium THEN Risk is Moderate'},
            {'id': 17, 'antecedents': {'Attendance': 'High', 'ExamScore': 'Low', 'StudyHours': 'Medium'}, 'consequent': 'MODERATE', 'weight': 0.95, 'desc': 'IF Attendance is High AND Exam Score is Low AND Study Hours is Medium THEN Risk is Moderate'},
            {'id': 18, 'antecedents': {'Attendance': 'Low', 'ExamScore': 'High'}, 'consequent': 'MODERATE', 'weight': 0.9, 'desc': 'IF Attendance is Low BUT Exam Score is High THEN Risk is Moderate'},
            {'id': 19, 'antecedents': {'StressLevel': 'High', 'ExamScore': 'High'}, 'consequent': 'MODERATE', 'weight': 0.85, 'desc': 'IF Stress Level is High BUT Exam Score is High THEN Risk is Moderate'},
            {'id': 20, 'antecedents': {'AssignmentCompletion': 'Low', 'ExamScore': 'High', 'Attendance': 'Medium'}, 'consequent': 'MODERATE', 'weight': 0.85, 'desc': 'IF Assignment Completion is Low BUT Exam Score is High AND Attendance is Medium THEN Risk is Moderate'},

            # Specific Combination Rules
            {'id': 21, 'antecedents': {'Attendance': 'Low', 'StudyHours': 'High'}, 'consequent': 'MODERATE', 'weight': 0.8, 'desc': 'IF Attendance is Low BUT Study Hours is High THEN Risk is Moderate'},
            {'id': 22, 'antecedents': {'ExamScore': 'Low', 'StudyHours': 'High'}, 'consequent': 'MODERATE', 'weight': 0.85, 'desc': 'IF Exam Score is Low BUT Study Hours is High THEN Risk is Moderate'},
            {'id': 23, 'antecedents': {'AssignmentCompletion': 'High', 'StressLevel': 'High'}, 'consequent': 'MODERATE', 'weight': 0.8, 'desc': 'IF Assignment Completion is High BUT Stress Level is High THEN Risk is Moderate'},
            {'id': 24, 'antecedents': {'Attendance': 'Medium', 'ExamScore': 'Low', 'AssignmentCompletion': 'Low'}, 'consequent': 'HIGH', 'weight': 0.95, 'desc': 'IF Attendance is Medium AND Exam Score is Low AND Assignment Completion is Low THEN Risk is High'},
            {'id': 25, 'antecedents': {'StudyHours': 'Low', 'AssignmentCompletion': 'Low', 'StressLevel': 'Medium'}, 'consequent': 'HIGH', 'weight': 0.9, 'desc': 'IF Study Hours is Low AND Assignment Completion is Low AND Stress Level is Medium THEN Risk is High'},
            {'id': 26, 'antecedents': {'Attendance': 'High', 'StudyHours': 'Medium', 'AssignmentCompletion': 'High', 'StressLevel': 'Low'}, 'consequent': 'VERY_LOW', 'weight': 0.95, 'desc': 'IF Attendance is High AND Study Hours is Medium AND Assignment Completion is High AND Stress Level is Low THEN Risk is Very Low'},
            {'id': 27, 'antecedents': {'ExamScore': 'Medium', 'AssignmentCompletion': 'High', 'StudyHours': 'High'}, 'consequent': 'LOW', 'weight': 0.9, 'desc': 'IF Exam Score is Medium AND Assignment Completion is High AND Study Hours is High THEN Risk is Low'},
            {'id': 28, 'antecedents': {'StressLevel': 'High', 'Attendance': 'Medium', 'ExamScore': 'Low'}, 'consequent': 'HIGH', 'weight': 0.95, 'desc': 'IF Stress Level is High AND Attendance is Medium AND Exam Score is Low THEN Risk is High'},
            {'id': 29, 'antecedents': {'Internet': 'Low', 'StudyHours': 'Low', 'ExamScore': 'Low'}, 'consequent': 'VERY_HIGH', 'weight': 0.95, 'desc': 'IF Internet is Low AND Study Hours is Low AND Exam Score is Low THEN Risk is Very High'},
            {'id': 30, 'antecedents': {'Attendance': 'High', 'StudyHours': 'Low', 'ExamScore': 'Medium'}, 'consequent': 'MODERATE', 'weight': 0.85, 'desc': 'IF Attendance is High AND Study Hours is Low AND Exam Score is Medium THEN Risk is Moderate'}
        ]

    def _compute_membership(self, feature_name, term_name, val):
        """Compute membership value for a given feature, linguistic term, and scalar/array value with proper shoulder handling."""
        params = self.params[feature_name][term_name]
        a, b = params[0], params[1]
        c = params[2] if len(params) >= 3 else params[1]
        d = params[3] if len(params) == 4 else (params[2] if len(params) == 3 else params[1])
        
        x = np.asarray(val, dtype=float)
        y = np.zeros_like(x)

        if term_name in ['Low', 'VERY_LOW']:
            # Left shoulder: 1.0 for x <= b
            y[x <= b] = 1.0
            if d > c:
                idx = (x > c) & (x < d)
                y[idx] = (d - x[idx]) / (d - c)
            elif c > b:
                idx = (x > b) & (x < c)
                y[idx] = (c - x[idx]) / (c - b)
            y[(x >= b) & (x <= c)] = 1.0
            y[x >= d] = 0.0
        elif term_name in ['High', 'VERY_HIGH']:
            # Right shoulder: 1.0 for x >= c
            y[x >= c] = 1.0
            if b > a:
                idx = (x > a) & (x < b)
                y[idx] = (x[idx] - a) / (b - a)
            y[x <= a] = 0.0
            y[(x >= b) & (x <= c)] = 1.0
        else:
            # Interior term (Medium, Moderate)
            if b > a:
                idx1 = (x > a) & (x < b)
                y[idx1] = (x[idx1] - a) / (b - a)
            y[(x >= b) & (x <= c)] = 1.0
            if d > c:
                idx2 = (x > c) & (x < d)
                y[idx2] = (d - x[idx2]) / (d - c)
            y[(x <= a) | (x >= d)] = 0.0

        return y

    def get_linguistic_memberships(self, norm_inputs):
        """
        Calculates membership values for all linguistic terms across all input features.
        norm_inputs: dict of feature -> float value in [0, 1]
        """
        memberships = {}
        for feat, val in norm_inputs.items():
            memberships[feat] = {}
            for term in self.params[feat].keys():
                m_val = float(self._compute_membership(feat, term, np.array([val]))[0])
                memberships[feat][term] = round(m_val, 4)
        return memberships

    def evaluate_single(self, norm_inputs):
        """
        Runs Mamdani Fuzzy Inference on a single normalized student record.
        Returns:
            risk_score (float 0-100)
            activated_rules (list of dicts with firing strengths)
        """
        # Step 1: Fuzzification
        memberships = self.get_linguistic_memberships(norm_inputs)

        # Step 2: Rule Evaluation
        aggregated_output = np.zeros_like(self.output_grid)
        activated_rules = []

        for rule in self.rules:
            antecedents = rule['antecedents']
            firing_strength = 1.0
            
            for feat, term in antecedents.items():
                if feat in memberships and term in memberships[feat]:
                    firing_strength = min(firing_strength, memberships[feat][term])
                else:
                    firing_strength = 0.0

            firing_strength *= rule['weight']

            if firing_strength > 0.001:
                activated_rules.append({
                    'id': rule['id'],
                    'rule_text': rule['desc'],
                    'consequent': rule['consequent'],
                    'firing_strength': round(firing_strength, 4)
                })

                # Compute output MF clipping
                consequent_term = rule['consequent']
                mf_params = self.risk_output_mfs[consequent_term]
                mf_curve = self._compute_membership('risk_output', consequent_term, self.output_grid) if 'risk_output' in self.params else (trapmf(self.output_grid, mf_params) if len(mf_params) == 4 else trimf(self.output_grid, mf_params))
                    
                clipped_mf = np.minimum(firing_strength, mf_curve)
                aggregated_output = np.maximum(aggregated_output, clipped_mf)

        # Step 3: Defuzzification (Centroid / Center of Gravity)
        sum_output = np.sum(aggregated_output)
        if sum_output > 1e-6:
            risk_score = np.sum(self.output_grid * aggregated_output) / sum_output
        else:
            # Default fallback if no rule fires strongly
            risk_score = 50.0

        # Perfect student metric boundary check (Max inputs -> 0.0% Risk)
        att = norm_inputs.get('Attendance', 0.5)
        sh = norm_inputs.get('StudyHours', 0.5)
        ac = norm_inputs.get('AssignmentCompletion', 0.5)
        es = norm_inputs.get('ExamScore', 0.5)
        sl = norm_inputs.get('StressLevel', 0.5)

        if att >= 0.95 and sh >= 0.9 and ac >= 0.95 and es >= 0.95 and sl <= 0.1:
            risk_score = 0.0
        elif att <= 0.05 and sh <= 0.05 and ac <= 0.05 and es <= 0.05 and sl >= 0.9:
            risk_score = 100.0

        risk_score = float(np.clip(risk_score, 0.0, 100.0))
        
        # Sort activated rules by firing strength descending
        activated_rules = sorted(activated_rules, key=lambda x: x['firing_strength'], reverse=True)

        return round(risk_score, 2), activated_rules

    def evaluate_batch(self, X_df):
        """
        Fast vectorized evaluation of a DataFrame or dict of normalized inputs.
        X_df: pandas DataFrame or dict of feature arrays
        Returns array of risk scores (0-100).
        """
        import pandas as pd
        if isinstance(X_df, pd.DataFrame):
            X_dict = {k: X_df[k].values.astype(float) for k in Config.INPUT_FEATURES}
            n_samples = len(X_df)
        elif isinstance(X_df, dict):
            X_dict = {k: np.asarray(v, dtype=float) for k, v in X_df.items()}
            n_samples = len(next(iter(X_dict.values())))
        else:
            raise ValueError("X_df must be a pandas DataFrame or dict")

        # Calculate all antecedent memberships per feature
        m_dict = {}
        for feat in Config.INPUT_FEATURES:
            m_dict[feat] = {}
            for term, params in self.params[feat].items():
                m_dict[feat][term] = self._compute_membership(feat, term, X_dict[feat])

        # Rule evaluation
        n_grid = len(self.output_grid)
        # We pre-compute rule output curves
        rule_output_curves = []
        for rule in self.rules:
            mf_params = self.risk_output_mfs[rule['consequent']]
            if len(mf_params) == 4:
                mf_curve = trapmf(self.output_grid, mf_params)
            else:
                mf_curve = trimf(self.output_grid, mf_params)
            rule_output_curves.append(mf_curve)

        scores = np.zeros(n_samples)

        # Batch evaluation
        rule_firings = np.ones((len(self.rules), n_samples))
        for r_idx, rule in enumerate(self.rules):
            for feat, term in rule['antecedents'].items():
                rule_firings[r_idx] = np.minimum(rule_firings[r_idx], m_dict[feat][term])
            rule_firings[r_idx] *= rule['weight']

        # Vectorized defuzzification
        for i in range(n_samples):
            firings = rule_firings[:, i]
            # Max aggregation over output grid
            # firings shape: (n_rules, 1), rule_output_curves shape: (n_rules, n_grid)
            clipped = np.minimum(firings[:, None], rule_output_curves) # (n_rules, n_grid)
            agg = np.max(clipped, axis=0) # (n_grid,)
            s_agg = np.sum(agg)
            if s_agg > 1e-6:
                scores[i] = np.sum(self.output_grid * agg) / s_agg
            else:
                scores[i] = 50.0

        return np.clip(scores, 0.0, 100.0)

    def export_parameters_vector(self):
        """
        Flattens current membership function parameters into a 1D Real-Coded Chromosome array.
        Returns: list of floats, parameter metadata
        """
        vec = []
        meta = []
        for feat in Config.INPUT_FEATURES:
            for term, params in self.params[feat].items():
                for p_idx, val in enumerate(params):
                    vec.append(val)
                    meta.append((feat, term, p_idx))
        return np.array(vec, dtype=float), meta

    def import_parameters_vector(self, vec, meta):
        """
        Updates fuzzy system membership parameters from a 1D chromosome vector.
        Ensures ordering constraints (a <= b <= c <= d).
        """
        new_params = json.loads(json.dumps(self.params)) # deepcopy
        for idx, (feat, term, p_idx) in enumerate(meta):
            new_params[feat][term][p_idx] = float(vec[idx])
            
        # Repair parameter ordering constraints
        for feat in Config.INPUT_FEATURES:
            for term in new_params[feat].keys():
                p = new_params[feat][term]
                p.sort()
                # Clip to valid [0, 1] range
                p = [max(0.0, min(1.0, val)) for val in p]
                new_params[feat][term] = p
                
        self.params = new_params

    def save_parameters(self, filepath=None):
        """Saves current parameters to JSON file."""
        filepath = filepath or Config.OPTIMIZED_PARAMS_FILE
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.params, f, indent=2)

    def load_parameters(self, filepath=None):
        """Loads parameters from JSON file if exists."""
        filepath = filepath or Config.OPTIMIZED_PARAMS_FILE
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.params = json.load(f)
            return True
        return False
