import os
import json
import uuid
import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from data_processor import DataProcessor
from risk_engine import RiskEngine
from recommendation_engine import RecommendationEngine
from genetic_algorithm import RealCodedGeneticAlgorithm
from evaluation import ModelEvaluation

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'Frontend'))
app.config.from_object(Config)

# Initialize Core Modules
dp = DataProcessor()
risk_engine = RiskEngine(use_optimized=True)
evaluator = ModelEvaluation(dp)

# Helper functions for users.json management
def load_users():
    users_file = Config.USERS_FILE
    if not os.path.exists(users_file):
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        with open(users_file, 'w') as f:
            json.dump({'users': []}, f, indent=2)
        return []
    try:
        with open(users_file, 'r') as f:
            data = json.load(f)
            return data.get('users', [])
    except Exception:
        return []

def save_users(users_list):
    users_file = Config.USERS_FILE
    os.makedirs(os.path.dirname(users_file), exist_ok=True)
    with open(users_file, 'w') as f:
        json.dump({'users': users_list}, f, indent=2)

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    users = load_users()
    for u in users:
        if u['id'] == user_id:
            return u
    return None

# ==================================================
# FRONTEND STATIC ROUTES
# ==================================================
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# ==================================================
# AUTHENTICATION API ENDPOINTS
# ==================================================
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required fields.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    users = load_users()
    for u in users:
        if u['email'] == email:
            return jsonify({'error': 'An account with this email already exists.'}), 400

    new_user = {
        'id': str(uuid.uuid4()),
        'name': name,
        'email': email,
        'password_hash': generate_password_hash(password),
        'registered_at': datetime.datetime.utcnow().isoformat(),
        'profile': {
            'student_id': f"STD-{np_random_id()}",
            'age': "20",
            'college': "Faculty of Science & Technology",
            'department': "Computer Science & Data Analytics",
            'course': "B.Tech Data Science & Soft Computing",
            'academic_year': "Year 3 (Sem 5)",
            'phone': "+1 555-0198",
            'city': "Academic City",
            'bio': "Passionate student focused on machine learning and soft computing algorithms."
        }
    }

    users.append(new_user)
    save_users(users)

    # Automatically set session
    session['user_id'] = new_user['id']
    session['user_name'] = new_user['name']

    user_payload = {
        'id': new_user['id'],
        'name': new_user['name'],
        'email': new_user['email'],
        'profile': new_user['profile']
    }
    return jsonify({'message': 'Registration successful.', 'user': user_payload}), 201

def np_random_id():
    import random
    return str(random.randint(10000, 99999))

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    users = load_users()
    user = None
    for u in users:
        if u['email'] == email:
            user = u
            break

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email credentials or password.'}), 401

    session['user_id'] = user['id']
    session['user_name'] = user['name']

    user_payload = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'profile': user['profile']
    }
    return jsonify({'message': 'Login successful.', 'user': user_payload}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully.'}), 200

@app.route('/api/profile', methods=['GET', 'PUT'])
def user_profile():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required.'}), 401

    if request.method == 'GET':
        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'profile': user['profile']
        })

    elif request.method == 'PUT':
        data = request.get_json() or {}
        users = load_users()
        for u in users:
            if u['id'] == user['id']:
                if 'name' in data and data['name'].strip():
                    u['name'] = data['name'].strip()
                if 'profile' in data and isinstance(data['profile'], dict):
                    u['profile'].update(data['profile'])
                save_users(users)
                return jsonify({
                    'message': 'Profile updated successfully.',
                    'user': {
                        'id': u['id'],
                        'name': u['name'],
                        'email': u['email'],
                        'profile': u['profile']
                    }
                }), 200
        return jsonify({'error': 'User record not found.'}), 44

# ==================================================
# RISK PREDICTION & WHAT-IF SIMULATOR ENDPOINTS
# ==================================================
@app.route('/api/predict', methods=['POST'])
def predict_academic_risk():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required.'}), 401

    data = request.get_json() or {}
    raw_inputs = {
        'Attendance': float(data.get('Attendance', 75.0)),
        'StudyHours': float(data.get('StudyHours', 18.0)),
        'AssignmentCompletion': float(data.get('AssignmentCompletion', 75.0)),
        'ExamScore': float(data.get('ExamScore', 65.0)),
        'StressLevel': float(data.get('StressLevel', 1.0)),
        'Internet': int(data.get('Internet', 1))
    }

    # Run Risk Engine Prediction
    result = risk_engine.predict_risk(raw_inputs, is_normalized=False)

    # Generate Personalized Recommendations
    recommendations = RecommendationEngine.generate_recommendations(
        raw_inputs,
        result['factor_contributions'],
        result['risk_score']
    )

    result['recommendations'] = recommendations
    return jsonify(result), 200

