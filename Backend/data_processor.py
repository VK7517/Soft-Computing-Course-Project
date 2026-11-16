import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from config import Config

class DataProcessor:
    def __init__(self, dataset_path=None):
        self.dataset_path = dataset_path or Config.DATASET_PATH
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_train_cat = None
        self.y_test_cat = None
        
    def load_dataset(self):
        """Load and validate the dataset from CSV."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset file not found at {self.dataset_path}")
            
        self.df = pd.read_csv(self.dataset_path)
        return self.df

    def inspect_dataset(self):
        """Return dataset statistics, missing values, duplicates, and range checks."""
        if self.df is None:
            self.load_dataset()
            
        inspection_results = {
            'num_rows': int(self.df.shape[0]),
            'num_cols': int(self.df.shape[1]),
            'columns': list(self.df.columns),
            'missing_values': self.df.isnull().sum().to_dict(),
            'duplicate_records': int(self.df.duplicated().sum()),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'target_distribution': self.df['FinalGrade'].value_counts().to_dict(),
            'feature_ranges': {}
        }

        # Inspect range for key columns
        key_cols = ['Attendance', 'StudyHours', 'AssignmentCompletion', 'ExamScore', 'StressLevel', 'Internet', 'FinalGrade']
        for col in key_cols:
            if col in self.df.columns:
                inspection_results['feature_ranges'][col] = {
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'mean': float(self.df[col].mean()),
                    'std': float(self.df[col].std())
                }
        return inspection_results

    @staticmethod
    def create_reference_risk_target(final_grade_series):
        """
        IMPORTANT TARGET RULE:
        Convert actual FinalGrade (0 to 3) into an academically defensible reference risk score (0 to 100).
        Higher academic performance (FinalGrade=3) corresponds to Lower Academic Risk.
        Lower academic performance (FinalGrade=0) corresponds to Higher Academic Risk.

        Mapping:
        FinalGrade = 3 (A/Distinction) -> Reference Risk = 10.0 (Very Low)
        FinalGrade = 2 (B/Good)        -> Reference Risk = 33.33 (Low)
        FinalGrade = 1 (C/Pass)        -> Reference Risk = 66.67 (High)
        FinalGrade = 0 (F/Fail)        -> Reference Risk = 90.0 (Very High)

        Continuous mapping formula: (3.0 - FinalGrade) / 3.0 * 100.0
        """
        # Continuous Risk Score (0-100)
        risk_score = (3.0 - final_grade_series.astype(float)) / 3.0 * 100.0
        risk_score = np.clip(risk_score, 0.0, 100.0)

        # Discrete Risk Category (0: Very Low, 1: Low, 2: Moderate, 3: High, 4: Very High)
        risk_category = np.zeros(len(final_grade_series), dtype=int)
        risk_category[risk_score <= 20.0] = 0
        risk_category[(risk_score > 20.0) & (risk_score <= 40.0)] = 1
        risk_category[(risk_score > 40.0) & (risk_score <= 60.0)] = 2
        risk_category[(risk_score > 60.0) & (risk_score <= 80.0)] = 3
        risk_category[risk_score > 80.0] = 4

        return risk_score, risk_category

    def prepare_data(self, test_size=0.2, random_state=42):
        """
        Prepare normalized features and reference target.
        Splits data reproducibly (80% train, 20% test).
        The test set is isolated from GA optimization.
        """
        if self.df is None:
            self.load_dataset()

        # Input features (normalized versions)
        norm_feature_cols = [
            'Attendance_norm',
            'StudyHours_norm',
            'AssignmentCompletion_norm',
            'ExamScore_norm',
            'StressLevel_norm',
            'Internet_norm'
        ]

        X = self.df[norm_feature_cols].copy()
        
        # Rename columns to standard feature names for processing
        X.columns = Config.INPUT_FEATURES

        # Target creation using create_reference_risk_target
        y_score, y_cat = self.create_reference_risk_target(self.df['FinalGrade'])

        # Train/Test Split (80/20 with stratification on risk category)
        X_tr, X_te, y_tr, y_te, y_tr_c, y_te_c = train_test_split(
            X, y_score, y_cat,
            test_size=test_size,
            random_state=random_state,
            stratify=y_cat
        )

        self.X_train = X_tr.reset_index(drop=True)
        self.X_test = X_te.reset_index(drop=True)
        self.y_train = pd.Series(y_tr).reset_index(drop=True)
        self.y_test = pd.Series(y_te).reset_index(drop=True)
        self.y_train_cat = pd.Series(y_tr_c).reset_index(drop=True)
        self.y_test_cat = pd.Series(y_te_c).reset_index(drop=True)

        return {
            'X_train': self.X_train,
            'X_test': self.X_test,
            'y_train': self.y_train,
            'y_test': self.y_test,
            'y_train_cat': self.y_train_cat,
            'y_test_cat': self.y_test_cat
        }

    @staticmethod
    def normalize_input(raw_dict):
        """
        Converts raw user inputs (e.g., Attendance=75%, StudyHours=20) into [0, 1] normalized values.
        """
        norm_dict = {}
        for feat, info in Config.FEATURE_RANGES.items():
            if feat in raw_dict:
                val = float(raw_dict[feat])
                f_min, f_max = info['min'], info['max']
                if f_max > f_min:
                    norm_val = (val - f_min) / (f_max - f_min)
                else:
                    norm_val = 0.0
                norm_dict[feat] = max(0.0, min(1.0, norm_val))
        return norm_dict

    @staticmethod
    def denormalize_input(norm_dict):
        """
        Converts [0, 1] normalized values back into human-understandable raw values.
        """
        raw_dict = {}
        for feat, info in Config.FEATURE_RANGES.items():
            if feat in norm_dict:
                n_val = float(norm_dict[feat])
                f_min, f_max = info['min'], info['max']
                r_val = n_val * (f_max - f_min) + f_min
                raw_dict[feat] = round(r_val, 1) if feat != 'Internet' else int(round(r_val))
        return raw_dict
