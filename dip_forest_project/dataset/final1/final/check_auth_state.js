// Check authentication state in browser
console.log('=== Authentication State Check ===');

// Check localStorage
const storedUser = localStorage.getItem('studySphereUser');
console.log('Stored user:', storedUser ? 'Found' : 'Not found');

if (storedUser) {
  try {
    const user = JSON.parse(storedUser);
    console.log('User data:', {
      id: user.id,
      email: user.email,
      role: user.role,
      hasToken: !!user.token,
      tokenLength: user.token ? user.token.length : 0
    });
  } catch (e) {
    console.log('Error parsing stored user:', e);
  }
}

// Check axios defaults
console.log('Axios Authorization header:', axios.defaults.headers.common['Authorization'] ? 'Set' : 'Not set');

// Check if user is logged in
console.log('Current user state:', user ? 'Logged in' : 'Not logged in');

console.log('=== End Check ==='); 