@app.route('/api/simulate', methods=['POST'])
def simulate_what_if():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required.'}), 401

    data = request.get_json() or {}
    current_inputs = data.get('current', {})
    simulated_inputs = data.get('simulated', {})

    # Calculate Current Risk Score
    current_res = risk_engine.predict_risk(current_inputs, is_normalized=False)
    
    # Calculate Simulated Risk Score using the exact SAME optimized fuzzy engine
    simulated_res = risk_engine.predict_risk(simulated_inputs, is_normalized=False)

    score_diff = round(simulated_res['risk_score'] - current_res['risk_score'], 1)

    # Identify improved and worsened factors
    factor_changes = []
    for feat in Config.INPUT_FEATURES:
        c_val = float(current_inputs.get(feat, 0))
        s_val = float(simulated_inputs.get(feat, 0))
        diff = s_val - c_val
        if abs(diff) > 0.01:
            unit = Config.FEATURE_RANGES[feat]['unit']
            # Determine if change is positive for student
            if feat == 'StressLevel':
                is_improved = diff < 0 # Lower stress is good
            else:
                is_improved = diff > 0 # Higher attendance/study/etc is good

            factor_changes.append({
                'factor': feat,
                'current_val': c_val,
                'simulated_val': s_val,
                'unit': unit,
                'change': round(diff, 1),
                'is_improved': is_improved
            })

    # Updated recommendations for simulated state
    sim_recommendations = RecommendationEngine.generate_recommendations(
        simulated_inputs,
        simulated_res['factor_contributions'],
        simulated_res['risk_score']
    )

    return jsonify({
        'current_risk_score': current_res['risk_score'],
        'current_risk_category': current_res['risk_category'],
        'simulated_risk_score': simulated_res['risk_score'],
        'simulated_risk_category': simulated_res['risk_category'],
        'risk_difference': score_diff,
        'is_risk_reduced': score_diff < 0,
        'factor_changes': factor_changes,
        'current_result': current_res,
        'simulated_result': simulated_res,
        'updated_recommendations': sim_recommendations
    }), 200

# ==================================================
# FUZZY SYSTEM & GA ENDPOINTS
# ==================================================
@app.route('/api/fuzzy/membership-functions', methods=['GET'])
def get_membership_functions():
    fuzzy = risk_engine.fuzzy_system
    return jsonify({
        'parameters': fuzzy.params,
        'output_grid': fuzzy.output_grid.tolist(),
        'feature_ranges': Config.FEATURE_RANGES
    })

@app.route('/api/fuzzy/rules', methods=['GET'])
def get_fuzzy_rules():
    fuzzy = risk_engine.fuzzy_system
    return jsonify({'rules': fuzzy.rules, 'total_rules': len(fuzzy.rules)})

@app.route('/api/ga/results', methods=['GET'])
def get_ga_results():
    if os.path.exists(Config.OPTIMIZED_PARAMS_FILE):
        eval_res = evaluator.evaluate_all()
        return jsonify({
            'status': 'Optimized Model Active',
            'parameters_file': Config.OPTIMIZED_PARAMS_FILE,
            'ga_history': eval_res['ga_history'],
            'improvement': eval_res['improvement']
        })
    else:
        return jsonify({'status': 'Baseline Model Active'}), 200

# ==================================================
# EVALUATION & ANALYTICS ENDPOINTS
# ==================================================
@app.route('/api/evaluation', methods=['GET'])
def get_model_evaluation():
    res = evaluator.evaluate_all()
    return jsonify(res)

@app.route('/api/analytics', methods=['GET'])
def get_dataset_analytics():
    info = dp.inspect_dataset()
    df = dp.df
    
    # Dataset Distribution Summaries for Frontend Charts
    grade_counts = df['FinalGrade'].value_counts().to_dict()
    grade_labels = {'3': 'Grade A (3)', '2': 'Grade B (2)', '1': 'Grade C (1)', '0': 'Grade F (0)'}
    formatted_grades = {grade_labels.get(str(k), str(k)): int(v) for k, v in grade_counts.items()}

    # Calculate average inputs per FinalGrade
    avg_by_grade = df.groupby('FinalGrade')[['Attendance', 'StudyHours', 'AssignmentCompletion', 'ExamScore', 'StressLevel']].mean().to_dict()

    return jsonify({
        'inspection': info,
        'grade_distribution': formatted_grades,
        'averages_by_grade': avg_by_grade
    })

if __name__ == '__main__':
    print("Starting Flask Backend Server for Academic Risk System...")
    app.run(host='127.0.0.1', port=5000, debug=True)
