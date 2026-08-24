# 1. Import the functools library
import functools
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Subject, StudySession, AudioNote, db
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Decorator to check if user is admin"""
    def decorator(f):
        # 2. This line preserves the original function's name and metadata
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # The rest of your decorator logic is perfect and remains unchanged
            current_user_id = get_jwt_identity()['id']
            user = User.query.get(current_user_id)
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_admin()
def admin_dashboard():
    try:
        # Get overall statistics
        total_users = User.query.count()
        total_subjects = Subject.query.count()
        total_sessions = StudySession.query.count()
        total_audio_notes = AudioNote.query.count()
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= week_ago).count()
        recent_sessions = StudySession.query.filter(StudySession.timestamp >= week_ago).count()
        recent_audio = AudioNote.query.filter(AudioNote.timestamp >= week_ago).count()
        
        # Get daily activity for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_sessions = db.session.query(
            func.date(StudySession.timestamp).label('date'),
            func.count(StudySession.id).label('count')
        ).filter(StudySession.timestamp >= thirty_days_ago)\
         .group_by(func.date(StudySession.timestamp))\
         .order_by(func.date(StudySession.timestamp))\
         .all()
        
        daily_data = {str(row.date): row.count for row in daily_sessions}
        
        # Get top subjects
        top_subjects = db.session.query(
            Subject.name,
            func.count(StudySession.id).label('session_count'),
            func.sum(StudySession.time_spent).label('total_time')
        ).join(StudySession)\
         .group_by(Subject.id, Subject.name)\
         .order_by(func.sum(StudySession.time_spent).desc())\
         .limit(10)\
         .all()
        
        top_subjects_data = [
            {
                'name': subject.name,
                'sessions': subject.session_count,
                'total_time': round(subject.total_time, 2)
            }
            for subject in top_subjects
        ]
        
        dashboard_data = {
            'overview': {
                'total_users': total_users,
                'total_subjects': total_subjects,
                'total_sessions': total_sessions,
                'total_audio_notes': total_audio_notes
            },
            'recent_activity': {
                'new_users': recent_users,
                'new_sessions': recent_sessions,
                'new_audio_notes': recent_audio
            },
            'daily_activity': daily_data,
            'top_subjects': top_subjects_data
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin()
def get_users():
    try:
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=20)
        
        users = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        user_data = []
        for user in users.items:
            # Get user statistics
            session_count = StudySession.query.join(Subject).filter(Subject.user_id == user.id).count()
            audio_count = AudioNote.query.filter_by(user_id=user.id).count()
            
            user_data.append({
                **user.to_dict(),
                'session_count': session_count,
                'audio_note_count': audio_count
            })
        
        return jsonify({
            'users': user_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@require_admin()
def get_user_details(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's subjects
        subjects = Subject.query.filter_by(user_id=user_id).all()
        
        # Get user's study sessions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sessions = StudySession.query.join(Subject).filter(
            Subject.user_id == user_id,
            StudySession.timestamp >= thirty_days_ago
        ).all()
        
        # Get user's audio notes (last 30 days)
        recent_audio = AudioNote.query.filter(
            AudioNote.user_id == user_id,
            AudioNote.timestamp >= thirty_days_ago
        ).all()
        
        user_details = {
            **user.to_dict(),
            'subjects': [subject.to_dict() for subject in subjects],
            'recent_activity': {
                'sessions': len(recent_sessions),
                'audio_notes': len(recent_audio),
                'total_study_time': round(sum(s.time_spent for s in recent_sessions), 2)
            }
        }
        
        return jsonify(user_details), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@require_admin()
def update_user_role(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({'error': 'Role is required'}), 400
        
        new_role = data['role']
        if new_role not in ['student', 'admin']:
            return jsonify({'error': 'Invalid role. Must be student or admin'}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/subjects/categories', methods=['GET'])
@jwt_required()
@require_admin()
def get_subject_categories():
    try:
        # Get all unique subject names and their usage statistics
        subjects = db.session.query(
            Subject.name,
            func.count(Subject.id).label('usage_count'),
            func.count(User.id.distinct()).label('user_count')
        ).join(User)\
         .group_by(Subject.name)\
         .order_by(func.count(Subject.id).desc())\
         .all()
        
        categories = [
            {
                'name': subject.name,
                'usage_count': subject.usage_count,
                'user_count': subject.user_count
            }
            for subject in subjects
        ]
        
        return jsonify(categories), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/subjects/categories', methods=['POST'])
@jwt_required()
@require_admin()
def create_subject_category():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Category name is required'}), 400
        
        category_name = data['name'].strip()
        if not category_name:
            return jsonify({'error': 'Category name cannot be empty'}), 400
        
        # Check if category already exists
        existing = Subject.query.filter_by(name=category_name).first()
        if existing:
            return jsonify({'error': 'Category already exists'}), 409
        
        # Create a sample subject with this category (for admin user)
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            sample_subject = Subject(
                name=category_name,
                user_id=admin_user.id,
                color='#3B82F6'
            )
            db.session.add(sample_subject)
            db.session.commit()
        
        return jsonify({
            'message': 'Subject category created successfully',
            'category': category_name
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/subjects/categories/<category_name>', methods=['DELETE'])
@jwt_required()
@require_admin()
def delete_subject_category(category_name):
    try:
        # Find all subjects with this category
        subjects = Subject.query.filter_by(name=category_name).all()
        
        if not subjects:
            return jsonify({'error': 'Category not found'}), 404
        
        # Delete all subjects with this category
        for subject in subjects:
            db.session.delete(subject)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Category "{category_name}" deleted successfully',
            'deleted_subjects': len(subjects)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/audio/monitor', methods=['GET'])
@jwt_required()
@require_admin()
def monitor_audio_notes():
    try:
        # Get recent audio notes for monitoring
        recent_audio = AudioNote.query\
            .order_by(AudioNote.timestamp.desc())\
            .limit(50)\
            .all()
        
        audio_data = []
        for note in recent_audio:
            user = User.query.get(note.user_id)
            audio_data.append({
                'id': note.id,
                'user_email': user.email if user else 'Unknown',
                'transcript': note.transcript,
                'duration': note.duration,
                'timestamp': note.timestamp.isoformat(),
                'audio_url': note.audio_url
            })
        
        return jsonify(audio_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/audio/<int:note_id>/flag', methods=['POST'])
@jwt_required()
@require_admin()
def flag_audio_note(note_id):
    try:
        audio_note = AudioNote.query.get(note_id)
        if not audio_note:
            return jsonify({'error': 'Audio note not found'}), 404
        
        data = request.get_json()
        reason = data.get('reason', 'Flagged by admin')
        
        # In a real application, you might want to add a 'flagged' field to the AudioNote model
        # For now, we'll just return a success message
        return jsonify({
            'message': 'Audio note flagged successfully',
            'note_id': note_id,
            'reason': reason
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/analytics/usage', methods=['GET'])
@jwt_required()
@require_admin()
def get_usage_analytics():
    try:
        # Get date range from query parameters
        days = request.args.get('days', type=int, default=30)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Daily user activity
        daily_users = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= start_date)\
         .group_by(func.date(User.created_at))\
         .order_by(func.date(User.created_at))\
         .all()
        
        # Daily session activity
        daily_sessions = db.session.query(
            func.date(StudySession.timestamp).label('date'),
            func.count(StudySession.id).label('count'),
            func.sum(StudySession.time_spent).label('total_time')
        ).filter(StudySession.timestamp >= start_date)\
         .group_by(func.date(StudySession.timestamp))\
         .order_by(func.date(StudySession.timestamp))\
         .all()
        
        # User engagement metrics
        active_users = db.session.query(func.count(User.id.distinct()))\
            .join(Subject)\
            .join(StudySession)\
            .filter(StudySession.timestamp >= start_date)\
            .scalar()
        
        total_users = User.query.count()
        engagement_rate = (active_users / total_users * 100) if total_users > 0 else 0
        
        analytics = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'daily_users': {str(row.date): row.count for row in daily_users},
            'daily_sessions': {
                str(row.date): {
                    'count': row.count,
                    'total_time': round(row.total_time, 2)
                }
                for row in daily_sessions
            },
            'engagement': {
                'active_users': active_users,
                'total_users': total_users,
                'engagement_rate': round(engagement_rate, 2)
            }
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
