import React from 'react';

const AdminDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Manage the StudySphere application</p>
      </div>
      
      <div className="card">
        <p className="text-gray-600">Admin dashboard component will be implemented here.</p>
        <p className="text-sm text-gray-500 mt-2">Features: Monitor user activity, manage subject categories, and view system analytics.</p>
      </div>
    </div>
  );
};

export default AdminDashboard; 