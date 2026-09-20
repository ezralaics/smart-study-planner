// Comprehensive IT, MPU, and Cooperative Placement list
const itModules = [
    "CD102 — Computer Ethics (Diploma)",
    "CD103 — Fundamental of Database Systems",
    "CD105 — System Analysis & Design",
    "CD106 — Java Programming 1 (Diploma)",
    "CD107 — Java Programming 2 (Diploma)",
    "CD108 — Discrete Mathematics 1 (Diploma)",
    "CD109 — Introduction to Information Technology (Diploma)",
    "CD110 — Introduction to Internet Technologies (Diploma)",
    "CD204 — User Interface Design",
    "CD206 — Business Programming",
    "CD209 — Managing and Implementing Business Project",
    "CD210 — Creative Problem Solving (Diploma)",
    "CD211 — Wireless and Mobile Technologies (Diploma)",
    "CD212 — Object-Oriented Modeling (Diploma)",
    "CD214 — Operating Systems & Networks (Diploma)",
    "CD215 — Multimedia Programming (Diploma)",
    "KAD2031 — Cooperative Placement 1 (Diploma)",
    "KAD2032 — Cooperative Placement 2 (Diploma)",
    "MPU21103 / MPU2133 — Penghayatan Etika and Peradaban / BM Komunikasi 2",
    "MPU2221 — University Life",
    "MPU2232 — Integriti dan Antirasuah",
    "MPU2411 — Extra-Curricular Learning Experience 1",
    "MPU2421 — Extra-Curricular Learning Experience 2",
    "BD100 — Business Communication for Diploma",
    "BD119 — Principle of Accounting",
    "BD120 — Basic and Practices of Marketing",
    "BD127 — Business Essentials",
    "BD128 — Quantitative Techniques",
    "BD129 — Introduction to Statistics",
    "DBB2043 — Introduction to Entrepreneurship"
];

const courseCreditsMap = {
    "CD103": 4, "CD105": 4, "CD106": 4, "CD107": 4, "CD109": 4, "CD110": 4, 
    "CD206": 4, "CD209": 4, "CD212": 4, "CD214": 4, "CD215": 4,
    "CD102": 3, "CD108": 3, "CD204": 3, "CD210": 3, "CD211": 3,
    "BD128": 4, "BD129": 4, "BD100": 3, "BD119": 3, "BD120": 3, "BD127": 3, "DBB2043": 3,
    "KAD2031": 3, "KAD2032": 3, "MPU21103": 3, "MPU2133": 3, "MPU2232": 2, 
    "MPU2221": 1, "MPU2411": 1, "MPU2421": 1
};

// --- UTILITIES ---

