import React from 'react';

const Profile: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="text-gray-600">Manage your account settings and preferences</p>
      </div>
      
      <div className="card">
        <p className="text-gray-600">Profile management component will be implemented here.</p>
        <p className="text-sm text-gray-500 mt-2">Features: Update profile information, change password, and manage account settings.</p>
      </div>
    </div>
  );
};

export default Profile; 