// API Configuration - Use global config or fallback to localhost
const API_URL = window.API_URL || 'http://localhost:8000/api';
let currentSessionId = null;
let allSessions = [];

// Get auth token
function getAuthToken() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
    }
    return token;
}

// Toggle history sidebar
function toggleHistorySidebar() {
    const sidebar = document.getElementById('historySidebar');
    const overlay = document.getElementById('historyOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
}

function closeHistorySidebar() {
    const sidebar = document.getElementById('historySidebar');
    const overlay = document.getElementById('historyOverlay');
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
}

// Load current session
async function loadCurrentSession() {
    try {
        const response = await fetch(`${API_URL}/chat/current-session`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.session_id) {
                currentSessionId = data.session_id;
            }
        }
    } catch (error) {
        console.error('Error loading current session:', error);
    }
}

// Load chat history (all sessions)
async function loadChatHistory() {
    try {
        const response = await fetch(`${API_URL}/chat/history`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            allSessions = data.sessions || [];
            
            updateHistorySidebar();
            
            if (data.messages && data.messages.length > 0) {
                currentSessionId = data.session_id;
                displayMessages(data.messages);
            } else if (data.session_id) {
                currentSessionId = data.session_id;
                showWelcomeMessage();
            } else {
                await createNewSession();
            }
        }
    } catch (error) {
        console.error('Error loading history:', error);
        await createNewSession();
    }
}

// Update history sidebar
function updateHistorySidebar() {
    const container = document.getElementById('historyList');
    
    if (!allSessions || allSessions.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #6c6c7a;">
                <i class="fas fa-comments" style="font-size: 2rem; margin-bottom: 0.5rem; display: block;"></i>
                No chat history yet<br>Start a new conversation!
            </div>
        `;
        return;
    }
    
    container.innerHTML = allSessions.map(session => `
        <div class="history-item ${currentSessionId === session.id ? 'active' : ''}" onclick="loadSession(${session.id})">
            <div class="history-item-header">
                <div class="history-title">${escapeHtml(session.title || 'Chat Session')}</div>
                <button class="delete-history-btn" onclick="event.stopPropagation(); deleteSession(${session.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="history-preview">${escapeHtml(session.preview || 'No messages')}</div>
            <div class="history-date">${formatDate(session.started_at)}</div>
        </div>
    `).join('');
}

// Load a specific session
async function loadSession(sessionId) {
    closeHistorySidebar();
    
    try {
        const response = await fetch(`${API_URL}/chat/session/${sessionId}`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentSessionId = sessionId;
            displayMessages(data.messages || []);
            updateHistorySidebar();
        } else {
            showNotification('Error loading session', 'error');
        }
    } catch (error) {
        console.error('Error loading session:', error);
        showNotification('Error loading chat history', 'error');
    }
}

// Delete a session
async function deleteSession(sessionId) {
    if (confirm('Are you sure you want to delete this chat history? This cannot be undone.')) {
        try {
            const response = await fetch(`${API_URL}/chat/session/${sessionId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${getAuthToken()}` }
            });
            
            if (response.ok) {
                showNotification('Chat session deleted!', 'success');
                
                if (currentSessionId === sessionId) {
                    await createNewSession();
                }
                
                await loadChatHistory();
            } else {
                showNotification('Error deleting session', 'error');
            }
        } catch (error) {
            console.error('Error deleting session:', error);
            showNotification('Error deleting session', 'error');
        }
    }
}

// Display messages in chat
function displayMessages(messages) {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = '';
    
    if (!messages || messages.length === 0) {
        showWelcomeMessage();
        return;
    }
    
    messages.forEach(msg => {
        addMessageToChat(msg.role, msg.content, msg.timestamp);
    });
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show welcome message
function showWelcomeMessage() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = `
        <div class="message assistant">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>✨ <strong>Assalam-o-Alaikum!</strong> ✨<br><br>I'm Nafsiyat AI, your mental wellness companion. How are you feeling today? Remember, I'm here to listen and support you. 💙</p>
                <span class="message-time">Just now</span>
            </div>
        </div>
    `;
}

// Create a new session
async function createNewSession() {
    try {
        const response = await fetch(`${API_URL}/chat/new-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentSessionId = data.session_id;
            console.log('New session created:', currentSessionId);
            return true;
        } else {
            console.error('Failed to create new session');
            return false;
        }
    } catch (error) {
        console.error('Error creating new session:', error);
        return false;
    }
}

