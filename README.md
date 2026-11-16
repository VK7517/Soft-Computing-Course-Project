# Intelligent Student Academic Risk Scoring and Early Intervention System Using Optimized Fuzzy Logic

An academic Data Science / Soft Computing project aligned with **UN Sustainable Development Goal 4 (SDG 4: Quality Education)**.

---

## 🌟 Executive Summary

This system provides early detection and personalized intervention for students at risk of academic failure. By integrating **Mamdani Fuzzy Logic Inference** with a custom **Real-Coded Genetic Algorithm (RCGA)**, the model transforms multi-dimensional academic metrics into a continuous **Academic Risk Score (0–100%)** with full mathematical explainability and dynamic intervention strategies.

---

## 🎯 Sustainable Development Goal Alignment

* **SDG 4 – Quality Education**: Target 4.1 & 4.4 — Reducing student dropout rates, enhancing academic retention, and promoting equitable learning outcomes through intelligent early warning analytics.

---

## 📊 Dataset & Feature Specification

* **Source File**: `Dataset/full_dataset_normalized.csv`
* **Total Dataset Size**: 12,469 student records (35 columns)
* **Missing Values**: 0
* **Duplicate Records**: 0

### Predictive Input Variables (6 Features)
| Input Feature | Raw Range | Normalized Range | Description |
| :--- | :--- | :--- | :--- |
| **Attendance** | 60% – 100% | `0.0 – 1.0` | Class attendance percentage |
| **Study Hours** | 5 – 44 hrs/wk | `0.0 – 1.0` | Weekly independent study hours |
| **Assignment Completion** | 50% – 100% | `0.0 – 1.0` | Percentage of continuous coursework submitted |
| **Exam Score** | 40 – 100 marks | `0.0 – 1.0` | Midterm / internal assessment marks |
| **Stress Level** | 0 – 2 (Low, Med, High) | `0.0 – 1.0` | Self-reported psychological stress level |
| **Internet Availability** | 0 / 1 (Binary) | `0.0 – 1.0` | Home broadband / digital resource access |

### Target Feature & Reference Risk Mapping
* **Target Feature**: `FinalGrade` (Values: `0, 1, 2, 3`)
* **Target Rule**: `FinalGrade` is **NEVER** used as a predictive input. It is converted into an academic outcome reference risk score via `create_reference_risk_target()`:
  * $\text{FinalGrade} = 3$ (Highest Performance) $\rightarrow \text{Reference Risk} = 10.0\%$ (Very Low Risk)
  * $\text{FinalGrade} = 2 \rightarrow \text{Reference Risk} = 33.33\%$ (Low Risk)
  * $\text{FinalGrade} = 1 \rightarrow \text{Reference Risk} = 66.67\%$ (High Risk)
  * $\text{FinalGrade} = 0$ (Course Failure) $\rightarrow \text{Reference Risk} = 90.0\%$ (Very High Risk)

---

## 🧠 Soft Computing Architecture

### 1. Mamdani Fuzzy Inference System
* **Fuzzification**: Triangular ($\text{trimf}$) and Trapezoidal ($\text{trapmf}$) membership functions for linguistic terms (`Low`, `Medium`, `High`).
* **Rule Base**: 30 domain-expert rules evaluating input combinations (e.g., *IF Attendance is Low AND Study Hours is Low THEN Risk is Very High*).
* **Aggregation**: $\text{MIN}$ antecedent rule firing strength; $\text{MAX}$ output composition over output grid $[0, 100]$.
* **Defuzzification**: Centroid (Center of Gravity) COG method yielding a continuous Risk Score ($z^*$).

### 2. Real-Coded Genetic Algorithm (RCGA)
* **Chromosome Representation**: 63-element real-valued vector representing membership function parameters.
* **Fitness Function**: Evaluates candidate chromosomes on training data ($N=9,975$):
  $$\text{Fitness} = 0.6 \cdot F1_{\text{macro}} + 0.4 \cdot \left(\frac{100}{100 + \text{RMSE}}\right)$$
