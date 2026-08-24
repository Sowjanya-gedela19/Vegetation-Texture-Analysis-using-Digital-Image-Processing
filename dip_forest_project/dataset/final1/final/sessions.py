from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import StudySession, Subject, db
from datetime import datetime, timedelta

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('', methods=['GET'])
@sessions_bp.route('/', methods=['GET'])
@jwt_required()
def get_sessions():
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        subject_id = request.args.get('subject_id', type=int)
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)

        query = StudySession.query.join(Subject).filter(Subject.user_id == current_user_id)

        if subject_id:
            query = query.filter(StudySession.subject_id == subject_id)

        sessions = query.order_by(StudySession.timestamp.desc()).limit(limit).offset(offset).all()

        return jsonify([session.to_dict() for session in sessions]), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@sessions_bp.route('', methods=['POST'])
@sessions_bp.route('/', methods=['POST'])
@jwt_required()
def create_session():
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        subject_id = data.get('subject_id')
        time_spent = data.get('time_spent')
        topic = data.get('topic', '')
        focus_level = data.get('focus_level')
        notes = data.get('notes', '')

        if not subject_id:
            return jsonify({'error': 'Subject ID is required'}), 400

        if not time_spent or time_spent <= 0:
            return jsonify({'error': 'Valid time spent is required'}), 400

        subject = Subject.query.filter_by(id=subject_id, user_id=current_user_id).first()
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404

        if focus_level is not None and (focus_level < 1 or focus_level > 10):
            return jsonify({'error': 'Focus level must be between 1 and 10'}), 400

        session_obj = StudySession(
            subject_id=subject_id,
            time_spent=time_spent,
            topic=topic,
            focus_level=focus_level,
            notes=notes
        )

        db.session.add(session_obj)
        db.session.commit()

        return jsonify({
            'message': 'Study session created successfully',
            'session': session_obj.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@sessions_bp.route('/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        session_obj = StudySession.query.join(Subject).filter(
            StudySession.id == session_id,
            Subject.user_id == current_user_id
        ).first()

        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify(session_obj.to_dict()), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@sessions_bp.route('/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_session(session_id):
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        session_obj = StudySession.query.join(Subject).filter(
            StudySession.id == session_id,
            Subject.user_id == current_user_id
        ).first()

        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if 'time_spent' in data:
            if data['time_spent'] <= 0:
                return jsonify({'error': 'Time spent must be greater than 0'}), 400
            session_obj.time_spent = data['time_spent']

        if 'topic' in data:
            session_obj.topic = data['topic']

        if 'focus_level' in data:
            if data['focus_level'] is not None and (data['focus_level'] < 1 or data['focus_level'] > 10):
                return jsonify({'error': 'Focus level must be between 1 and 10'}), 400
            session_obj.focus_level = data['focus_level']

        if 'notes' in data:
            session_obj.notes = data['notes']

        db.session.commit()

        return jsonify({
            'message': 'Session updated successfully',
            'session': session_obj.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@sessions_bp.route('/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        session_obj = StudySession.query.join(Subject).filter(
            StudySession.id == session_id,
            Subject.user_id == current_user_id
        ).first()

        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404

        db.session.delete(session_obj)
        db.session.commit()

        return jsonify({'message': 'Session deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@sessions_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        days = request.args.get('days', type=int, default=7)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        sessions = StudySession.query.join(Subject).filter(
            Subject.user_id == current_user_id,
            StudySession.timestamp >= start_date,
            StudySession.timestamp <= end_date
        ).all()

        total_time = sum(s.time_spent for s in sessions)
        total_sessions = len(sessions)
        focus_levels = [s.focus_level for s in sessions if s.focus_level is not None]
        avg_focus = sum(focus_levels) / len(focus_levels) if focus_levels else 0

        daily_data = {}
        subject_data = {}

        for s in sessions:
            date_key = s.timestamp.date().isoformat()
            daily_data.setdefault(date_key, {'time': 0, 'sessions': 0})
            daily_data[date_key]['time'] += s.time_spent
            daily_data[date_key]['sessions'] += 1

            subject_name = s.subject.name
            subject_data.setdefault(subject_name, {'time': 0, 'sessions': 0, 'color': s.subject.color})
            subject_data[subject_name]['time'] += s.time_spent
            subject_data[subject_name]['sessions'] += 1

        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_time': round(total_time, 2),
                'total_sessions': total_sessions,
                'average_focus_level': round(avg_focus, 1),
                'average_time_per_session': round(total_time / total_sessions, 2) if total_sessions > 0 else 0
            },
            'daily_breakdown': daily_data,
            'subject_breakdown': subject_data
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@sessions_bp.route('/streak', methods=['GET'])
@jwt_required()
def get_streak():
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        sessions = StudySession.query.join(Subject).filter(
            Subject.user_id == current_user_id
        ).order_by(StudySession.timestamp.desc()).all()

        if not sessions:
            return jsonify({'current_streak': 0, 'longest_streak': 0}), 200

        sessions_by_date = {}
        for s in sessions:
            date_key = s.timestamp.date()
            sessions_by_date.setdefault(date_key, []).append(s)

        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        dates = sorted(sessions_by_date.keys(), reverse=True)
        today = datetime.utcnow().date()

        for i, date in enumerate(dates):
            if i == 0 and date == today:
                temp_streak = 1
                current_streak = 1
            elif i == 0 and date == today - timedelta(days=1):
                temp_streak = 1
                current_streak = 1
            elif i > 0:
                prev_date = dates[i - 1]
                if (prev_date - date).days == 1:
                    temp_streak += 1
                    if i == 1:
                        current_streak = temp_streak
                else:
                    longest_streak = max(longest_streak, temp_streak)
                    temp_streak = 1

            longest_streak = max(longest_streak, temp_streak)

        return jsonify({'current_streak': current_streak, 'longest_streak': longest_streak}), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
