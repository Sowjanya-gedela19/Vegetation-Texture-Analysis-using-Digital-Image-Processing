import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const auth = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const success = await auth.login(formData.email, formData.password);
      if (success) {
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error('Login failed:', err.response?.data || err.message);
      alert(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-lg shadow-md w-full max-w-md space-y-4"
      >
        <h2 className="text-2xl font-bold text-center">Login</h2>

        <div>
          <label className="block text-sm font-medium">Email</label>
          <div className="flex items-center border rounded px-2">
            <Mail className="w-4 h-4 mr-2 text-gray-500" />
            <input
              type="email"
              name="email"
              className="w-full p-2 outline-none"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
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
              name="password"
              className="w-full p-2 outline-none"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
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

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <div className="text-center mt-4">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={() => navigate('/signup')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Create Account
            </button>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Login;