function startLiveClock() {
    const clockEl = document.getElementById('liveClock');
    const dateEl = document.getElementById('liveDate');
    function update() {
        if (!clockEl || !dateEl) return;
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        dateEl.textContent = now.toLocaleDateString('en-MY', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
    }
    update();
    setInterval(update, 1000);
}

function checkAuth() {
    const userData = localStorage.getItem('student_profile');
    if (userData) {
        const profile = JSON.parse(userData);
        document.querySelectorAll('#displayGreeting, #navGreeting').forEach(el => el.innerText = profile.name);
        if (document.getElementById('editName')) document.getElementById('editName').value = profile.name;
        if (document.getElementById('editStudentType')) document.getElementById('editStudentType').value = profile.program;
        updateCourseInputUI(profile.program);
    }
}

// --- GRADE COMPONENT LOGIC ---

function resetTaskRows() {
    const wrapper = document.getElementById('tasksWrapper');
    if (!wrapper) return;
    wrapper.innerHTML = ''; 
    addTaskRow('Assignment 1', 25);
    addTaskRow('Midterm', 25);
    addTaskRow('Final Exam', 50);
}

function addTaskRow(name = '', weight = '') {
    const wrapper = document.getElementById('tasksWrapper');
    if (!wrapper) return; 

    const row = document.createElement('div');
    row.className = 'task-row row g-2 align-items-end mb-3';
    row.innerHTML = `
        <div class="col-md-5">
            <label class="fw-bold text-muted mb-1" style="font-size: 10px;">COMPONENT NAME</label>
            <input type="text" class="form-control form-control-sm task-name" value="${name}" placeholder="e.g. Quiz">
        </div>
        <div class="col-md-2">
            <label class="fw-bold text-muted mb-1" style="font-size: 10px;">WEIGHT %</label>
            <input type="number" class="form-control form-control-sm task-weight" value="${weight}" onchange="calculateWeights()">
        </div>
        <div class="col-md-4">
            <label class="fw-bold text-muted mb-1" style="font-size: 10px;">DEADLINE</label>
            <input type="date" class="form-control form-control-sm task-deadline">
        </div>
        <div class="col-md-1 text-end">
            <button class="btn btn-sm btn-outline-danger border-0" onclick="this.parentElement.parentElement.remove(); calculateWeights();">
                <i class="bi bi-trash"></i>
            </button>
        </div>`;
    wrapper.appendChild(row);
    calculateWeights();
}

function calculateWeights() {
    let total = 0;
    document.querySelectorAll('.task-weight').forEach(w => total += (parseFloat(w.value) || 0));
    
    const display = document.getElementById('totalWeightDisplay');
    const warning = document.getElementById('weightWarning');
    
    if (display) {
        display.innerText = total + "%";
        display.className = (total === 100) ? 'text-success fw-bold' : 'text-danger fw-bold';
    }
    
    if (warning) warning.classList.toggle('d-none', total === 100);
    return total;
}

// --- COURSE UI & BACKEND SYNC ---

function updateCourseInputUI(program) {
    const wrapper = document.getElementById('courseInputWrapper');
    if (!wrapper) return;

    if (program === "IT") {
        let options = itModules.sort().map(m => `<option value="${m}">${m}</option>`).join('');
        wrapper.innerHTML = `
            <label class="form-label fw-bold small text-muted">SELECT COURSE</label>
            <select id="subName" class="form-select shadow-sm" onchange="handleCourseSelection(this)">
                <option value="">-- Choose Course --</option>
                ${options}
                <option value="MANUAL_ENTRY" class="fw-bold text-primary">+ Add Manually...</option>
            </select>`;
    } else {
        wrapper.innerHTML = `
            <label class="form-label fw-bold small text-muted">COURSE NAME</label>
            <input type="text" id="subName" class="form-control shadow-sm" placeholder="e.g. BD119 — Principle of Accounting">`;
    }
}

function handleCourseSelection(selectObj) {
    if (selectObj.value === "MANUAL_ENTRY") {
        const wrapper = document.getElementById('courseInputWrapper');
        wrapper.innerHTML = `
            <label class="form-label fw-bold small text-muted">MANUAL ENTRY</label>
            <div class="input-group shadow-sm">
                <input type="text" id="subName" class="form-control" placeholder="Enter Course Name">
                <button class="btn btn-outline-secondary" type="button" onclick="updateCourseInputUI('IT')"><i class="bi bi-arrow-left"></i></button>
            </div>`;
        document.getElementById('subName').focus();
    } else {
        autoDetectCredits(selectObj.value);
    }
}

function autoDetectCredits(subName) {
    const creditSelect = document.getElementById('subCredits');
    if (!subName || !creditSelect) return;
    const match = subName.match(/[A-Z]{2,3}\d{3,4}/);
    const courseCode = match ? match[0] : null;
    creditSelect.value = courseCreditsMap[courseCode] || 3;
}

async function loadDashboardData() {
    const container = document.getElementById('planContainer');
    if (!container) return;

    try {
        const res = await fetch('/api/generate_plan');
        const data = await res.json();
        container.innerHTML = data.length ? '' : '<div class="alert alert-light text-center p-5 w-100">No courses added yet.</div>';
        
        data.forEach(sub => {
            const tasksHtml = (sub.tasks || []).map(t => `
                <div class="d-flex justify-content-between border-bottom py-2">
                    <span class="small">${t.name || t.task_name} (${t.weight || t.weightage}%)</span>
                    <span class="badge bg-light text-dark">${t.deadline || t.due_date || 'TBD'}</span>
                </div>`).join('');

            container.innerHTML += `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card h-100 p-3 border-0 shadow-sm" style="border-top: 4px solid #0d6efd !important;">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="fw-bold mb-0 text-truncate">${sub.name}</h6>
                            <button class="btn btn-sm text-danger p-0" onclick="deleteSubject('${sub.name}')"><i class="bi bi-trash"></i></button>
                        </div>
                        <div class="task-list-mini">${tasksHtml || '<small class="text-muted">No tasks</small>'}</div>
                    </div>
                </div>`;
        });
    } catch (e) { console.error(e); }
}

async function deleteSubject(name) {
    if (!confirm(`Remove ${name}?`)) return;
    const res = await fetch('/api/delete_subject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
    if (res.ok) location.reload();
}

function showToast(title, message, type = "success") {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-white bg-${type} border-0 mb-2`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body"><strong>${title}</strong>: ${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}