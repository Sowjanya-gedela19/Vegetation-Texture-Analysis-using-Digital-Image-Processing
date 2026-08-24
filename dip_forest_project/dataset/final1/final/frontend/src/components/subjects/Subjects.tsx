import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Plus, Edit, Trash2, BookOpen, X, Loader2, AlertTriangle } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';

// --- Define the Subject Type ---
interface Subject {
  id: number;
  name: string;
  color: string;
  user_id: number;
}

// Predefined colors for the color picker in the modal
const SUBJECT_COLORS = [
  '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
  '#06B6D4', '#F97316', '#84CC16', '#EC4899', '#6366F1'
];

// --- Main Subjects Component ---
const Subjects: React.FC = () => {
  // Get shared state and functions from AuthContext
  const { subjects, fetchSubjects } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null);
  const [deletingSubject, setDeletingSubject] = useState<Subject | null>(null);
  
  const [name, setName] = useState('');
  const [color, setColor] = useState(SUBJECT_COLORS[0]);
  const [isSaving, setIsSaving] = useState(false);

  // Use a separate loading state for the initial fetch
  useEffect(() => {
    setLoading(true);
    fetchSubjects().finally(() => setLoading(false));
  }, [fetchSubjects]);

  const handleOpenModal = (subject: Subject | null = null) => {
    if (subject) {
      setEditingSubject(subject);
      setName(subject.name);
      setColor(subject.color);
    } else {
      setEditingSubject(null);
      setName('');
      setColor(SUBJECT_COLORS[0]);
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error("Subject name cannot be empty.");
      return;
    }
    setIsSaving(true);
    
    const subjectData = { name, color };
    try {
      if (editingSubject) {
        await axios.put(`/api/subjects/${editingSubject.id}`, subjectData);
        toast.success('Subject updated!');
      } else {
        await axios.post('/api/subjects/', subjectData);
        toast.success('Subject created!');
      }
      await fetchSubjects(); // Refresh the shared list from the server
      handleCloseModal();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to save subject.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = (subject: Subject) => {
    setDeletingSubject(subject);
  };

  const confirmDelete = async () => {
    if (!deletingSubject) return;
    try {
      await axios.delete(`/api/subjects/${deletingSubject.id}`);
      toast.success('Subject deleted.');
      await fetchSubjects(); // Refresh the list
    } catch (error) {
      toast.error('Failed to delete subject.');
    } finally {
      setDeletingSubject(null);
    }
  };

  if (loading) {
    return <div className="p-6 flex justify-center items-center"><LoadingSpinner size="lg" /></div>;
  }

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Subjects</h1>
            <p className="text-gray-600 mt-1">Organize your studies and track your progress.</p>
          </div>
          <button onClick={() => handleOpenModal()} className="btn-primary mt-4 md:mt-0 flex items-center justify-center">
            <Plus className="w-5 h-5 mr-2" />
            Add New Subject
          </button>
        </div>
        
        {subjects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {subjects.map(subject => (
              <div key={subject.id} className="card relative overflow-hidden group">
                <div className="absolute top-0 left-0 h-2 w-full" style={{ backgroundColor: subject.color }}></div>
                <div className="pt-4">
                  <h3 className="text-xl font-bold text-gray-800 truncate">{subject.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">No sessions yet</p>
                </div>
                <div className="absolute top-4 right-4 flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => handleOpenModal(subject)} className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDelete(subject)} className="p-2 rounded-full bg-gray-100 hover:bg-red-100 text-gray-600 hover:text-red-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 card">
            <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-xl font-semibold text-gray-900">No subjects yet</h3>
            <p className="mt-1 text-gray-500">Get started by adding your first study subject.</p>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md m-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">{editingSubject ? 'Edit Subject' : 'Add New Subject'}</h2>
              <button onClick={handleCloseModal} className="p-2 rounded-full hover:bg-gray-100">
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="space-y-6">
                <div>
                  <label htmlFor="subject-name" className="form-label">Subject Name</label>
                  <input
                    id="subject-name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="input-field"
                    placeholder="e.g., Mathematics"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Choose a Color</label>
                  <div className="flex flex-wrap gap-3">
                    {SUBJECT_COLORS.map(c => (
                      <button
                        key={c}
                        type="button"
                        onClick={() => setColor(c)}
                        className={`w-10 h-10 rounded-full transition-transform transform hover:scale-110 ${color === c ? 'ring-2 ring-offset-2 ring-blue-500' : ''}`}
                        style={{ backgroundColor: c }}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-8 flex justify-end space-x-4">
                <button type="button" onClick={handleCloseModal} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary w-32" disabled={isSaving}>
                  {isSaving ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deletingSubject && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
              <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md m-4">
                  <div className="flex items-start">
                      <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                          <AlertTriangle className="h-6 w-6 text-red-600" />
                      </div>
                      <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                          <h3 className="text-lg leading-6 font-medium text-gray-900">Delete Subject</h3>
                          <div className="mt-2">
                              <p className="text-sm text-gray-500">
                                  Are you sure you want to delete the subject "<strong>{deletingSubject.name}</strong>"? This action cannot be undone.
                              </p>
                          </div>
                      </div>
                  </div>
                  <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                      <button
                          type="button"
                          className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 sm:ml-3 sm:w-auto sm:text-sm"
                          onClick={confirmDelete}
                      >
                          Delete
                      </button>
                      <button
                          type="button"
                          className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:w-auto sm:text-sm"
                          onClick={() => setDeletingSubject(null)}
                      >
                          Cancel
                      </button>
                  </div>
              </div>
          </div>
      )}
    </>
  );
};

export default Subjects;
