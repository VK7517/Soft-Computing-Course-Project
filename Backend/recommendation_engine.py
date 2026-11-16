from config import Config

class RecommendationEngine:
    """
    Dynamic Recommendation Engine for Academic Early Intervention.
    Generates actionable, personalized academic advice based on real student inputs and risk analysis.
    """
    @staticmethod
    def generate_recommendations(raw_inputs, factor_contributions, risk_score):
        """
        Generates tailored recommendations based on raw student inputs and factor impact analysis.
        """
        recommendations = []

        attendance = raw_inputs.get('Attendance', 100)
        study_hours = raw_inputs.get('StudyHours', 20)
        assignment = raw_inputs.get('AssignmentCompletion', 100)
        exam_score = raw_inputs.get('ExamScore', 100)
        stress_level = raw_inputs.get('StressLevel', 0)
        internet = raw_inputs.get('Internet', 1)

        # 1. Attendance Recommendation
        if attendance < 75.0:
            recommendations.append({
                'factor': 'Attendance',
                'current_condition': f"{attendance}% (Below 75% Threshold)",
                'why_it_matters': 'Low class attendance strongly correlates with missing key conceptual lectures and failing end-term assessments.',
                'action': 'Prioritize attending all remaining lectures, log attendance regularly, and schedule a meeting with class tutors to cover missed topics.',
                'priority': 'Urgent' if attendance < 65.0 else 'High',
                'category': 'Academic Discipline'
            })
        elif attendance < 85.0:
            recommendations.append({
                'factor': 'Attendance',
                'current_condition': f"{attendance}% (Moderate Attendance)",
                'why_it_matters': 'Maintaining attendance above 85% ensures complete coverage of course material and eligibility for bonus continuous evaluation marks.',
                'action': 'Aim for 90%+ attendance over the upcoming weeks by setting morning reminders and tracking daily schedule.',
                'priority': 'Moderate',
                'category': 'Academic Discipline'
            })

        # 2. Study Hours Recommendation
        if study_hours < 15.0:
            recommendations.append({
                'factor': 'Study Hours',
                'current_condition': f"{study_hours} hrs/week (Insufficient Independent Study)",
                'why_it_matters': 'Fewer than 15 study hours weekly leaves inadequate time for revision, problem-solving, and deep comprehension.',
                'action': 'Implement a weekly study timetable. Increase self-study by 1.5 hours daily using 25-minute Pomodoro sessions.',
                'priority': 'Urgent' if study_hours < 10.0 else 'High',
                'category': 'Study Habits'
            })
        elif study_hours < 22.0:
            recommendations.append({
                'factor': 'Study Hours',
                'current_condition': f"{study_hours} hrs/week (Average Study Load)",
                'why_it_matters': 'Increasing weekly study hours slightly will improve confidence in technical assignments and midterm preparations.',
                'action': 'Allocate 2 additional dedicated study blocks per weekend focusing on challenging subjects.',
                'priority': 'Moderate',
                'category': 'Study Habits'
            })

        # 3. Assignment Completion Recommendation
        if assignment < 75.0:
            recommendations.append({
                'factor': 'Assignment Completion',
                'current_condition': f"{assignment}% (Significant Pending Assignments)",
                'why_it_matters': 'Incomplete assignments lead to direct loss of continuous assessment marks and weak preparation for exams.',
                'action': 'Break large assignments into daily sub-tasks. Utilize instructor office hours or peer study groups to clear bottlenecks.',
                'priority': 'Urgent' if assignment < 60.0 else 'High',
                'category': 'Assessment & Tasks'
            })
        elif assignment < 90.0:
            recommendations.append({
                'factor': 'Assignment Completion',
                'current_condition': f"{assignment}% (Minor Assignment Gaps)",
                'why_it_matters': 'Completing 100% of coursework maximizes internal grade safety margins.',
                'action': 'Set submission reminders 48 hours prior to official deadlines to ensure buffer time for review.',
                'priority': 'Moderate',
                'category': 'Assessment & Tasks'
            })

        # 4. Exam Score Recommendation
        if exam_score < 60.0:
            recommendations.append({
                'factor': 'Exam Score',
                'current_condition': f"{exam_score}/100 (Below Passing/Safety Threshold)",
                'why_it_matters': 'Low exam scores reflect gaps in core concept mastery and increase overall course risk.',
                'action': 'Review past exam solutions, solve practice problem sets under timed conditions, and request remedial mentoring from faculty.',
                'priority': 'Urgent' if exam_score < 50.0 else 'High',
                'category': 'Exam Preparation'
            })
        elif exam_score < 75.0:
            recommendations.append({
                'factor': 'Exam Score',
                'current_condition': f"{exam_score}/100 (Moderate Performance)",
                'why_it_matters': 'Focusing on high-weightage exam topics can elevate your overall grade to top tier.',
                'action': 'Focus revision on complex syllabus modules and practice sample mock tests.',
                'priority': 'Moderate',
                'category': 'Exam Preparation'
            })

        # 5. Stress Level Recommendation
        if stress_level >= 2.0 or stress_level == 'High':
            recommendations.append({
                'factor': 'Stress Level',
                'current_condition': 'High Stress Level',
                'why_it_matters': 'High academic burnout impairs memory retention, exam performance, and overall well-being.',
                'action': 'Access campus wellness counseling, adopt structured breaks, and consult academic advisors for workload balancing.',
                'priority': 'High',
                'category': 'Wellness & Support'
            })
        elif stress_level == 1.0 or stress_level == 'Medium':
            recommendations.append({
                'factor': 'Stress Level',
                'current_condition': 'Moderate Stress Level',
                'why_it_matters': 'Unmanaged moderate stress can escalate during exam periods.',
                'action': 'Incorporate daily physical activity, mindfulness breaks, and balanced sleep schedules.',
                'priority': 'Low',
                'category': 'Wellness & Support'
            })

        # 6. Internet Availability Recommendation
        if internet == 0 or internet == 'Unavailable' or internet == 0.0:
            recommendations.append({
                'factor': 'Internet Availability',
                'current_condition': 'Limited / Unavailable Personal Internet Access',
                'why_it_matters': 'Lack of home internet restricts access to digital learning repositories, online lectures, and e-submissions.',
                'action': 'Utilize campus library Wi-Fi labs, download course materials for offline study, and request offline textbook access.',
                'priority': 'High',
                'category': 'Learning Resources'
            })

        # If student is doing exceptionally well
        if not recommendations or risk_score <= 20.0:
            recommendations.append({
                'factor': 'Overall Academic Performance',
                'current_condition': 'Excellent Academic Standing (Very Low Risk)',
                'why_it_matters': 'Consistent top performance opens opportunities for research assistantships, honors programs, and peer mentoring.',
                'action': 'Maintain existing study discipline, participate in academic competitions or research projects, and mentor peers.',
                'priority': 'Low',
                'category': 'Enrichment'
            })

        return recommendations
