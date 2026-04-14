const API_URL = 'http://localhost:8000/api';
let authToken = null;

// Modal functions
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function showSignupModal() {
    document.getElementById('signupModal').style.display = 'flex';
}

function closeSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
}

function switchToSignup() {
    closeLoginModal();
    showSignupModal();
}

function switchToLogin() {
    closeSignupModal();
    showLoginModal();
}

// Handle login
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('token', authToken);
            localStorage.setItem('username', username);
            window.location.href = 'dashboard.html';
        } else {
            alert('Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Network error. Please try again.');
    }
});

// Handle signup
document.getElementById('signupForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fullName = document.getElementById('signupFullName').value;
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullName, username, email, password })
        });
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            closeSignupModal();
            showLoginModal();
        } else {
            const error = await response.json();
            alert(error.detail || 'Registration failed.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('Network error. Please try again.');
    }
});

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        authToken = token;
        return true;
    }
    return false;
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// Scroll to features
function scrollToFeatures() {
    document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}