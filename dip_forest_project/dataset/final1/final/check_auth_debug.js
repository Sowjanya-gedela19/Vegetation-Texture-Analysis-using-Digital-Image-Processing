// Debug authentication state
console.log('=== Authentication Debug ===');

// Check localStorage
const storedUser = localStorage.getItem('studySphereUser');
console.log('Stored user exists:', !!storedUser);

if (storedUser) {
  try {
    const user = JSON.parse(storedUser);
    console.log('User data:', {
      id: user.id,
      email: user.email,
      role: user.role,
      hasToken: !!user.token,
      tokenLength: user.token ? user.token.length : 0,
      tokenStart: user.token ? user.token.substring(0, 20) + '...' : 'No token'
    });
  } catch (e) {
    console.log('Error parsing user:', e);
  }
} else {
  console.log('No user found in localStorage');
}

// Check axios defaults
console.log('Axios Authorization header:', axios.defaults.headers.common['Authorization'] ? 'Set' : 'Not set');

// Test API call
if (storedUser) {
  try {
    const user = JSON.parse(storedUser);
    console.log('Testing API call...');
    
    fetch('/api/sessions/analytics?days=7', {
      headers: {
        'Authorization': `Bearer ${user.token}`
      }
    })
    .then(res => {
      console.log('API Response Status:', res.status);
      return res.json();
    })
    .then(data => {
      console.log('API Response Data:', data);
    })
    .catch(err => {
      console.log('API Error:', err);
    });
  } catch (e) {
    console.log('Error testing API:', e);
  }
}

console.log('=== End Debug ==='); 