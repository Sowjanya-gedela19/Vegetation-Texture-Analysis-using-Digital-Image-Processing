import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

// --- Define the shared Types ---
export interface Subject {
  id: number;
  name: string;
  color: string;
  user_id: number;
}

interface User {
  id: number;
  email: string;
  role: 'student' | 'admin';
  token: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  subjects: Subject[];
  setSubjects: React.Dispatch<React.SetStateAction<Subject[]>>;
  fetchSubjects: () => Promise<void>;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  signup: (email: string, password: string, academic_goal?: string, focus_areas?: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState<Subject[]>([]);

  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('studySphereUser');
      if (storedUser) {
        const parsedUser: User = JSON.parse(storedUser);
        setUser(parsedUser);
        axios.defaults.headers.common['Authorization'] = `Bearer ${parsedUser.token}`;
      }
    } catch (error) {
      console.error("Failed to parse user from localStorage", error);
      localStorage.removeItem('studySphereUser');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSubjects = useCallback(async () => {
    if (user?.token) {
      try {
        const response = await axios.get('/api/subjects/');
        setSubjects(response.data);
      } catch (error) {
        console.error("Failed to fetch subjects:", error);
        toast.error("Could not load your subjects.");
      }
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      fetchSubjects();
    } else {
      setSubjects([]);
    }
  }, [user, fetchSubjects]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const res = await axios.post('/api/auth/login', {
        email,
        password,
      });

      const { token, user: userData } = res.data;
      const userWithToken: User = { ...userData, token };

      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUser(userWithToken);
      localStorage.setItem('studySphereUser', JSON.stringify(userWithToken));

      toast.success('Login successful!');
      return true;
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Login failed.');
      return false;
    }
  };

  const signup = async (
    email: string,
    password: string,
    academic_goal?: string,
    focus_areas?: string
  ): Promise<boolean> => {
    try {
      const response = await axios.post('/api/auth/signup', {
        email,
        password,
        academic_goal,
        focus_areas
      });

      const { token, user: userData } = response.data;
      const userWithToken: User = { ...userData, token };

      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUser(userWithToken);
      localStorage.setItem('studySphereUser', JSON.stringify(userWithToken));

      toast.success('Account created successfully!');
      return true;
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Signup failed.');
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('studySphereUser');
    delete axios.defaults.headers.common['Authorization'];
    toast.success('You have been logged out.');
  };

  const value = { user, loading, subjects, setSubjects, fetchSubjects, login, logout, signup };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
