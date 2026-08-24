from flask import Blueprint, request, jsonify
from models import User, Subject, StudySession, AudioNote, db
from datetime import datetime, timedelta
import os
import google.generativeai as genai

ai_bp = Blueprint('ai', __name__)

def get_study_data_for_ai(user_id, days=7):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    sessions = StudySession.query.join(Subject).filter(
        Subject.user_id == user_id,
        StudySession.timestamp >= start_date,
        StudySession.timestamp <= end_date
    ).all()

    audio_notes = AudioNote.query.filter(
        AudioNote.user_id == user_id,
        AudioNote.timestamp >= start_date,
        AudioNote.timestamp <= end_date
    ).all()

    user = User.query.get(user_id)

    study_data = {
        'user_goal': user.academic_goal or 'Not specified',
        'focus_areas': user.focus_areas or 'Not specified',
        'period': f"Last {days} days",
        'sessions': []
    }

    subject_sessions = {}
    for session in sessions:
        subject_name = session.subject.name
        if subject_name not in subject_sessions:
            subject_sessions[subject_name] = {
                'total_time': 0,
                'sessions': 0,
                'focus_levels': [],
                'topics': []
            }

        subject_sessions[subject_name]['total_time'] += session.time_spent
        subject_sessions[subject_name]['sessions'] += 1
        if session.focus_level:
            subject_sessions[subject_name]['focus_levels'].append(session.focus_level)
        if session.topic:
            subject_sessions[subject_name]['topics'].append(session.topic)

    study_data['subjects'] = subject_sessions

    study_data['reflections'] = [
        {
            'transcript': note.transcript,
            'timestamp': note.timestamp.isoformat()
        }
        for note in audio_notes if note.transcript
    ]

    return study_data

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_ai_suggestions(study_data):
    try:
        prompt = f"""
        You are an AI study coach analyzing a student's learning progress. Here's the student's data:

        Academic Goal: {study_data['user_goal']}
        Focus Areas: {study_data['focus_areas']}
        Analysis Period: {study_data['period']}

        Study Sessions by Subject:
        """
        for subject, data in study_data['subjects'].items():
            avg_focus = sum(data['focus_levels']) / len(data['focus_levels']) if data['focus_levels'] else 0
            prompt += f"""
            - {subject}:
              * Total time: {data['total_time']} hours
              * Sessions: {data['sessions']}
              * Average focus level: {avg_focus:.1f}/10
              * Topics covered: {', '.join(data['topics'][:5])}
            """
        if study_data['reflections']:
            prompt += f"""
            Recent Reflections:
            {chr(10).join([f"- {r['transcript']}" for r in study_data['reflections'][:3]])}
            """

        prompt += """
        Based on this data, provide:
        1. 2-3 specific, actionable study suggestions
        2. 1-2 areas that need attention
        3. 1 motivational message
        4. A brief analysis of study patterns

        Format your response as JSON with these keys: suggestions, attention_areas, motivation, pattern_analysis
        Keep each suggestion under 100 words and be encouraging but realistic.
        """

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error generating suggestions: {str(e)}"

@ai_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    try:
        user_id = 1  # Replace this with actual user logic later
        days = request.args.get('days', type=int, default=7)

        study_data = get_study_data_for_ai(user_id, days)

        total_sessions = sum(data['sessions'] for data in study_data['subjects'].values())
        if total_sessions == 0:
            return jsonify({
                'suggestions': [
                    "Start by logging your first study session to get personalized suggestions!",
                    "Set up your academic goals in your profile to receive targeted advice."
                ],
                'attention_areas': ["No study data available yet"],
                'motivation': "Every expert was once a beginner. Start your learning journey today!",
                'pattern_analysis': "No patterns to analyze yet. Begin studying to see insights."
            }), 200

        ai_response = generate_ai_suggestions(study_data)

        try:
            import json
            suggestions = json.loads(ai_response)
        except:
            suggestions = {
                'suggestions': [
                    "Focus on maintaining consistent study sessions",
                    "Try to improve your focus levels gradually"
                ],
                'attention_areas': ["Study consistency"],
                'motivation': "Keep up the great work!",
                'pattern_analysis': ai_response
            }

        return jsonify(suggestions), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@ai_bp.route('/weekly-insights', methods=['GET'])
def get_weekly_insights():
    try:
        user_id = 1  # Replace with actual user logic
        study_data = get_study_data_for_ai(user_id, 7)

        total_time = sum(data['total_time'] for data in study_data['subjects'].values())
        total_sessions = sum(data['sessions'] for data in study_data['subjects'].values())

        subjects = study_data['subjects']
        if subjects:
            most_studied = max(subjects.items(), key=lambda x: x[1]['total_time'])
            least_studied = min(subjects.items(), key=lambda x: x[1]['total_time'])
        else:
            most_studied = least_studied = (None, {'total_time': 0})

        all_focus_levels = []
        for subject_data in subjects.values():
            all_focus_levels.extend(subject_data['focus_levels'])

        avg_focus = sum(all_focus_levels) / len(all_focus_levels) if all_focus_levels else 0

        insights = {
            'total_study_time': round(total_time, 2),
            'total_sessions': total_sessions,
            'average_focus_level': round(avg_focus, 1),
            'most_studied_subject': {
                'name': most_studied[0],
                'time': most_studied[1]['total_time']
            },
            'least_studied_subject': {
                'name': least_studied[0],
                'time': least_studied[1]['total_time']
            },
            'reflection_count': len(study_data['reflections']),
            'subjects_studied': len(subjects)
        }

        return jsonify(insights), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@ai_bp.route('/subject-feedback/<int:subject_id>', methods=['GET'])
def get_subject_feedback(subject_id):
    try:
        user_id = 1  # Replace with actual user logic

        subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        sessions = StudySession.query.filter(
            StudySession.subject_id == subject_id,
            StudySession.timestamp >= start_date,
            StudySession.timestamp <= end_date
        ).all()

        if not sessions:
            return jsonify({
                'subject_name': subject.name,
                'feedback': f"No recent study sessions for {subject.name}. Start studying to get personalized feedback!",
                'suggestions': [
                    "Schedule regular study sessions for this subject",
                    "Set specific goals for what you want to learn"
                ]
            }), 200

        total_time = sum(session.time_spent for session in sessions)
        focus_levels = [s.focus_level for s in sessions if s.focus_level]
        avg_focus = sum(focus_levels) / len(focus_levels) if focus_levels else 0
        topics = [s.topic for s in sessions if s.topic]

        prompt = f"""
        Analyze this student's performance in {subject.name}:

        - Total study time: {total_time} hours (last 30 days)
        - Number of sessions: {len(sessions)}
        - Average focus level: {avg_focus:.1f}/10
        - Topics covered: {', '.join(topics[:10])}

        Provide:
        1. A brief analysis of their performance
        2. 2-3 specific suggestions for improvement
        3. 1-2 strengths to build upon

        Keep it encouraging and actionable.
        """

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            feedback = response.text
        except:
            feedback = f"Great work studying {subject.name}! Keep up the consistent effort."

        return jsonify({
            'subject_name': subject.name,
            'feedback': feedback,
            'stats': {
                'total_time': round(total_time, 2),
                'sessions': len(sessions),
                'average_focus': round(avg_focus, 1)
            }
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