// Send message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    if (!currentSessionId) {
        const created = await createNewSession();
        if (!created) {
            showNotification('Error creating session', 'error');
            return;
        }
    }
    
    addMessageToChat('user', message);
    input.value = '';
    input.style.height = 'auto';
    
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/chat/send-with-session?session_id=${currentSessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({ content: message })
        });
        
        if (response.ok) {
            const data = await response.json();
            removeTypingIndicator();
            
            setTimeout(() => {
                addMessageToChat('assistant', data.response);
                
                if (data.risk_detected) {
                    showCrisisAlert();
                }
                
                if (data.session_id) {
                    currentSessionId = data.session_id;
                }
                
                refreshChatHistory();
            }, 500);
            
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            removeTypingIndicator();
            addMessageToChat('assistant', "I'm having trouble responding right now. Please try again in a moment. 🙏");
        }
    } catch (error) {
        console.error('Network error:', error);
        removeTypingIndicator();
        addMessageToChat('assistant', "Network error. Please check your connection and try again. 💙");
    }
}

// Refresh chat history
async function refreshChatHistory() {
    try {
        const response = await fetch(`${API_URL}/chat/history`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            allSessions = data.sessions || [];
            updateHistorySidebar();
        }
    } catch (error) {
        console.error('Error refreshing history:', error);
    }
}

// Start new chat
async function startNewChat() {
    if (confirm('Start a new conversation? Your current chat will be saved in history.')) {
        const created = await createNewSession();
        
        if (created) {
            showWelcomeMessage();
            showNotification('New conversation started! 💙', 'success');
            await loadChatHistory();
        } else {
            showNotification('Error starting new conversation', 'error');
        }
    }
}

// Add message to chat
function addMessageToChat(role, content, timestamp = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    
    if (timestamp) {
        const date = new Date(timestamp);
        timeSpan.textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
        timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    contentDiv.appendChild(timeSpan);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatMessage(content) {
    let formatted = content.replace(/\n/g, '<br>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    return formatted;
}

// Typing indicator
function showTypingIndicator() {
    removeTypingIndicator();
    
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div><div style="font-size: 0.7rem; color: #6c6c7a; margin-top: 4px;">Nafsiyat AI is thinking...</div>';
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(contentDiv);
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function sendQuickMessage(message) {
    document.getElementById('messageInput').value = message;
    sendMessage();
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Auto-resize textarea
document.getElementById('messageInput')?.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 100) + 'px';
});

function showCrisisAlert() {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'crisis-alert';
    alertDiv.innerHTML = `
        <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-left: 4px solid #e74c3c; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
            <p style="color: #c0392b; font-weight: bold; margin-bottom: 0.5rem;">
                <i class="fas fa-exclamation-triangle"></i> Need Immediate Support?
            </p>
            <p style="margin-bottom: 0.5rem;">You're not alone. Help is available 24/7:</p>
            <p style="margin-bottom: 0.25rem;">📞 Rozan Helpline: 0311-778-6264</p>
            <p>💙 You matter. Please reach out for support.</p>
        </div>
    `;
    document.getElementById('chatMessages').appendChild(alertDiv);
    document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i><span>${message}</span>`;
    notification.style.cssText = `
        position: fixed; bottom: 20px; right: 20px;
        background: ${type === 'success' ? '#2ECC71' : '#1B2B4E'};
        color: white; padding: 10px 18px; border-radius: 10px;
        z-index: 10000; animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-size: 0.85rem;
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadUserName() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        if (response.ok) {
            const user = await response.json();
            document.getElementById('userNameDisplay').textContent = user.full_name || user.username;
        }
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadUserName();
    await loadCurrentSession();
    await loadChatHistory();
});