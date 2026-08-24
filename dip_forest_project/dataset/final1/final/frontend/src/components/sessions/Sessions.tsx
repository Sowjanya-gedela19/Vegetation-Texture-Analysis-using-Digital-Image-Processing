import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Plus, Clock, Target, Trash2, X, Loader2 } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';

// --- Define the necessary Types ---
interface Subject {
  id: number;
  name: string;
  color: string;
}

interface Session {
  id: number;
  subject_id: number;
  time_spent: number;
  topic: string;
  focus_level: number;
  notes: string;
  timestamp: string;
  subject: Subject;
}

// --- Main Sessions Component ---
const Sessions: React.FC = () => {
  // Get the shared subjects list from the context
  const { user, subjects } = useAuth(); 
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const fetchSessions = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.get('/api/sessions/');
      setSessions(response.data);
    } catch (error) {
      toast.error('Failed to fetch sessions.');
      console.error("Fetch sessions error:", error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    // Fetch sessions when the component loads
    fetchSessions();
  }, [fetchSessions]);

  const handleSessionCreated = (newSession: Session) => {
    // Add the new session to the top of the list for immediate feedback
    setSessions(prevSessions => [newSession, ...prevSessions]);
  };

  const handleDeleteSession = async (sessionId: number) => {
    if (!window.confirm('Are you sure you want to delete this session?')) return;

    try {
        await axios.delete(`/api/sessions/${sessionId}`);
        toast.success('Session deleted successfully!');
        setSessions(prevSessions => prevSessions.filter(s => s.id !== sessionId));
    } catch (error) {
        toast.error('Failed to delete session.');
    }
  };

  if (loading) {
    return <div className="p-6 flex justify-center items-center"><LoadingSpinner size="lg" /></div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Study Sessions</h1>
          <p className="text-gray-600 mt-1">Log your study time and keep track of your progress.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)} 
          className="btn-primary mt-4 md:mt-0 flex items-center justify-center"
          disabled={subjects.length === 0}
        >
          <Plus className="w-5 h-5 mr-2" />
          Log New Session
        </button>
      </div>
      
      {subjects.length === 0 && !loading && (
        <div className="card text-center py-8">
            <p className="text-gray-600">You need to add a subject on the 'Subjects' page before you can log a session.</p>
        </div>
      )}

      {sessions.length > 0 ? (
        <div className="space-y-4">
          {sessions.map(session => (
            <SessionCard 
              key={session.id} 
              session={session}
              onDelete={() => handleDeleteSession(session.id)}
            />
          ))}
        </div>
      ) : (
        !loading && subjects.length > 0 && (
            <div className="text-center py-16 card">
                <Clock className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-xl font-semibold text-gray-900">No sessions logged</h3>
                <p className="mt-1 text-gray-500">Click "Log New Session" to get started.</p>
            </div>
        )
      )}

      {isModalOpen && (
        <SessionModal 
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSessionCreated={handleSessionCreated}
          subjects={subjects}
        />
      )}
    </div>
  );
};

// --- Session Card Component ---
const SessionCard: React.FC<{ session: Session; onDelete: () => void; }> = ({ session, onDelete }) => {
  return (
    <div className="card p-4 transition-shadow hover:shadow-lg">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
            <div className="w-2 h-10 rounded-full" style={{backgroundColor: session.subject?.color || '#3B82F6'}}></div>
            <div>
                <h3 className="text-lg font-bold text-gray-800">{session.subject?.name || 'unknown subject'}</h3>
                <p className="text-sm text-gray-600">{session.topic || 'General Study'}</p>
            </div>
        </div>
        <div className="text-right">
            <p className="text-lg font-bold text-gray-800">{session.time_spent} min</p>
            <p className="text-xs text-gray-500">{new Date(session.timestamp).toLocaleDateString()}</p>
        </div>
      </div>
      {session.notes && <p className="mt-3 text-sm text-gray-700 bg-gray-50 p-3 rounded-md">{session.notes}</p>}
      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Target className="w-4 h-4" />
            <span>Focus: {session.focus_level}/10</span>
        </div>
        <button onClick={onDelete} className="p-2 rounded-full hover:bg-red-100 text-gray-500 hover:text-red-500">
            <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

// --- Session Modal Component ---
const SessionModal: React.FC<{ 
    isOpen: boolean; 
    onClose: () => void; 
    onSessionCreated: (session: Session) => void;
    subjects: Subject[];
}> = ({ isOpen, onClose, onSessionCreated, subjects }) => {
  const [subjectId, setSubjectId] = useState<string>('');
  const [timeSpent, setTimeSpent] = useState('');
  const [topic, setTopic] = useState('');
  const [focusLevel, setFocusLevel] = useState(5);
  const [notes, setNotes] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (isOpen && subjects.length > 0 && !subjectId) {
        setSubjectId(subjects[0].id.toString());
    }
  }, [isOpen, subjects, subjectId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectId || !timeSpent) {
        toast.error("Please select a subject and enter the time spent.");
        return;
    }
    
    setIsSaving(true);
    try {
        const response = await axios.post('/api/sessions/', {
            subject_id: parseInt(subjectId),
            time_spent: parseFloat(timeSpent),
            topic,
            focus_level: focusLevel,
            notes
        });
        toast.success('Session logged successfully!');
        onSessionCreated(response.data.session);
        onClose();
    } catch (error: any) {
        toast.error(error.response?.data?.error || 'Failed to log session.');
    } finally {
        setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-lg m-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Log a New Study Session</h2>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-100">
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="subject-id" className="form-label">Subject</label>
              <select
                id="subject-id"
                value={subjectId}
                onChange={(e) => setSubjectId(e.target.value)}
                className="input-field"
              >
                {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="time-spent" className="form-label">Time Spent (minutes)</label>
              <input
                id="time-spent"
                type="number"
                value={timeSpent}
                onChange={(e) => setTimeSpent(e.target.value)}
                className="input-field"
                placeholder="e.g., 45"
                required
              />
            </div>
          </div>
          <div>
            <label htmlFor="topic" className="form-label">Topic Studied (Optional)</label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="input-field"
              placeholder="e.g., Chapter 3: Integrals"
            />
          </div>
           <div>
              <label htmlFor="focus-level" className="form-label">Focus Level: {focusLevel}/10</label>
              <input
                id="focus-level"
                type="range"
                min="1"
                max="10"
                value={focusLevel}
                onChange={(e) => setFocusLevel(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          <div>
            <label htmlFor="notes" className="form-label">Notes (Optional)</label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="input-field min-h-[100px]"
              placeholder="Any thoughts or key takeaways..."
            />
          </div>
          <div className="mt-6 flex justify-end space-x-4">
            <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
            <button type="submit" className="btn-primary w-32" disabled={isSaving}>
              {isSaving ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Log Session'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Sessions;
