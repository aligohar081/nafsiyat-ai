// API Configuration - Use global config or fallback to localhost
const API_URL = window.API_URL || 'http://localhost:8000/api';

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
            document.getElementById('userNameDisplay').textContent = user.full_name || user.username;
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
        
        // Load completed sessions count
        const completedResponse = await fetch(`${API_URL}/appointments?status=completed`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (completedResponse.ok) {
            const completed = await completedResponse.json();
            document.getElementById('completedCount').textContent = completed.length;
        }
        
        // Load community posts count
        const postsResponse = await fetch(`${API_URL}/community/posts`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (postsResponse.ok) {
            const posts = await postsResponse.json();
            document.getElementById('postCount').textContent = posts.length;
        }
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Mood tracking
document.querySelectorAll('.mood-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
        const selectedMood = btn.dataset.mood;
        
        // Remove selected class from all
        document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        
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
            
            // Show success notification
            showNotification('Mood recorded! Thanks for sharing. 💙', 'success');
            
        } catch (error) {
            console.error('Error saving mood:', error);
        }
    });
});

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#2ECC71' : '#1B2B4E'};
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);