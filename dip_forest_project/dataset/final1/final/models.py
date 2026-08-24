from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student')
    academic_goal = db.Column(db.String(256))
    focus_areas = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subjects = db.relationship('Subject', backref='user', lazy=True, cascade='all, delete-orphan')
    audio_notes = db.relationship('AudioNote', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'academic_goal': self.academic_goal,
            'focus_areas': self.focus_areas,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color for UI
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    study_sessions = db.relationship('StudySession', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_study_time': sum(session.time_spent for session in self.study_sessions)
        }

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    time_spent = db.Column(db.Float, nullable=False)  # Hours
    topic = db.Column(db.String(128))
    focus_level = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'time_spent': self.time_spent,
            'topic': self.topic,
            'focus_level': self.focus_level,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AudioNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    audio_url = db.Column(db.String(256))
    transcript = db.Column(db.Text)
    duration = db.Column(db.Float)  # Duration in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'audio_url': self.audio_url,
            'transcript': self.transcript,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
