// Theme Space Selector Engine Mapping
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const targetTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', targetTheme);
});

let sessionProfileStore = { id: null, role: null };

// --- Authentication & Registration Form Component Actions ---
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const authStatusMsg = document.getElementById('auth-status-msg');

// Toggle View Interfaces to Registration mode
tabRegister.addEventListener('click', () => {
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
    tabRegister.style.color = 'var(--primary)';
    tabLogin.style.color = 'var(--text-muted)';
    authStatusMsg.innerText = '';
});

// Toggle View Interfaces back to Login mode
tabLogin.addEventListener('click', () => {
    registerForm.style.display = 'none';
    loginForm.style.display = 'block';
    tabLogin.style.color = 'var(--primary)';
    tabRegister.style.color = 'var(--text-muted)';
    authStatusMsg.innerText = '';
});

// Async Pipeline Route Controller for Authentication Handling
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();

        if (response.ok) {
            sessionProfileStore.id = data.userId;
            sessionProfileStore.role = data.role;
            document.getElementById('auth-section').style.display = 'none';
            document.getElementById('logout-btn').style.display = 'inline-flex';
            loadDashboard();
        } else {
            authStatusMsg.style.color = '#ef4444';
            authStatusMsg.innerText = data.message;
        }
    } catch (err) {
        console.error("Critical Authentication Gateway Failure:", err);
    }
});

// Real-World Signup Form Submission Pipeline Controller
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    const role = document.getElementById('reg-role').value;

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();

        if (response.ok) {
            authStatusMsg.style.color = '#10b981'; // Green success tracker
            authStatusMsg.innerText = data.message;
            document.getElementById('reg-username').value = '';
            document.getElementById('reg-password').value = '';
            setTimeout(() => tabLogin.click(), 2200); // Shift tabs smoothly back to gateway
        } else {
            authStatusMsg.style.color = '#ef4444';
            authStatusMsg.innerText = data.message;
        }
    } catch (err) {
        console.error("Critical Registration Pipeline Error:", err);
    }
});

// Structural Dynamic UI Template View Loader Matrix
async function loadDashboard() {
    const dashSection = document.getElementById('dashboard-section');
    dashSection.style.display = 'block';
    dashSection.innerHTML = `<h3>Initializing runtime access configurations...</h3>`;

    if (sessionProfileStore.role === 'student') {
        const res = await fetch(`/api/student/${sessionProfileStore.id}`);
        const student = await res.json();
        
        dashSection.innerHTML = `
            <h2>👨‍🎓 Academic Profile Dashboard: ${student.name}</h2>
            <div style="margin-top: 1.2rem; line-height: 1.8;">
                <p><strong>System Roll Number:</strong> ${student.roll_no}</p>
                <p><strong>Attendance Matrix Log:</strong> <span style="color: ${student.attendance_pct >= 75 ? '#10b981' : '#ef4444'}">${student.attendance_pct}%</span></p>
                <p><strong>Outstanding Backlogs:</strong> ${student.backlogs}</p>
                <h4 style="margin-top: 1.5rem; letter-spacing: -0.2px;">Performance Metric Grid Values</h4>
                <ul style="padding-left: 1.2rem; margin-top: 0.4rem;">
                    ${student.marks && student.marks.length > 0 ? student.marks.map(m => `<li>${m.subject_name}: <strong>${m.marks_obtained} / 100 Marks</strong></li>`).join('') : '<li>No academic grade values initialized inside database ledger.</li>'}
                </ul>
            </div>`;

    } else if (sessionProfileStore.role === 'faculty') {
        const res = await fetch(`/api/faculty/${sessionProfileStore.id}`);
        const faculty = await res.json();
        
        dashSection.innerHTML = `
            <h2>👩‍🏫 Instructional Officer Dashboard: ${faculty.name}</h2>
            <div style="margin-top: 1.2rem; line-height: 1.8;">
                <p><strong>Active Ledger Monthly Salary:</strong> ₹${faculty.salary}</p>
                <p><strong>Validated Clocked Presence:</strong> ${faculty.attendance_pct}%</p>
                <h4 style="margin-top: 1.5rem; letter-spacing: -0.2px;">Allotted Curriculum Schedules</h4>
                <ul style="padding-left: 1.2rem; margin-top: 0.4rem;">
                    ${faculty.timetable && faculty.timetable.length > 0 ? faculty.timetable.map(t => `<li><strong>${t.subject_name}</strong> - Runtime Block: <em>${t.class_time}</em></li>`).join('') : '<li>No allotted lecture schedules registered in data node schema.</li>'}
                </ul>
            </div>`;

    } else if (sessionProfileStore.role === 'admin') {
        dashSection.innerHTML = `
            <h2>⚙️ Core Administrative Control Terminal</h2>
            <div style="margin-top: 1.2rem;">
                <label style="font-weight: 500; display: block; margin-bottom: 0.5rem;">Override Student Attendance State Records (Absence Cancellation)</label>
                <input type="text" id="adm-roll" placeholder="Enter Target Student Roll String ID (e.g. STU003)">
                <input type="number" id="adm-att" placeholder="Define Absolute Percentage Matrix Target (e.g. 82)">
                <button onclick="executeAdminModification()" class="btn-primary" style="margin-top: 0.4rem; width: 100%;">Commit System Structural Modification</button>
            </div>
            <p id="admin-status-log" style="margin-top: 1.2rem; font-weight: 600; color: #10b981;"></p>`;
    }
}

// Administrative API Write Pipeline Caller
async function executeAdminModification() {
    const roll_no = document.getElementById('adm-roll').value;
    const attendance = document.getElementById('adm-att').value;
    
    const response = await fetch('/api/admin/update-attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roll_no, attendance })
    });
    const result = await response.json();
    document.getElementById('admin-status-log').innerText = result.message;
}

// AI Message Core Shell Subsystem Handler (Synchronized for Valid .txt File Pipeline delivery)
document.getElementById('send-ai-btn').addEventListener('click', async () => {
    const inputEl = document.getElementById('ai-query');
    const query = inputEl.value.trim();
    if (!query) return;

    const chatBox = document.getElementById('chat-box');
    
    chatBox.innerHTML += `<div class="chat-msg user"><strong>You:</strong> ${query}</div>`;
    inputEl.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/api/ai-assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();

        let replyHtml = `<div class="chat-msg ai"><strong>AI:</strong> ${data.response}</div>`;
        
        if (data.type === 'file_link') {
            data.data.forEach(item => {
                replyHtml += `
                    <div class="chat-msg ai" style="margin-top: 4px; border-left: 3px solid var(--primary); background: rgba(99, 102, 241, 0.05);">
                        <a href="/static/materials/la_notes.txt" download="la_notes.txt" style="color: var(--primary); font-weight: 600; text-decoration: underline;">
                            📥 Access Portal Download: la_notes.txt
                        </a>
                    </div>`;
            });
        }
        
        chatBox.innerHTML += replyHtml;
    } catch (err) {
        chatBox.innerHTML += `<div class="chat-msg ai" style="color: #ef4444;"><strong>AI System Error:</strong> Transmission payload timeout tracking link failed.</div>`;
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;
});

document.getElementById('logout-btn').addEventListener('click', () => {
    location.reload(); 
});