* **Selection**: Tournament Selection ($k=3$).
* **Crossover**: Blend Crossover ($\text{BLX-0.5}$).
* **Mutation**: Bounded Gaussian Mutation ($\sigma=0.05$).
* **Elitism**: Retains top 2 elite chromosomes per generation.
* **Optimized Parameters Saved To**: `Backend/models/optimized_parameters.json`.

---

## 📈 Model Evaluation (20% Isolated Test Set, N=2,494)

| Metric | Baseline Fuzzy Model | GA-Optimized Fuzzy Model | Empirical Improvement |
| :--- | :--- | :--- | :--- |
| **Accuracy** | 35.8% | **61.4%** | **+25.6%** |
| **F1-Score (Macro)** | 0.285 | **0.582** | **+0.297** |
| **RMSE (Error)** | 42.60 | **28.45** | **-14.15 (33.2% error reduction)** |
| **MAE (Mean Abs Error)** | 36.50 | **22.10** | **-14.40** |
| **ROC / AUC (OVR)** | 0.612 | **0.785** | **+0.173** |

---

## 🛠️ Technology Stack & Architecture

```
HTML5 / CSS3 / Vanilla JS Frontend
            ↕ REST API (JSON)
Flask Python Backend Server
            ↕ Processing & Inference
Fuzzy System & RCGA Optimizer (NumPy, SciPy, scikit-learn)
            ↕
Dataset (full_dataset_normalized.csv)
```

---

## 📂 Project Folder Structure

```
Soft_Computing/
│
├── Dataset/
│   └── full_dataset_normalized.csv
│
├── Frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── css/
│   │   ├── style.css
│   │   ├── login.css
│   │   └── dashboard.css
│   ├── js/
│   │   ├── auth.js
│   │   ├── dashboard.js
│   │   ├── profile.js
│   │   ├── risk.js
│   │   ├── simulator.js
│   │   └── charts.js
│   └── assets/
│       ├── logo.svg
│       ├── student.svg
│       ├── education.svg
│       ├── risk.svg
│       ├── fuzzy.svg
│       └── icons/
│
├── Backend/
│   ├── app.py
│   ├── config.py
│   ├── data_processor.py
│   ├── fuzzy_system.py
│   ├── genetic_algorithm.py
│   ├── risk_engine.py
│   ├── recommendation_engine.py
│   ├── explainability.py
│   ├── evaluation.py
│   ├── requirements.txt
│   ├── data/
│   │   └── users.json
│   └── models/
│       └── optimized_parameters.json
│
└── README.md
```

---

## 🚀 How to Run the Project

### 1. Install Dependencies
Navigate to `Backend/` directory and install dependencies:
```bash
pip install -r Backend/requirements.txt
```

### 2. Run Flask Backend Server
```bash
python Backend/app.py
```
* The backend server will start at `http://127.0.0.1:5000/`.

### 3. Access Frontend
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```
* Log in or register a new student account to access the interactive dashboard, what-if simulator, fuzzy rule explorer, and model evaluation metrics.

---

## 📌 Features Included
1. **Authenticated User Management**: PBKDF2 hashed passwords stored in `users.json`.
2. **Student Risk Assessment**: Interactive sliders for 6 input features generating real-time risk score (0-100%).
3. **What-If Scenario Simulator**: Side-by-side comparison of current vs projected risk scores.
4. **Transparent Explainability**: Mathematical factor contribution percentages & activated rule firing strengths.
5. **Dynamic Recommendations**: Actionable interventions customized to student deficits.
6. **Academic Visual Asset Suite**: SVG logos, student graphics, membership function curves, and Chart.js dashboards.

---

## 🔬 Limitations & Future Scope
* **Limitations**: Dataset features are static snapshots per term; real-time weekly LMS telemetry could enhance dynamic tracking.
* **Future Scope**: Integration with LMS APIs (Canvas/Moodle), automated email alerts to academic advisors, and adaptive fuzzy neural networks (ANFIS).
