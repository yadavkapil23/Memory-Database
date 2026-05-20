// Update dashboard.html to use authenticated user_id

const fs = require('fs');
const path = '/sessions/epic-brave-ramanujan/mnt/Memory_Project/static/dashboard.html';

let content = require('fs').readFileSync(path, 'utf8');

// Add authentication check at the beginning
const authCheck = `
    // Check authentication on page load
    window.addEventListener('load', () => {
        const user_id = localStorage.getItem('user_id');
        const username = localStorage.getItem('username');
        
        if (!user_id) {
            window.location.href = '/';
            return;
        }
        
        // Update user display
        const userNameEl = document.getElementById('userName');
        const userAvatarEl = document.getElementById('userAvatar');
        
        if (userNameEl) userNameEl.textContent = username || 'User';
        if (userAvatarEl) userAvatarEl.textContent = (username || 'U')[0].toUpperCase();
        
        loadDashboard();
    });
`;

// Add logout function
const logoutFunc = `
    function logout() {
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('user_name');
        window.location.href = '/';
    }
`;

// Replace API_BASE with proper user_id passing
content = content.replace(
    "const API_BASE = '/api';",
    `const API_BASE = '/api';
    const user_id = localStorage.getItem('user_id');`
);

// Update all fetch calls to include user_id parameter
content = content.replace(/fetch\(API_BASE \+ '\/api\/memories'/g, "fetch(API_BASE + '/memories?user_id=' + user_id");
content = content.replace(/fetch\(API_BASE \+ '\/stats/g, "fetch(API_BASE + '/stats?user_id=' + user_id");
content = content.replace(/fetch\(API_BASE \+ '\/insights/g, "fetch(API_BASE + '/insights?user_id=' + user_id");
content = content.replace(/fetch\(API_BASE \+ '\/search/g, "fetch(API_BASE + '/search?user_id=' + user_id");

// Update memory creation to include user_id
content = content.replace(
    "const response = await fetch(API_BASE + '/memories'",
    "const response = await fetch(API_BASE + '/memories?user_id=' + user_id"
);

// Add logout button to header
content = content.replace(
    '<span id="userName">User</span>',
    '<span id="userName">User</span> | <button onclick="logout()" style="background: none; border: none; color: #667eea; cursor: pointer; font-size: 12px; margin-left: 10px;">Logout</button>'
);

// Inject auth check and logout function before closing script tag
content = content.replace(
    '<script>',
    '<script>' + authCheck + logoutFunc
);

require('fs').writeFileSync(path, content, 'utf8');
console.log('Dashboard updated with authentication');
