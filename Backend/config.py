import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'academic_risk_fuzzy_ga_secret_key_2026')
    DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'Dataset', 'full_dataset_normalized.csv')
    USERS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')
    OPTIMIZED_PARAMS_FILE = os.path.join(os.path.dirname(__file__), 'models', 'optimized_parameters.json')
    
    # Risk Score Categories (0 - 100)
    RISK_CATEGORIES = {
        'VERY_LOW': {'min': 0, 'max': 20, 'label': 'Very Low Risk', 'color': '#10B981'},
        'LOW': {'min': 21, 'max': 40, 'label': 'Low Risk', 'color': '#3B82F6'},
        'MODERATE': {'min': 41, 'max': 60, 'label': 'Moderate Risk', 'color': '#F59E0B'},
        'HIGH': {'min': 61, 'max': 80, 'label': 'High Risk', 'color': '#EF4444'},
        'VERY_HIGH': {'min': 81, 'max': 100, 'label': 'Very High Risk', 'color': '#991B1B'}
    }

    # Predictive Input Feature Names
    INPUT_FEATURES = [
        'Attendance',
        'StudyHours',
        'AssignmentCompletion',
        'ExamScore',
        'StressLevel',
        'Internet'
    ]

    # Target Feature
    TARGET_FEATURE = 'FinalGrade'

    # Normalization Ranges (Original Feature Ranges based on inspection)
    FEATURE_RANGES = {
        'Attendance': {'min': 60.0, 'max': 100.0, 'unit': '%'},
        'StudyHours': {'min': 5.0, 'max': 44.0, 'unit': 'hrs/wk'},
        'AssignmentCompletion': {'min': 50.0, 'max': 100.0, 'unit': '%'},
        'ExamScore': {'min': 40.0, 'max': 100.0, 'unit': 'marks'},
        'StressLevel': {'min': 0.0, 'max': 2.0, 'unit': 'scale (0-2)'},  # 0: Low, 1: Med, 2: High
        'Internet': {'min': 0.0, 'max': 1.0, 'unit': 'binary (0/1)'}    # 0: Unavailable, 1: Available
    }
