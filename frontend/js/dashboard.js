const API_URL = 'http://localhost:8000/api';

function getAuthToken() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
    }
    return token;
}

// Load user data
async function loadDashboard() {
    try {
        // Get user info
        const userResponse = await fetch(`${API_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (userResponse.ok) {
            const user = await userResponse.json();
            document.getElementById('userName').textContent = user.full_name || user.username;
        }
        
        // Load chat count
        const chatResponse = await fetch(`${API_URL}/chat/history`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (chatResponse.ok) {
            const chatData = await chatResponse.json();
            const messageCount = chatData.messages?.filter(m => m.role === 'user').length || 0;
            document.getElementById('chatCount').textContent = messageCount;
        }
        
        // Load appointments
        const appointmentResponse = await fetch(`${API_URL}/appointments`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (appointmentResponse.ok) {
            const appointments = await appointmentResponse.json();
            document.getElementById('appointmentCount').textContent = appointments.length;
        }
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Mood tracking
document.querySelectorAll('.mood').forEach(mood => {
    mood.addEventListener('click', async (e) => {
        const selectedMood = e.target.dataset.mood;
        
        // Send mood to chatbot
        try {
            await fetch(`${API_URL}/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getAuthToken()}`
                },
                body: JSON.stringify({ content: `I'm feeling ${selectedMood} today` })
            });
            
            // Show success message
            const moodChecker = document.querySelector('.mood-checker');
            const originalText = moodChecker.innerHTML;
            moodChecker.innerHTML = '<span>✅ Mood recorded!</span>';
            setTimeout(() => {
                moodChecker.innerHTML = originalText;
            }, 2000);
            
        } catch (error) {
            console.error('Error saving mood:', error);
        }
    });
});

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);