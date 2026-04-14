// ================================================
// KrishiVani - SINGLE JS FILE (Only one file)
// Sab pages ke liye complete JavaScript
// Python 3.10 Project
// ================================================

const API_BASE = '/api';

// Global fetch with JWT auto attach
// KrishiVani - FIXED Main JS (400 Error + Token + FormData)
// KrishiVani - FINAL FIXED JS
// KrishiVani - FINAL FIXED JS (Voice + Token)
// KrishiVani - FINAL FIXED JS (Voice Mic + Token)
const originalFetch = window.fetch;

window.fetch = async (url, options = {}) => {
    if (!options.headers) options.headers = {};
    const token = localStorage.getItem('token');
    if (token) options.headers.Authorization = `Bearer ${token}`;
    if (options.body instanceof FormData) delete options.headers['Content-Type'];
    else if (options.body) options.headers['Content-Type'] = 'application/json';
    return originalFetch(url, options);
};

window.startVoice = function() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'hi-IN';
    recognition.onstart = () => {
        const status = document.getElementById('status');
        if (status) status.textContent = 'Listening... Boliye';
    };
    recognition.onresult = async (event) => {
        const text = event.results[0][0].transcript;
        const status = document.getElementById('status');
        if (status) status.textContent = 'You said: ' + text;
        try {
            const res = await fetch('/api/chat/message', {
                method: 'POST',
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            const respDiv = document.getElementById('response');
            if (respDiv) respDiv.innerHTML = `<p class="text-green-700">${data.response}</p>`;
            const utterance = new SpeechSynthesisUtterance(data.response);
            utterance.lang = 'hi-IN';
            speechSynthesis.speak(utterance);
        } catch (e) {}
    };
    recognition.start();
};

console.log('%c✅ Voice Mic + Token FIXED', 'color:green; font-weight:bold');console.log('%c✅ Voice + Token Fixed', 'color:green; font-weight:bold');
// Check login on protected pages
function checkAuth() {
    const token = localStorage.getItem('token');
    const publicPages = ['/login', '/signup'];
    if (!token && !publicPages.includes(window.location.pathname)) {
        window.location.href = '/login';
    }
}

// Logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

// ====================== ANALYSIS ======================
async function uploadCropImage(file, problemText = "My crop looks unhealthy") {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('problem', problemText);

    const res = await fetch('/api/analysis/upload', { method: 'POST', body: formData });
    if (!res.ok) throw new Error('Upload failed');
    return await res.json();
}

// ====================== CHAT ======================
async function sendChatMessage(message) {
    const res = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });
    if (!res.ok) throw new Error('Chat failed');
    return await res.json();
}

// ====================== VOICE MODE ======================


// ====================== COMMUNITY POST ======================
async function createCommunityPost(formData) {
    const res = await fetch('/api/community/post', {
        method: 'POST',
        body: formData
    });
    if (!res.ok) throw new Error('Post failed');
    return await res.json();
}

// ====================== MARKET & SCHEMES (already in templates) ======================

// ====================== COMMON FUNCTIONS ======================
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-24 left-1/2 -translate-x-1/2 px-6 py-3 rounded-2xl text-white text-sm shadow-xl ${type === 'success' ? 'bg-green-600' : 'bg-red-600'}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Auto run on every page
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    console.log('%c🚀 KrishiVani - Single JS File Loaded Successfully!', 'color:#10b981; font-weight:bold; font-size:13px');
});

// Export for inline scripts (optional)
window.uploadCropImage = uploadCropImage;
window.sendChatMessage = sendChatMessage;
window.startVoice = startVoice;
window.createCommunityPost = createCommunityPost;
window.logout = logout;
window.showToast = showToast;