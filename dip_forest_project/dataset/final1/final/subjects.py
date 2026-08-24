from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Subject, db
import random

subjects_bp = Blueprint('subjects', __name__)

# Predefined colors for subjects
SUBJECT_COLORS = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#06B6D4', '#F97316', '#84CC16', '#EC4899', '#6366F1'
]

@subjects_bp.route('/', methods=['GET'])
@jwt_required()
def get_subjects():
    try:
        current_user_id = get_jwt_identity()
        subjects = Subject.query.filter_by(user_id=current_user_id).all()
        
        return jsonify([subject.to_dict() for subject in subjects]), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@subjects_bp.route('/', methods=['POST'])
@jwt_required()
def create_subject():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name')
        color = data.get('color')
        
        if not name:
            return jsonify({'error': 'Subject name is required'}), 400
        
        # Check if subject already exists for this user
        existing_subject = Subject.query.filter_by(
            user_id=current_user_id, 
            name=name
        ).first()
        
        if existing_subject:
            return jsonify({'error': 'Subject with this name already exists'}), 409
        
        # Assign random color if not provided
        if not color:
            color = random.choice(SUBJECT_COLORS)
        
        # Create new subject
        subject = Subject(
            name=name,
            color=color,
            user_id=current_user_id
        )
        
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@subjects_bp.route('/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_subject(subject_id):
    try:
        current_user_id = get_jwt_identity()
        subject = Subject.query.filter_by(
            id=subject_id, 
            user_id=current_user_id
        ).first()
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        return jsonify(subject.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@subjects_bp.route('/<int:subject_id>', methods=['PUT'])
@jwt_required()
def update_subject(subject_id):
    try:
        current_user_id = get_jwt_identity()
        subject = Subject.query.filter_by(
            id=subject_id, 
            user_id=current_user_id
        ).first()
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            # Check if new name conflicts with existing subject
            if data['name'] != subject.name:
                existing_subject = Subject.query.filter_by(
                    user_id=current_user_id, 
                    name=data['name']
                ).first()
                
                if existing_subject:
                    return jsonify({'error': 'Subject with this name already exists'}), 409
            
            subject.name = data['name']
        
        if 'color' in data:
            subject.color = data['color']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Subject updated successfully',
            'subject': subject.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@subjects_bp.route('/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    try:
        current_user_id = get_jwt_identity()
        subject = Subject.query.filter_by(
            id=subject_id, 
            user_id=current_user_id
        ).first()
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@subjects_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_subject_stats():
    try:
        current_user_id = get_jwt_identity()
        subjects = Subject.query.filter_by(user_id=current_user_id).all()
        
        stats = []
        for subject in subjects:
            total_time = sum(session.time_spent for session in subject.study_sessions)
            avg_focus = 0
            if subject.study_sessions:
                avg_focus = sum(session.focus_level or 0 for session in subject.study_sessions) / len(subject.study_sessions)
            
            stats.append({
                'id': subject.id,
                'name': subject.name,
                'color': subject.color,
                'total_study_time': total_time,
                'session_count': len(subject.study_sessions),
                'average_focus_level': round(avg_focus, 1),
                'last_studied': max([session.timestamp for session in subject.study_sessions]).isoformat() if subject.study_sessions else None
            })
        
        # Sort by total study time
        stats.sort(key=lambda x: x['total_study_time'], reverse=True)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
