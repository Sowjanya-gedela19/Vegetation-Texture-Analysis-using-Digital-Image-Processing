import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, Target } from 'lucide-react';

// 👇 Use proxy instead of hardcoded URL
const API_BASE_URL = 'http://localhost:5000';

const SignupPage: React.FC = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [academicGoal, setAcademicGoal] = useState('');
  const [focusAreas, setFocusAreas] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          academic_goal: academicGoal,
          focus_areas: focusAreas,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Signup failed');
      }

      // Store token (optional)
      localStorage.setItem('token', data.token);

      // Navigate to dashboard or login
      navigate('/login');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form
        onSubmit={handleSignup}
        className="bg-white p-6 rounded-lg shadow-md w-full max-w-md space-y-4"
      >
        <h2 className="text-2xl font-bold text-center">Create Account</h2>

        {error && <p className="text-red-500 text-sm text-center">{error}</p>}

        <div>
          <label className="block text-sm font-medium">Email</label>
          <div className="flex items-center border rounded px-2">
            <Mail className="w-4 h-4 mr-2 text-gray-500" />
            <input
              type="email"
              className="w-full p-2 outline-none"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium">Password</label>
          <div className="flex items-center border rounded px-2">
            <Lock className="w-4 h-4 mr-2 text-gray-500" />
            <input
              type={showPassword ? 'text' : 'password'}
              className="w-full p-2 outline-none"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="ml-2 focus:outline-none"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium">Academic Goal</label>
          <div className="flex items-center border rounded px-2">
            <Target className="w-4 h-4 mr-2 text-gray-500" />
            <input
              type="text"
              className="w-full p-2 outline-none"
              placeholder="e.g., Get straight A's this semester"
              value={academicGoal}
              onChange={(e) => setAcademicGoal(e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium">Focus Areas</label>
          <div className="flex items-center border rounded px-2">
            <User className="w-4 h-4 mr-2 text-gray-500" />
            <input
              type="text"
              className="w-full p-2 outline-none"
              placeholder="e.g., Math, Science, Literature"
              value={focusAreas}
              onChange={(e) => setFocusAreas(e.target.value)}
            />
          </div>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>

        <div className="text-center mt-4">
          <p className="text-gray-600">
            Already have an account?{' '}
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Back to Login
            </button>
          </p>
        </div>
      </form>
    </div>
  );
};

export default SignupPage;
