import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Clock, 
  // TrendingUp, // Removed unused import
  BookOpen, 
  Target, 
  Zap, 
  Calendar,
  // BarChart3, // Removed unused import
  Lightbulb,
  // Trophy, // Removed unused import
  Activity,
  AlertTriangle, // For attention areas
  Sparkles,      // For motivation
} from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';

// --- 1. Updated Interfaces to match Backend Data ---

interface DashboardStats {
  totalStudyTime: number;
  sessionsThisWeek: number;
  averageFocusLevel: number;
  subjectsCount: number;
}

// This interface is now more flexible to handle different types of AI insights
interface AIInsight {
  type: 'suggestion' | 'attention' | 'motivation';
  title: string;
  content: string[]; // Can be a list of suggestions or attention areas
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]); // To hold recent sessions
  const [loading, setLoading] = useState(true);

  // --- 2. Corrected Data Fetching Logic ---

  useEffect(() => {
    console.log('Dashboard useEffect - user:', user);
    console.log('Dashboard useEffect - user has token:', user && 'token' in user);
    
    // This check confirms the user object exists and has a 'token' property before using it.
    if (user && 'token' in user) {
      console.log('Dashboard - calling fetchDashboardData with token');
      // We cast user to 'any' here to tell TypeScript we know the token exists.
      fetchDashboardData((user as any).token);
    } else {
      console.log('Dashboard - no user or token, stopping loading');
      // If there's no user or token, we stop loading.
      setLoading(false);
    }
  }, [user]);

  const fetchDashboardData = async (token: string) => {
    console.log('fetchDashboardData called with token:', token ? token.substring(0, 20) + '...' : 'No token');
    setLoading(true);
    
    // Use the global axios instance that's already configured with auth headers
    console.log('Using global axios with auth header:', axios.defaults.headers.common['Authorization']);

    try {
      // Test each endpoint individually to see which one fails
      console.log('Testing analytics endpoint...');
      const analyticsRes = await axios.get('/api/sessions/analytics?days=7');
      console.log('Analytics response status:', analyticsRes.status);
      
      console.log('Testing AI suggestions endpoint...');
      const aiRes = await axios.get('/api/ai/suggestions');
      console.log('AI suggestions response status:', aiRes.status);
      
      console.log('Testing sessions endpoint...');
      // Use explicit trailing slash to match what the browser is sending
      const recentSessionsRes = await axios.get('/api/sessions/?limit=3');
      console.log('Sessions response status:', recentSessionsRes.status);

      // --- Process Analytics Data ---
      const analyticsData = analyticsRes.data;
      setStats({
        totalStudyTime: analyticsData.summary?.total_time || 0,
        sessionsThisWeek: analyticsData.summary?.total_sessions || 0,
        averageFocusLevel: analyticsData.summary?.average_focus_level || 0,
        subjectsCount: Object.keys(analyticsData.subject_breakdown || {}).length
      });

      // --- Process AI Insights Data ---
      const aiData = aiRes.data;
      const insights: AIInsight[] = [];
      if (aiData.suggestions?.length > 0) {
        insights.push({ type: 'suggestion', title: 'Actionable Suggestions', content: aiData.suggestions });
      }
      if (aiData.attention_areas?.length > 0) {
        insights.push({ type: 'attention', title: 'Areas for Attention', content: aiData.attention_areas });
      }
      if (aiData.motivation) {
        insights.push({ type: 'motivation', title: 'Your Daily Motivation', content: [aiData.motivation] });
      }
      setAiInsights(insights);

      // --- Process Recent Activity ---
      setRecentActivity(recentSessionsRes.data);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Could not load your dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // --- 3. Dynamic Icon Component ---
  const getIconComponent = (iconName: AIInsight['type']) => {
    const icons: { [key: string]: React.ReactNode } = {
      suggestion: <Lightbulb className="w-6 h-6 text-white" />,
      attention: <AlertTriangle className="w-6 h-6 text-white" />,
      motivation: <Sparkles className="w-6 h-6 text-white" />,
    };
    return icons[iconName] || <Zap className="w-6 h-6 text-white" />;
  };

  const getIconBgColor = (iconName: AIInsight['type']) => {
    const colors: { [key: string]: string } = {
        suggestion: 'from-blue-500 to-indigo-600',
        attention: 'from-amber-500 to-orange-600',
        motivation: 'from-green-500 to-emerald-600',
    };
    return colors[iconName] || 'from-gray-500 to-gray-600';
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-10">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
        {/* Welcome Header */}
        <div>
          <h1 className="text-3xl md:text-4xl font-bold gradient-text">
            Welcome back, {user?.email?.split('@')[0]}! 👋
          </h1>
          <p className="text-lg text-gray-600 mt-1">
            Ready to continue your learning journey? Here's your progress overview.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="stats-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Study Time</p>
                <p className="text-3xl font-bold gradient-text">
                  {stats?.totalStudyTime ? `${stats.totalStudyTime.toFixed(1)}h` : '0h'}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <Clock className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
          <div className="stats-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sessions This Week</p>
                <p className="text-3xl font-bold gradient-text">
                  {stats?.sessionsThisWeek || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <Calendar className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
          <div className="stats-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Average Focus</p>
                <p className="text-3xl font-bold gradient-text">
                  {stats?.averageFocusLevel ? `${stats.averageFocusLevel.toFixed(1)}/10` : 'N/A'}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                <Target className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
          <div className="stats-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Subjects</p>
                <p className="text-3xl font-bold gradient-text">
                  {stats?.subjectsCount || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-8">
            {/* Quick Actions */}
            <div className="card">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-blue-600" />
                Quick Actions
              </h2>
              <div className="space-y-3">
                <button className="w-full btn-primary">Start Study Session</button>
                <button className="w-full btn-secondary">View Analytics</button>
                <button className="w-full btn-secondary">Set Goals</button>
              </div>
            </div>
            {/* Recent Activity */}
            <div className="card">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-blue-600" />
                Recent Activity
              </h2>
              <div className="space-y-3">
                {recentActivity.length > 0 ? recentActivity.map((session) => (
                  <div key={session.id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-gray-800">{session.subject?.name || 'Unknown Subject'}</p>
                      <p className="text-sm text-gray-600">{session.topic || 'General Study'}</p>
                    </div>
                    <span className="text-sm text-gray-500">{new Date(session.timestamp).toLocaleDateString()}</span>
                  </div>
                )) : (
                  <p className="text-center text-gray-500 py-4">No recent activity. Start a study session!</p>
                )}
              </div>
            </div>
          </div>

          {/* AI Insights */}
          <div className="lg:col-span-2 card">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-blue-600" />
              AI Insights & Recommendations
            </h2>
            <div className="space-y-4">
              {aiInsights.length > 0 ? aiInsights.map((insight, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className={`w-10 h-10 bg-gradient-to-r ${getIconBgColor(insight.type)} rounded-lg flex items-center justify-center flex-shrink-0 shadow-md`}>
                    {getIconComponent(insight.type)}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800">{insight.title}</h3>
                    <ul className="list-disc list-inside text-gray-600 mt-1">
                        {insight.content.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                </div>
              )) : (
                <p className="text-center text-gray-500 py-8">No AI insights available yet. Complete a few study sessions to get started.</p>
              )}
            </div>
          </div>
        </div>
    </div>
  );
};

export default Dashboard;
