from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import AudioNote, db
from datetime import datetime
import os
import uuid

audio_bp = Blueprint('audio', __name__)

# Configure upload folder
UPLOAD_FOLDER = 'audio_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@audio_bp.route('/', methods=['GET'])
@jwt_required()
def get_audio_notes():
    try:
        current_user_id = get_jwt_identity()['id']
        
        # Get query parameters
        limit = request.args.get('limit', type=int, default=20)
        offset = request.args.get('offset', type=int, default=0)
        
        # Get audio notes for user
        audio_notes = AudioNote.query.filter_by(user_id=current_user_id)\
            .order_by(AudioNote.timestamp.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return jsonify([note.to_dict() for note in audio_notes]), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@audio_bp.route('/', methods=['POST'])
@jwt_required()
def create_audio_note():
    try:
        current_user_id = get_jwt_identity()['id']
        
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'wav', 'mp3', 'm4a', 'ogg'}
        file_extension = audio_file.filename.rsplit('.', 1)[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Allowed: wav, mp3, m4a, ogg'}), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save audio file
        audio_file.save(filepath)
        
        # Get additional data
        transcript = request.form.get('transcript', '')
        duration = request.form.get('duration', type=float)
        
        # Create audio note
        audio_note = AudioNote(
            user_id=current_user_id,
            audio_url=f"/audio_uploads/{filename}",
            transcript=transcript,
            duration=duration
        )
        
        db.session.add(audio_note)
        db.session.commit()
        
        return jsonify({
            'message': 'Audio note created successfully',
            'audio_note': audio_note.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@audio_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
def get_audio_note(note_id):
    try:
        current_user_id = get_jwt_identity()['id']
        
        audio_note = AudioNote.query.filter_by(
            id=note_id, 
            user_id=current_user_id
        ).first()
        
        if not audio_note:
            return jsonify({'error': 'Audio note not found'}), 404
        
        return jsonify(audio_note.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@audio_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_audio_note(note_id):
    try:
        current_user_id = get_jwt_identity()['id']
        
        audio_note = AudioNote.query.filter_by(
            id=note_id, 
            user_id=current_user_id
        ).first()
        
        if not audio_note:
            return jsonify({'error': 'Audio note not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update transcript
        if 'transcript' in data:
            audio_note.transcript = data['transcript']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Audio note updated successfully',
            'audio_note': audio_note.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@audio_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_audio_note(note_id):
    try:
        current_user_id = get_jwt_identity()['id']
        
        audio_note = AudioNote.query.filter_by(
            id=note_id, 
            user_id=current_user_id
        ).first()
        
        if not audio_note:
            return jsonify({'error': 'Audio note not found'}), 404
        
        # Delete audio file if it exists
        if audio_note.audio_url:
            filepath = os.path.join(os.getcwd(), audio_note.audio_url.lstrip('/'))
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(audio_note)
        db.session.commit()
        
        return jsonify({'message': 'Audio note deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@audio_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_audio_notes():
    try:
        current_user_id = get_jwt_identity()['id']
        
        # Get recent audio notes (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_notes = AudioNote.query.filter(
            AudioNote.user_id == current_user_id,
            AudioNote.timestamp >= week_ago
        ).order_by(AudioNote.timestamp.desc()).limit(10).all()
        
        return jsonify([note.to_dict() for note in recent_notes]), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@audio_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_audio_stats():
    try:
        current_user_id = get_jwt_identity()['id']
        
        # Get all audio notes for user
        audio_notes = AudioNote.query.filter_by(user_id=current_user_id).all()
        
        total_notes = len(audio_notes)
        total_duration = sum(note.duration or 0 for note in audio_notes)
        avg_duration = total_duration / total_notes if total_notes > 0 else 0
        
        # Notes by day of week
        from datetime import datetime
        day_counts = {}
        for note in audio_notes:
            day = note.timestamp.strftime('%A')
            day_counts[day] = day_counts.get(day, 0) + 1
        
        stats = {
            'total_notes': total_notes,
            'total_duration_minutes': round(total_duration / 60, 2),
            'average_duration_seconds': round(avg_duration, 2),
            'notes_by_day': day_counts
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# Serve audio files
@audio_bp.route('/uploads/<filename>')
@jwt_required()
def serve_audio(filename):
    try:
        current_user_id = get_jwt_identity()['id']
        
        # Verify user owns this audio file
        audio_note = AudioNote.query.filter_by(
            audio_url=f"/audio_uploads/{filename}",
            user_id=current_user_id
        ).first()
        
        if not audio_note:
            return jsonify({'error': 'Audio file not found'}), 404
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Audio file not found'}), 404
        
        from flask import send_file
        return send_file(filepath, mimetype='audio/mpeg')
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
