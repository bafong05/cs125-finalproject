const API_BASE_URL = "http://127.0.0.1:8000";

// --- GLOBAL STATE ---
let allStudents = [];
let allGroups = [];
let allEvents = [];
let currentCalendarDate = new Date();
let attendanceRefreshInterval = null;


// -----------------------------
// Toast Notifications
// -----------------------------
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) {
        alert(message);
        return;
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("visible");
    });

    setTimeout(() => {
        toast.classList.remove("visible");
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 250);
    }, 3200);
}

// -----------------------------
// Debounce Helper
// -----------------------------
function createDebounced(fn, delay = 300) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

// -----------------------------
// Skeleton Loading Helpers
// -----------------------------
function renderStudentSkeleton(count = 5) {
    const tableBody = document.getElementById("member-table-body");
    if (!tableBody) return;

    tableBody.innerHTML = "";
    for (let i = 0; i < count; i++) {
        const row = document.createElement("tr");
        row.className = "skeleton-row";
        row.innerHTML = `
            <td>
                <div class="skeleton skeleton-text"></div>
            </td>
            <td style="text-align:right;">
                <div class="skeleton skeleton-button"></div>
            </td>
        `;
        tableBody.appendChild(row);
    }
}

// -----------------------------
// Fetch Helper (Shared)
// -----------------------------
async function fetchData(endpoint, loadingElementId = null) {
    const loadingElement = loadingElementId
        ? document.getElementById(loadingElementId)
        : null;

    if (loadingElement) loadingElement.style.display = "flex";

    try {
        const res = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error("Fetch error:", err);
        showToast(`Error loading ${endpoint.replace("/", "")}`, "error");
        return [];
    } finally {
        if (loadingElement) loadingElement.style.display = "none";
    }
}

// -----------------------------
// VIEW SWITCHING LOGIC
// -----------------------------
function switchView(mode) {
    const leaderView = document.getElementById("leader-dashboard-view");
    const studentView = document.getElementById("student-view");
    const leaderBtn = document.getElementById("leader-mode-btn");
    const studentBtn = document.getElementById("student-mode-btn");
    const pageTitle = document.getElementById("page-title");

    if (mode === "leader") {
        leaderView.style.display = "block";
        studentView.style.display = "none";
        leaderBtn.classList.add("active");
        leaderBtn.setAttribute("aria-selected", "true");
        studentBtn.classList.remove("active");
        studentBtn.setAttribute("aria-selected", "false");
        if (pageTitle) pageTitle.textContent = "Leader Dashboard";
    } else if (mode === "student") {
        leaderView.style.display = "none";
        studentView.style.display = "block";
        studentBtn.classList.add("active");
        studentBtn.setAttribute("aria-selected", "true");
        leaderBtn.classList.remove("active");
        leaderBtn.setAttribute("aria-selected", "false");
        if (pageTitle) pageTitle.textContent = "Student View";
    }
}

function initViewSwitcher() {
    const leaderBtn = document.getElementById("leader-mode-btn");
    const studentBtn = document.getElementById("student-mode-btn");
    
    if (leaderBtn) {
        leaderBtn.addEventListener("click", () => switchView("leader"));
    }
    if (studentBtn) {
        studentBtn.addEventListener("click", () => switchView("student"));
    }
}

// -----------------------------
// STUDENTS SECTION
// -----------------------------
function toggleStudentsList() {
    const container = document.getElementById("student-section");
    const btn = document.getElementById("students-toggle-btn");

    if (container.style.display === "none" || container.style.display === "") {
        container.style.display = "block";
        btn.innerHTML = "Hide Students ▲";
        btn.setAttribute("aria-expanded", "true");
    } else {
        container.style.display = "none";
        btn.innerHTML = "Show Students ▼";
        btn.setAttribute("aria-expanded", "false");
    }
}

function initStudentsToggle() {
    const btn = document.getElementById("students-toggle-btn");
    if (btn) {
        btn.addEventListener("click", toggleStudentsList);
    }
}

function toggleStudentDetails(id) {
    const row = document.getElementById(`student-details-${id}`);
    const btn = document.querySelector(`button[data-student="${id}"]`);

    if (!row || !btn) return;

    if (row.style.display === "none" || row.style.display === "") {
        row.style.display = "table-row";
        btn.innerText = "Details ▲";
    } else {
        row.style.display = "none";
        btn.innerText = "Details ▼";
    }
}

function renderStudents(students, { updateGlobal = false } = {}) {
    if (updateGlobal) {
        allStudents = students || [];
    }

    const tableBody = document.getElementById("member-table-body");
    tableBody.innerHTML = "";

    if (!students || students.length === 0) {
        tableBody.innerHTML =
            '<tr><td colspan="2" style="text-align:center; padding:16px; color:#6b7280;">No student data available.</td></tr>';
        return;
    }

    students.forEach((student) => {
        const row = document.createElement("tr");
        row.className = "student-row";

        const fullName = `${student.firstName} ${student.lastName}`;
        const guardians = student.guardians || [];

        row.innerHTML = `
            <td class="student-name-cell" style="color: var(--text-primary);">
                ${fullName}
            </td>
            <td style="width: 120px; text-align:right;">
                <button class="btn btn-accent btn-sm" data-student="${student.studentID}" onclick="toggleStudentDetails(${student.studentID})">
                    Details ▼
                </button>
            </td>
        `;
        tableBody.appendChild(row);

        const detailsRow = document.createElement("tr");
        detailsRow.id = `student-details-${student.studentID}`;
        detailsRow.className = "details-row";
        detailsRow.style.display = "none";

        const guardianList = guardians.length
            ? guardians.map((g) => `• ${g}`).join("<br>")
            : "N/A";

        detailsRow.innerHTML = `
            <td colspan="2">
                <div class="details-box">
                    <strong>Student ID:</strong> ${student.studentID}<br>
                    <strong>Age:</strong> ${student.age}<br>
                    <strong>Phone:</strong> ${student.phone || student.phoneNumber || "N/A"}<br>
                    <strong>Email:</strong> ${student.email || "N/A"}<br>
                    <strong>Group ID:</strong> ${student.groupID}<br><br>
                    <strong>Guardian(s):</strong><br>${guardianList}
                </div>
            </td>
        `;
        tableBody.appendChild(detailsRow);
    });
}

// Student search
function initStudentSearch() {
    const searchInput = document.getElementById("student-search");
    if (!searchInput) return;

    const debouncedSearch = createDebounced(() => {
        const term = searchInput.value.trim().toLowerCase();
        if (!term) {
            renderStudents(allStudents);
            return;
        }

        const filtered = allStudents.filter((s) =>
            `${s.firstName} ${s.lastName}`.toLowerCase().includes(term)
        );
        renderStudents(filtered);
    }, 250);

    searchInput.addEventListener("input", debouncedSearch);
}

// -----------------------------
// GROUPS SECTION
// -----------------------------
function toggleGroupsList() {
    const container = document.getElementById("groups-section");
    const btn = document.getElementById("groups-toggle-btn");

    if (container.style.display === "none" || container.style.display === "") {
        container.style.display = "block";
        btn.innerHTML = "Hide Groups ▲";
        btn.setAttribute("aria-expanded", "true");
    } else {
        container.style.display = "none";
        btn.innerHTML = "Show Groups ▼";
        btn.setAttribute("aria-expanded", "false");
    }
}

function initGroupsToggle() {
    const btn = document.getElementById("groups-toggle-btn");
    if (btn) {
        btn.addEventListener("click", toggleGroupsList);
    }
}

function toggleGroupDetails(id) {
    const row = document.getElementById(`group-details-${id}`);
    const btn = document.querySelector(`button[data-group="${id}"]`);

    if (!row || !btn) return;

    if (row.style.display === "none" || row.style.display === "") {
        row.style.display = "table-row";
        btn.innerText = "Members ▲";
    } else {
        row.style.display = "none";
        btn.innerText = "Members ▼";
    }
}

function toggleEventDetails(id) {
    const row = document.getElementById(`event-details-${id}`);
    const btn = document.querySelector(`button[data-event="${id}"]`);

    if (!row || !btn) return;

    if (row.style.display === "none" || row.style.display === "") {
        row.style.display = "table-row";
        btn.innerText = "Details ▲";
    } else {
        row.style.display = "none";
        btn.innerText = "Details ▼";
    }
}

function renderGroups(groups, { updateGlobal = false } = {}) {
    if (updateGlobal) {
        allGroups = groups || [];
    }

    const tableBody = document.getElementById("groups-table-body");
    tableBody.innerHTML = "";

    if (!groups || groups.length === 0) {
        tableBody.innerHTML =
            '<tr><td colspan="2" style="text-align:center; padding:16px; color:#6b7280;">No groups available.</td></tr>';
        return;
    }

    groups.forEach((group) => {
        const row = document.createElement("tr");
        row.className = "group-row";

        // Handle leaders - API should provide leaderNames array
        let leaderNames = "N/A";
        
        // Check if leaderNames exists and is an array with data
        if (group.leaderNames && Array.isArray(group.leaderNames)) {
            if (group.leaderNames.length > 0) {
                leaderNames = group.leaderNames.filter(n => n && n.trim()).join(", ");
            }
        } 
        // Fallback: try to extract from leaders array if leaderNames not available
        else if (group.leaders && Array.isArray(group.leaders) && group.leaders.length > 0) {
            const names = group.leaders
                .map(l => {
                    if (typeof l === 'string') return l.trim();
                    if (l && l.firstName) return `${l.firstName} ${l.lastName || ''}`.trim();
                    return null;
                })
                .filter(n => n && n.length > 0);
            
            if (names.length > 0) {
                leaderNames = names.join(", ");
            }
        }

        // Handle members - API returns members as array of student objects
        let memberNames = "No members assigned";
        if (group.members && Array.isArray(group.members) && group.members.length > 0) {
            memberNames = group.members.map(m => {
                if (typeof m === 'string') {
                    return `• ${m}`;
                } else {
                    return `• ${m.firstName || ''} ${m.lastName || ''}`.trim() || `• Student ID: ${m.studentID || 'N/A'}`;
                }
            }).filter(m => m).join("<br>");
        } else if (group.memberNames && Array.isArray(group.memberNames)) {
            memberNames = group.memberNames.map(m => `• ${m}`).join("<br>");
        }

        row.innerHTML = `
            <td class="student-name-cell" style="color: var(--text-primary);">
                ${escapeHtml(group.name || 'Unnamed Group')} 
                <div style="font-size:0.75em; color: var(--text-muted); margin-top: 2px;">Leader(s): ${escapeHtml(leaderNames)}</div>
            </td>
            <td style="width: 120px; text-align:right;">
                <button class="btn btn-accent btn-sm" data-group="${group.groupID}" onclick="toggleGroupDetails(${group.groupID})">
                    Members ▼
                </button>
            </td>
        `;
        tableBody.appendChild(row);

        const detailsRow = document.createElement("tr");
        detailsRow.id = `group-details-${group.groupID}`;
        detailsRow.className = "details-row";
        detailsRow.style.display = "none";

        detailsRow.innerHTML = `
            <td colspan="2">
                <div class="details-box" style="border-left-color: #f59e0b;">
                    <strong>Group Members:</strong><br>${memberNames}
                </div>
            </td>
        `;
        tableBody.appendChild(detailsRow);
    });
}


// -----------------------------
// EVENT VIEW: POPUP + ATTENDANCE
// -----------------------------
let currentPopupEventID = null;

function closeEventDetailsPopup() {
    const popup = document.getElementById("event-details-popup");
    const backdrop = document.getElementById("popup-backdrop");
    
    // Clear auto-refresh interval
    if (attendanceRefreshInterval) {
        clearInterval(attendanceRefreshInterval);
        attendanceRefreshInterval = null;
    }
    
    if (popup) {
        popup.style.display = "none";
        popup.setAttribute("aria-hidden", "true");
    }
    if (backdrop) {
        backdrop.style.display = "none";
        backdrop.setAttribute("aria-hidden", "true");
    }
    
    // Remove body scroll lock
    document.body.style.overflow = "";
    currentPopupEventID = null;
}

// Global ESC key handler (only add once)
let escKeyHandlerAdded = false;

function initPopupCloseHandlers() {
    // ESC key handler (only add once)
    if (!escKeyHandlerAdded) {
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                const popup = document.getElementById("event-details-popup");
                const isVisible = popup && window.getComputedStyle(popup).display !== "none";
        
                if (isVisible) {
                    closeEventDetailsPopup();
                }
            }
        });
        escKeyHandlerAdded = true;
    }
}

function showEventDetailsPopup(eventID, e) {
    if (e) e.stopPropagation();

    const event = allEvents.find((ev) => ev.eventID === eventID);
    if (!event) return;

    const popup = document.getElementById("event-details-popup");
    const backdrop = document.getElementById("popup-backdrop");
    
    currentPopupEventID = eventID;

    popup.innerHTML = `
        <button class="popup-close-btn" aria-label="Close dialog">&times;</button>
        
        <div style="margin-bottom: var(--spacing-lg);">
            <h3 id="popup-event-title" style="margin-bottom: var(--spacing-xs); color: var(--text-primary); font-size: 1.25rem;">${escapeHtml(event.name)}</h3>
            <p style="color: var(--text-muted); font-size: 0.875rem; margin: 0;">${escapeHtml(event.date)} @ ${escapeHtml(event.time)} • ${escapeHtml(event.location)}</p>
        </div>

        <!-- Live Attendance Display -->
        <div style="background: var(--bg-secondary); padding: var(--spacing-md); border-radius: var(--radius-md); margin-bottom: var(--spacing-lg); border: 1px solid var(--border);">
            <h4 style="color: var(--text-primary); margin: 0 0 var(--spacing-sm) 0; font-size: 0.9375rem; font-weight: 600;">Live Attendance</h4>
            <div id="live-attendance-display">
                <div style="display: flex; align-items: baseline; gap: var(--spacing-sm); margin-bottom: var(--spacing-sm);">
                    <span id="live-attendance-count" style="color: var(--primary); font-weight: 700; font-size: 2rem; line-height: 1;">0</span>
                    <span style="color: var(--text-muted); font-size: 0.875rem;">checked in</span>
                </div>
                <div id="live-attendance-names" style="font-size: 0.8125rem; color: var(--text-secondary); line-height: 1.6; max-height: 200px; overflow-y: auto;">
                    <div style="color: var(--text-muted); font-style: italic;">No one checked in yet</div>
                </div>
            </div>
        </div>

        <!-- Check-In Section -->
        <div style="margin-bottom: var(--spacing-lg);">
            <h4 style="color: var(--text-primary); margin-bottom: var(--spacing-sm); font-size: 0.9375rem; font-weight: 600;">Check In</h4>
            <div class="attendance-row" style="display: flex; gap: var(--spacing-sm);">
                <input 
                    id="checkin-input" 
                    type="number" 
                    placeholder="Enter Student ID"
                    class="attendance-input"
                    aria-label="Student ID for check-in"
                    style="flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 0.9375rem;"
                />
                <button 
                    class="btn btn-accent"
                    data-action="checkin"
                    data-event-id="${event.eventID}"
                    style="padding: 10px 20px; white-space: nowrap;"
                >
                    Check In
                </button>
            </div>
            </div>

        <!-- Check-Out Section -->
        <div style="margin-bottom: var(--spacing-lg);">
            <h4 style="color: var(--text-primary); margin-bottom: var(--spacing-sm); font-size: 0.9375rem; font-weight: 600;">Check Out</h4>
            <div class="attendance-row" style="display: flex; gap: var(--spacing-sm);">
                <input 
                    id="checkout-input" 
                    type="number" 
                    placeholder="Enter Student ID"
                    class="attendance-input"
                    aria-label="Student ID for check-out"
                    style="flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 0.9375rem;"
                />
                <button 
                    class="btn btn-secondary"
                    data-action="checkout"
                    data-event-id="${event.eventID}"
                    style="padding: 10px 20px; white-space: nowrap;"
                >
                    Check Out
                </button>
            </div>
            </div>

        <!-- Finalize Button -->
            <button 
            class="btn btn-danger"
            style="width: 100%; margin-top: var(--spacing-md);"
            data-action="finalize"
            data-event-id="${event.eventID}"
            >
                Finalize Event
            </button>
    `;

    // Attach event listeners to popup buttons
    const closeBtn = popup.querySelector(".popup-close-btn");
    if (closeBtn) {
        closeBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeEventDetailsPopup();
        };
    }
    
    const checkInBtn = popup.querySelector('[data-action="checkin"]');
    if (checkInBtn) {
        checkInBtn.addEventListener("click", () => submitCheckIn(event.eventID));
    }
    
    const checkOutBtn = popup.querySelector('[data-action="checkout"]');
    if (checkOutBtn) {
        checkOutBtn.addEventListener("click", () => submitCheckOut(event.eventID));
    }
    
    const refreshBtn = popup.querySelector('[data-action="refresh-attendance"]');
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => updateLiveAttendance(event.eventID));
    }
    
    const finalizeBtn = popup.querySelector('[data-action="finalize"]');
    if (finalizeBtn) {
        finalizeBtn.addEventListener("click", () => finalizeEvent(event.eventID));
    }

    popup.style.display = "block";
    popup.setAttribute("aria-hidden", "false");
    
    if (backdrop) {
        backdrop.style.display = "block";
        backdrop.setAttribute("aria-hidden", "false");
    }
    
    // Lock body scroll
    document.body.style.overflow = "hidden";
    
    // Focus management
    closeBtn?.focus();
    
    // Initial attendance update
    updateLiveAttendance(event.eventID);
    
    // Set up auto-refresh every 3 seconds
    if (attendanceRefreshInterval) {
        clearInterval(attendanceRefreshInterval);
    }
    attendanceRefreshInterval = setInterval(() => {
        if (currentPopupEventID === event.eventID) {
            updateLiveAttendance(event.eventID);
        }
    }, 3000);
    
    // Set up auto-refresh every 3 seconds
    if (attendanceRefreshInterval) {
        clearInterval(attendanceRefreshInterval);
    }
    attendanceRefreshInterval = setInterval(() => {
        if (currentPopupEventID === event.eventID) {
            updateLiveAttendance(event.eventID);
        }
    }, 3000);
}

// Helper to escape HTML
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Check-in (inline)
async function submitCheckIn(eventID) {
    const input = document.getElementById("checkin-input");
    const studentID = input.value.trim();
    if (!studentID) return showToast("Enter a student ID", "error");
    
    // Convert to integer for API
    const studentIDInt = parseInt(studentID, 10);
    if (isNaN(studentIDInt)) {
        input.value = "";
        return showToast("Student ID must be a number", "error");
    }

    try {
        const res = await fetch(
            `${API_BASE_URL}/events/${eventID}/checkin/${studentIDInt}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );

        if (!res.ok) {
            input.value = "";
            const errorData = await res.json().catch(() => ({}));
            const errorMessage = errorData.detail || "Check-in failed — invalid student or event.";
            return showToast(errorMessage, "error");
        }

        showToast(`Checked in Student ${studentIDInt}`, "success");
        input.value = "";
        updateLiveAttendance(eventID);
    } catch (err) {
        console.error("Check-in error:", err);
        showToast("Check-in failed due to network error.", "error");
    }
}

// Check-out (inline)
async function submitCheckOut(eventID) {
    const input = document.getElementById("checkout-input");
    const studentID = input.value.trim();

    if (!studentID) return showToast("Enter a student ID", "error");
    
    // Convert to integer for API
    const studentIDInt = parseInt(studentID, 10);
    if (isNaN(studentIDInt)) {
        input.value = "";
        return showToast("Student ID must be a number", "error");
    }

    try {
        const res = await fetch(
            `${API_BASE_URL}/events/${eventID}/checkout/${studentIDInt}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            let errorMessage = errorData.detail || "Check-out failed — invalid student or event.";
            
            // Provide more specific error messages
            if (errorMessage.includes("not checked in")) {
                errorMessage = `Student ${studentIDInt} is not checked in. Please check in first.`;
            } else if (errorMessage.includes("Student") && errorMessage.includes("not found")) {
                errorMessage = `Student ${studentIDInt} not found.`;
            } else if (errorMessage.includes("Event") && errorMessage.includes("not found")) {
                errorMessage = `Event not found.`;
            }
            
            input.value = "";
            return showToast(errorMessage, "error");
        }

        const data = await res.json();
        showToast(
            `Checked out Student ${studentIDInt}`,
            "success"
        );

        input.value = "";
        updateLiveAttendance(eventID);
    } catch (err) {
        console.error("Checkout error:", err);
        input.value = "";
        showToast("Checkout failed due to network error.", "error");
    }
}

// Live attendance display
async function updateLiveAttendance(eventID) {
    const liveText = document.getElementById("live-attendance-count");
    const namesContainer = document.getElementById("live-attendance-names");
    if (!liveText) return;

    try {
        const data = await fetchData(`/events/${eventID}/live`);
        const count = data.count || 0;
        const checkedInStudents = data.checkedInStudents || [];
        
        // Debug: Log the data to verify correct student IDs
        console.log("Live attendance update:", {
            eventID,
            count,
            studentIDs: checkedInStudents.map(s => s.studentID),
            students: checkedInStudents.map(s => ({ id: s.studentID, name: s.name }))
        });
        
        // Update the large number display (checked in)
        liveText.innerText = count;
        
        // Update student names list - ensure we're using the correct studentID
        if (namesContainer) {
            if (checkedInStudents.length === 0) {
                namesContainer.innerHTML = '<div style="color: var(--text-muted); font-style: italic;">No one checked in yet</div>';
            } else {
                // Sort by studentID to maintain consistent order
                const sortedStudents = [...checkedInStudents].sort((a, b) => {
                    const idA = parseInt(a.studentID, 10) || 0;
                    const idB = parseInt(b.studentID, 10) || 0;
                    return idA - idB;
                });
                
                const namesList = sortedStudents
                    .map(student => {
                        // Ensure studentID is properly extracted
                        const studentID = student.studentID || student.id;
                        const name = escapeHtml(student.name || `Student ${studentID}`);
                        return `<div style="padding: 2px 0;" data-student-id="${studentID}">• ${name} (ID: ${studentID})</div>`;
                    })
                    .join('');
                namesContainer.innerHTML = namesList;
            }
        }
    } catch (err) {
        liveText.innerText = "—";
        if (namesContainer) {
            namesContainer.innerHTML = '<div style="color: var(--text-muted); font-style: italic;">Error loading names</div>';
        }
        console.error("Error updating live attendance:", err);
    }
}

// Finalize event
async function finalizeEvent(eventID) {
    try {
        const res = await fetch(
            `${API_BASE_URL}/events/${eventID}/finalize`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );
        
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            const errorMessage = errorData.detail || "Finalization failed.";
            return showToast(errorMessage, "error");
        }

        const data = await res.json();

        if (data && data.totalAttendees !== undefined) {
            showToast(
                `Event finalized. Total attendees: ${data.totalAttendees}`,
                "success"
            );
            closeEventDetailsPopup();
            
            // Refresh events list
            const updatedEvents = await fetchData("/events", "events-loading");
            allEvents = updatedEvents;
            renderAllEventViews(allEvents, currentCalendarDate);
        } else {
            showToast("Finalization failed.", "error");
        }
    } catch (err) {
        console.error("Finalize error:", err);
        showToast("Finalization failed due to network error.", "error");
    }
}

// -----------------------------
// EVENTS: LIST VIEW
// -----------------------------
function toggleEventsList() {
    const container = document.getElementById("events-section");
    const btn = document.getElementById("events-toggle-btn");

    if (container.style.display === "none" || container.style.display === "") {
        container.style.display = "block";
        btn.innerHTML = "Hide Events ▲";
        btn.setAttribute("aria-expanded", "true");
    } else {
        container.style.display = "none";
        btn.innerHTML = "Show Events ▼";
        btn.setAttribute("aria-expanded", "false");
    }
}

function initEventsToggle() {
    const btn = document.getElementById("events-toggle-btn");
    if (btn) {
        btn.addEventListener("click", toggleEventsList);
    }
}

function toggleCreateEventForm() {
    const container = document.getElementById("create-event-section");
    const btn = document.getElementById("create-event-toggle-btn");

    if (container.style.display === "none" || container.style.display === "") {
        container.style.display = "block";
        btn.innerHTML = "Hide Form ▲";
        btn.setAttribute("aria-expanded", "true");
    } else {
        container.style.display = "none";
        btn.innerHTML = "Show Form ▼";
        btn.setAttribute("aria-expanded", "false");
    }
}

function initCreateEventToggle() {
    const btn = document.getElementById("create-event-toggle-btn");
    if (btn) {
        btn.addEventListener("click", toggleCreateEventForm);
    }
}

function renderAllEventViews(events, date = currentCalendarDate) {
    renderEventList(events);
}

function renderEventList(events) {
    const tableBody = document.getElementById("event-list-body");
    tableBody.innerHTML = "";

    if (!events || events.length === 0) {
        tableBody.innerHTML =
            '<tr><td colspan="4" style="text-align:center; padding:16px; color:#6b7280;">No events scheduled.</td></tr>';
        return;
    }

    const sortedEvents = [...events].sort((a, b) => {
        const dateA = new Date(`${a.date}T${a.time}`);
        const dateB = new Date(`${b.date}T${b.time}`);
        return dateA - dateB;
    });

    sortedEvents.forEach((event) => {
        const row = document.createElement("tr");
        row.className = "event-list-row";

        row.innerHTML = `
            <td>
                <strong>${escapeHtml(event.name)}</strong> 
                <p style="margin: 0; font-size: 0.8em; color: var(--text-muted);">${escapeHtml(event.location)}</p>
            </td>
            <td>${escapeHtml(event.date)} @ ${escapeHtml(event.time)}</td>
            <td style="width: 100px; text-align:right;">
                <button class="btn btn-secondary btn-sm" data-event="${event.eventID}" onclick="toggleEventDetails(${event.eventID})">
                    Details ▼
                </button>
            </td>
            <td style="width: 100px; text-align:right;">
                <button class="btn btn-accent btn-sm" data-event-id="${event.eventID}" aria-label="Start attendance for ${escapeHtml(event.name)}" onclick="startEventAttendance(${event.eventID}, event)">
                    Start
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);

        // Create details row
        const detailsRow = document.createElement("tr");
        detailsRow.id = `event-details-${event.eventID}`;
        detailsRow.className = "details-row";
        detailsRow.style.display = "none";

        // Format custom fields
        let customFieldsHtml = "";
        if (event.customFields && Object.keys(event.customFields).length > 0) {
            customFieldsHtml = formatCustomFields(event.customFields);
        }

        detailsRow.innerHTML = `
            <td colspan="4">
                <div class="details-box" style="border-left-color: var(--primary);">
                    <strong>Event ID:</strong> ${event.eventID}<br>
                    <strong>Date:</strong> ${escapeHtml(event.date)}<br>
                    <strong>Time:</strong> ${escapeHtml(event.time)}<br>
                    <strong>Location:</strong> ${escapeHtml(event.location)}<br>
                    ${customFieldsHtml ? `<div style="margin-top: var(--spacing-sm); padding-top: var(--spacing-sm); border-top: 1px solid var(--border);"><strong>Additional Details:</strong><br>${customFieldsHtml}</div>` : ''}
                    <div style="margin-top: var(--spacing-sm); padding-top: var(--spacing-sm); border-top: 1px solid var(--border);">
                        <button class="btn btn-secondary btn-sm" onclick="loadEventAttendance(${event.eventID})" style="margin-top: var(--spacing-xs);">
                            View Finalized Attendance
                        </button>
                        <div id="event-attendance-${event.eventID}" style="margin-top: var(--spacing-sm); display: none;"></div>
                    </div>
                </div>
            </td>
        `;
        tableBody.appendChild(detailsRow);
    });
}

// Calendar rendering
function changeMonth(delta) {
    currentCalendarDate.setMonth(currentCalendarDate.getMonth() + delta);
    renderCalendar(allEvents, currentCalendarDate);
}

function initCalendarNavigation() {
    const prevBtn = document.getElementById("calendar-prev-btn");
    const nextBtn = document.getElementById("calendar-next-btn");
    
    if (prevBtn) {
        prevBtn.addEventListener("click", () => changeMonth(-1));
    }
    if (nextBtn) {
        nextBtn.addEventListener("click", () => changeMonth(1));
    }
}

function renderCalendar(events, date = currentCalendarDate) {
    const calendarGrid = document.getElementById("calendar-grid");
    const monthYearDisplay = document.getElementById("current-month-year");
    if (!calendarGrid || !monthYearDisplay) return;

    calendarGrid.innerHTML = "";

    const today = new Date();
    const currentMonth = date.getMonth();
    const currentYear = date.getFullYear();

    const monthNames = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ];
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    monthYearDisplay.innerText = `${monthNames[currentMonth]} ${currentYear}`;

    // Day headers
    dayNames.forEach((day) => {
        const headerDiv = document.createElement("div");
        headerDiv.className = "day-header";
        headerDiv.textContent = day;
        headerDiv.setAttribute("role", "columnheader");
        calendarGrid.appendChild(headerDiv);
    });

    const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    // Leading blanks
    for (let i = 0; i < firstDayOfMonth; i++) {
        const emptyDiv = document.createElement("div");
        emptyDiv.className = "calendar-day empty";
        emptyDiv.setAttribute("aria-hidden", "true");
        calendarGrid.appendChild(emptyDiv);
    }

    for (let day = 1; day <= daysInMonth; day++) {
        const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        const dayEvents = events.filter((event) => event.date === dateString);

        let dayClass = "calendar-day";
        const isToday =
            day === today.getDate() &&
            currentMonth === today.getMonth() &&
            currentYear === today.getFullYear();
        if (isToday) {
            dayClass += " today";
        }

        let dayContent = `<span class="day-number">${day}</span>`;

        dayEvents.forEach((event) => {
            dayContent += `
                <span class="day-event-marker" 
                      data-event-id="${event.eventID}"
                      role="button"
                      tabindex="0"
                      aria-label="Event: ${escapeHtml(event.name)}">
                    ${escapeHtml(event.name)}
                </span>`;
        });

        const dayDiv = document.createElement("div");
        dayDiv.className = dayClass;
        dayDiv.innerHTML = dayContent;
        
        if (dayEvents.length > 0) {
            dayDiv.setAttribute("role", "button");
            dayDiv.setAttribute("tabindex", "0");
            dayDiv.addEventListener("click", (e) => {
                if (e.target.classList.contains("day-event-marker")) {
                    showEventDetailsPopup(parseInt(e.target.dataset.eventId), e);
                } else {
                    showEventDetailsPopup(dayEvents[0].eventID, e);
                }
            });
            dayDiv.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    showEventDetailsPopup(dayEvents[0].eventID, e);
                }
            });
        }
        
        // Attach event listeners to event markers
        const markers = dayDiv.querySelectorAll(".day-event-marker");
        markers.forEach(marker => {
            marker.addEventListener("click", (e) => {
                e.stopPropagation();
                showEventDetailsPopup(parseInt(marker.dataset.eventId), e);
            });
            marker.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    e.stopPropagation();
                    showEventDetailsPopup(parseInt(marker.dataset.eventId), e);
                }
            });
        });
        
        calendarGrid.appendChild(dayDiv);
    }
}

// -----------------------------
// STUDENT VIEW FUNCTIONS
// -----------------------------
async function handleStudentLookup(e) {
    e.preventDefault();
    const studentID = document.getElementById("student-id-input").value;
    const contentDiv = document.getElementById("student-dashboard-content");
    const nameDisplay = document.getElementById("student-name");

    const student = allStudents.find((s) => String(s.studentID) === studentID);
    if (!student) {
        showToast(`Student ID ${studentID} not found.`, "error");
        document.getElementById("student-attendance-loading").style.display = "none";
        contentDiv.style.display = "none";
        return;
    }

    const studentName = `${student.firstName} ${student.lastName}`;
    nameDisplay.innerText = `Welcome, ${studentName}! (ID: ${studentID})`;

    const attendanceHistory = await fetchData(
        `/attendance/${studentID}`,
        "student-attendance-loading"
    );

    renderStudentUpcomingEvents(studentID, allEvents);
    renderStudentAttendanceHistory(attendanceHistory);

    contentDiv.style.display = "block";
}

function renderStudentUpcomingEvents(studentID, events) {
    const container = document.getElementById("student-upcoming-events");
    container.innerHTML = "";

    if (!events.length) {
        container.innerHTML = "<p>No upcoming events scheduled.</p>";
        return;
    }

    events.forEach((event) => {
        const isRegistered = Math.random() > 0.5; // mock
        const statusClass = isRegistered ? "status-registered" : "status-not-registered";
        const statusText = isRegistered ? "Registered" : "Not Registered";

        container.innerHTML += `
            <div class="parent-event-card">
                <strong>${event.name}</strong> 
                <span class="registration-status ${statusClass}">${statusText}</span>
                <p>Date: ${event.date} @ ${event.time}</p>
                <p>Location: ${event.location}</p>
            </div>
        `;
    });
}

function renderStudentAttendanceHistory(records) {
    const tableBody = document.getElementById("student-attendance-body");
    tableBody.innerHTML = "";

    if (!records || records.length === 0) {
        tableBody.innerHTML =
            '<tr><td colspan="4" style="text-align:center;">No attendance history.</td></tr>';
        return;
    }

    records.forEach((record) => {
        tableBody.innerHTML += `
            <tr>
                <td>${record.eventName || "N/A"}</td>
                <td>${record.date}</td>
                <td>${record.checkOutTime ? "Completed" : "Checked-In"}</td>
                <td>${
                    record.checkInTime
                        ? new Date(record.checkInTime).toLocaleTimeString()
                        : "N/A"
                }</td>
            </tr>
        `;
    });
}

// -----------------------------
// FORM VALIDATION
// -----------------------------
function validateEventForm() {
    const name = document.getElementById("event-name").value.trim();
    const date = document.getElementById("event-date").value;
    const time = document.getElementById("event-time").value;
    const location = document.getElementById("event-location").value.trim();
    
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll(".error-message").forEach(el => {
        el.textContent = "";
        el.style.display = "none";
    });
    
    // Validate name
    if (!name || name.length < 1) {
        showFieldError("event-name-error", "Event name is required");
        isValid = false;
    } else if (name.length > 100) {
        showFieldError("event-name-error", "Event name must be 100 characters or less");
        isValid = false;
    }
    
    // Validate date
    if (!date) {
        showFieldError("event-date-error", "Date is required");
        isValid = false;
    } else {
        const eventDate = new Date(`${date}T${time || "00:00"}`);
        const now = new Date();
        if (eventDate < now) {
            showFieldError("event-date-error", "Event date must be in the future");
            isValid = false;
        }
    }
    
    // Validate time
    if (!time) {
        showFieldError("event-time-error", "Time is required");
        isValid = false;
    }
    
    // Validate location
    if (!location || location.length < 1) {
        showFieldError("event-location-error", "Location is required");
        isValid = false;
    } else if (location.length > 200) {
        showFieldError("event-location-error", "Location must be 200 characters or less");
        isValid = false;
    }
    
    return isValid;
}

function showFieldError(errorId, message) {
    const errorEl = document.getElementById(errorId);
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = "block";
    }
}

function initEventForm() {
    const form = document.getElementById("create-event-form");
    if (!form) return;
    
    form.addEventListener("submit", async function(e) {
        e.preventDefault();
        
        if (!validateEventForm()) {
            showToast("Please fix the form errors before submitting.", "error");
            return;
        }

        const newEvent = {
            eventID: Date.now(),
            name: document.getElementById("event-name").value.trim(),
            date: document.getElementById("event-date").value,
            time: document.getElementById("event-time").value,
            location: document.getElementById("event-location").value.trim(),
            customFields: {
                description: document.getElementById("event-description").value.trim(),
            }
        };

        try {
            const response = await fetch(`${API_BASE_URL}/events`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newEvent)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Failed to create event: ${errorData.detail || "Unknown error"}`);
            }
            
            const result = await response.json();
            
            this.reset();
            // Clear error messages
            document.querySelectorAll(".error-message").forEach(el => {
                el.textContent = "";
                el.style.display = "none";
            });
            
            showToast(`Event '${newEvent.name}' created successfully!`, "success");
            
            // Re-fetch all events and re-render
            const updatedEvents = await fetchData("/events", "events-loading");
            allEvents = updatedEvents;
            renderAllEventViews(allEvents, currentCalendarDate);

        } catch (error) {
            console.error("Creation error:", error);
            showToast(`Error creating event: ${error.message || "Could not connect to the API."}`, "error");
        }
    });
}

// -----------------------------
// INITIAL LOAD
// -----------------------------
async function init() {
    try {
        // Initialize event listeners
        initViewSwitcher();
        initStudentsToggle();
        initGroupsToggle();
        initEventsToggle();
        initCreateEventToggle();
        initPopupCloseHandlers();
        initEventForm();
        
        const lookupForm = document.getElementById("student-lookup-form");
        if (lookupForm) {
            lookupForm.addEventListener("submit", handleStudentLookup);
        }

        // Show loading skeleton
    renderStudentSkeleton();

        // Fetch and render data
    const students = await fetchData("/students", "students-loading");
        if (students && students.length > 0) {
    renderStudents(students, { updateGlobal: true });
    initStudentSearch();
        } else {
            renderStudents([], { updateGlobal: true });
        }

    const groups = await fetchData("/groups", "groups-loading");
        if (groups && groups.length > 0) {
            // Debug: log groups data to see structure
            console.log("=== GROUPS DATA RECEIVED ===");
            console.log("Number of groups:", groups.length);
            
            // Check Middle School A specifically
            const middleSchoolA = groups.find(g => g.groupID === 1 || g.name === "Middle School A");
            if (middleSchoolA) {
                console.log("=== MIDDLE SCHOOL A DATA ===");
                console.log("Full object:", JSON.stringify(middleSchoolA, null, 2));
                console.log("leaderNames property:", middleSchoolA.leaderNames);
                console.log("leaderNames type:", typeof middleSchoolA.leaderNames);
                console.log("leaderNames is array:", Array.isArray(middleSchoolA.leaderNames));
                console.log("leaders property:", middleSchoolA.leaders);
            }
            
            console.log("Full groups array:", JSON.stringify(groups, null, 2));
            groups.forEach(g => {
                console.log(`\nGroup ${g.groupID} (${g.name}):`, {
                    hasLeaders: !!g.leaders,
                    leadersType: typeof g.leaders,
                    leadersIsArray: Array.isArray(g.leaders),
                    leadersCount: g.leaders?.length || 0,
                    leadersValue: g.leaders,
                    hasLeaderNames: !!g.leaderNames,
                    leaderNamesType: typeof g.leaderNames,
                    leaderNamesIsArray: Array.isArray(g.leaderNames),
                    leaderNamesCount: g.leaderNames?.length || 0,
                    leaderNamesValue: g.leaderNames,
                    membersCount: g.members?.length || 0,
                    memberNamesCount: g.memberNames?.length || 0
                });
            });
            console.log("=== END GROUPS DATA ===\n");
    renderGroups(groups, { updateGlobal: true });
        } else {
            console.warn("No groups data received or empty array");
            renderGroups([], { updateGlobal: true });
        }

    const events = await fetchData("/events", "events-loading");
        allEvents = events || [];
        
        // Debug: Check if customFields are being loaded
        if (allEvents.length > 0) {
            console.log("=== EVENTS DATA DEBUG ===");
            console.log("Number of events:", allEvents.length);
            allEvents.forEach((ev, idx) => {
                console.log(`Event ${idx + 1} (ID: ${ev.eventID}, Name: ${ev.name}):`, {
                    hasCustomFields: !!ev.customFields,
                    customFieldsKeys: ev.customFields ? Object.keys(ev.customFields) : [],
                    customFields: ev.customFields
                });
            });
            console.log("=== END EVENTS DEBUG ===");
        }

        // Initialize event views
    renderAllEventViews(allEvents, currentCalendarDate);

        // Set initial view
    switchView("leader");
        
        console.log("Initialization complete. Students:", allStudents.length, "Groups:", allGroups.length, "Events:", allEvents.length);
    } catch (error) {
        console.error("Initialization error:", error);
        showToast("Error initializing application. Please refresh the page.", "error");
    }
}

// Make functions globally accessible for onclick handlers
window.toggleStudentDetails = toggleStudentDetails;
window.toggleGroupDetails = toggleGroupDetails;
window.toggleEventDetails = toggleEventDetails;
window.showEventDetailsPopup = showEventDetailsPopup;
window.closeEventDetailsPopup = closeEventDetailsPopup;
window.submitCheckIn = submitCheckIn;
window.submitCheckOut = submitCheckOut;
window.updateLiveAttendance = updateLiveAttendance;
window.finalizeEvent = finalizeEvent;
window.switchView = switchView;
window.toggleStudentsList = toggleStudentsList;
window.toggleGroupsList = toggleGroupsList;
window.toggleEventsList = toggleEventsList;
window.toggleCreateEventForm = toggleCreateEventForm;
window.loadEventAttendance = loadEventAttendance;

// Load and display finalized attendance for an event
async function loadEventAttendance(eventID) {
    const container = document.getElementById(`event-attendance-${eventID}`);
    if (!container) return;
    
    // Toggle visibility
    if (container.style.display === "none") {
        container.style.display = "block";
        container.innerHTML = '<div style="color: var(--text-muted); font-style: italic;">Loading attendance...</div>';
        
        try {
            const data = await fetchData(`/events/${eventID}/attendance`);
            
            if (!data) {
                container.innerHTML = '<div style="color: var(--text-muted); font-style: italic;">Error loading attendance data.</div>';
                return;
            }
            
            // Check status from backend
            if (data.status === "not_started") {
                container.innerHTML = `<div style="color: var(--text-muted); font-style: italic;">${data.message || "The event hasn't been started yet."}</div>`;
                return;
            }
            
            if (data.status === "in_progress") {
                container.innerHTML = `<div style="color: var(--text-muted); font-style: italic;">${data.message || "Event is in progress. Finalize to view attendance data."}</div>`;
                return;
            }
            
            // If status is "finalized" or has finalized data, show the full information
            const hasRegistered = data?.registered && data.registered.length > 0;
            const hasWalkIns = data?.walkIns && data.walkIns.length > 0;
            
            if (!hasRegistered && !hasWalkIns) {
                container.innerHTML = '<div style="color: var(--text-muted); font-style: italic;">The event hasn\'t been started yet.</div>';
                return;
            }
            
            // Calculate actual counts from arrays (more reliable than API counts)
            const actualRegisteredCount = data.registered ? data.registered.length : 0;
            const actualWalkInsCount = data.walkIns ? data.walkIns.length : 0;
            const actualTotalCount = actualRegisteredCount + actualWalkInsCount;
            
            let html = `<div style="margin-top: var(--spacing-sm);">`;
            html += `<strong style="color: var(--text-primary);">Total Attendees: ${actualTotalCount}</strong><br>`;
            html += `<span style="color: var(--text-secondary); font-size: 0.875rem;">Registered: ${actualRegisteredCount} | Walk-ins: ${actualWalkInsCount}</span>`;
            
            if (data.registered && data.registered.length > 0) {
                html += `<div style="margin-top: var(--spacing-sm);"><strong style="color: var(--text-primary); font-size: 0.875rem;">Registered Attendees (${actualRegisteredCount}):</strong>`;
                html += `<ul style="margin: var(--spacing-xs) 0; padding-left: 20px; font-size: 0.875rem; color: var(--text-secondary);">`;
                data.registered.forEach(attendee => {
                    const name = `${escapeHtml(attendee.firstName || '')} ${escapeHtml(attendee.lastName || '')}`.trim();
                    html += `<li>${name || 'Unknown'} (ID: ${attendee.studentID})</li>`;
                });
                html += `</ul></div>`;
            }
            
            if (data.walkIns && data.walkIns.length > 0) {
                html += `<div style="margin-top: var(--spacing-sm);"><strong style="color: var(--text-primary); font-size: 0.875rem;">Walk-ins (${actualWalkInsCount}):</strong>`;
                html += `<ul style="margin: var(--spacing-xs) 0; padding-left: 20px; font-size: 0.875rem; color: var(--text-secondary);">`;
                data.walkIns.forEach(attendee => {
                    const name = `${escapeHtml(attendee.firstName || '')} ${escapeHtml(attendee.lastName || '')}`.trim();
                    html += `<li>${name || 'Unknown'} (ID: ${attendee.studentID})</li>`;
                });
                html += `</ul></div>`;
            }
            
            html += `</div>`;
            container.innerHTML = html;
        } catch (err) {
            console.error("Error loading attendance:", err);
            container.innerHTML = `<div style="color: var(--text-error, #dc2626); font-style: italic;">Error loading attendance data: ${err.message || 'Unknown error'}</div>`;
        }
    } else {
        container.style.display = "none";
    }
}

// Helper function to format custom fields for display
function formatCustomFields(customFields) {
    if (!customFields || Object.keys(customFields).length === 0) {
        return "";
    }
    
    let html = "";
    for (const [key, value] of Object.entries(customFields)) {
        const formattedKey = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()).trim();
        
        if (Array.isArray(value)) {
            html += `<p style="margin-bottom: var(--spacing-sm);"><strong style="color: var(--text-primary);">${escapeHtml(formattedKey)}:</strong> <span style="color: var(--text-secondary);">${value.map(v => escapeHtml(String(v))).join(", ")}</span></p>`;
        } else if (typeof value === "boolean") {
            html += `<p style="margin-bottom: var(--spacing-sm);"><strong style="color: var(--text-primary);">${escapeHtml(formattedKey)}:</strong> <span style="color: var(--text-secondary);">${value ? "Yes" : "No"}</span></p>`;
        } else if (typeof value === "object" && value !== null) {
            html += `<p style="margin-bottom: var(--spacing-sm);"><strong style="color: var(--text-primary);">${escapeHtml(formattedKey)}:</strong> <span style="color: var(--text-secondary);">${JSON.stringify(value, null, 2)}</span></p>`;
        } else {
            html += `<p style="margin-bottom: var(--spacing-sm);"><strong style="color: var(--text-primary);">${escapeHtml(formattedKey)}:</strong> <span style="color: var(--text-secondary);">${escapeHtml(String(value))}</span></p>`;
        }
    }
    return html;
}

// Event list view functions
function showEventDetails(eventID, e) {
    if (e) e.stopPropagation();
    
    const event = allEvents.find((ev) => ev.eventID === eventID);
    if (!event) {
        showToast("Event not found.", "error");
        return;
    }
    
    // Debug: Log event data
    console.log("=== SHOW EVENT DETAILS DEBUG ===");
    console.log("Event ID:", eventID);
    console.log("Event object:", event);
    console.log("Has customFields:", !!event.customFields);
    console.log("customFields:", event.customFields);
    console.log("customFields keys:", event.customFields ? Object.keys(event.customFields) : []);
    console.log("=== END DEBUG ===");
    
    // Show event details in a simple format
    const popup = document.getElementById("event-details-popup");
    const backdrop = document.getElementById("popup-backdrop");
    
    popup.innerHTML = `
        <button class="popup-close-btn" aria-label="Close dialog">&times;</button>
        
        <h3 id="popup-event-title" style="margin-bottom: var(--spacing-md); color: var(--text-primary);">${escapeHtml(event.name)}</h3>
        <p style="color: var(--text-muted); margin-bottom: var(--spacing-lg);">Event ID: ${event.eventID}</p>

        <div class="popup-event-info" style="margin-bottom: var(--spacing-lg);">
            <p style="margin-bottom: var(--spacing-sm);"><strong style="color: var(--text-primary);">Date:</strong> <span style="color: var(--text-secondary);">${escapeHtml(event.date)}</span></p>
            <p style="margin-bottom: var(--spacing-sm);"><strong style="color: var(--text-primary);">Time:</strong> <span style="color: var(--text-secondary);">${escapeHtml(event.time)}</span></p>
            <p style="margin-bottom: var(--spacing-sm);"><strong style="color: var(--text-primary);">Location:</strong> <span style="color: var(--text-secondary);">${escapeHtml(event.location)}</span></p>
            ${
                event.customFields && Object.keys(event.customFields).length > 0
                    ? `<div style="margin-top: var(--spacing-md); padding-top: var(--spacing-md); border-top: 1px solid var(--border);">
                        <h4 style="color: var(--text-primary); margin-bottom: var(--spacing-sm); font-size: 0.9375rem; font-weight: 600;">Additional Details:</h4>
                        ${formatCustomFields(event.customFields)}
                    </div>`
                    : ""
            }
        </div>
    `;
    
    // Set current popup event ID for ESC key handler
    currentPopupEventID = eventID;
    
    // Attach close button listener
    const closeBtn = popup.querySelector(".popup-close-btn");
    if (closeBtn) {
        closeBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeEventDetailsPopup();
        };
    }
    
    // Attach backdrop click handler
    if (backdrop) {
        backdrop.addEventListener("click", (e) => {
            if (e.target === backdrop) {
                closeEventDetailsPopup();
            }
        });
    }
    
    popup.style.display = "block";
    popup.setAttribute("aria-hidden", "false");
    
    if (backdrop) {
        backdrop.style.display = "block";
        backdrop.setAttribute("aria-hidden", "false");
    }
    
    document.body.style.overflow = "hidden";
    closeBtn?.focus();
    
    // Set current popup event ID for ESC key handler
    currentPopupEventID = eventID;
}

function startEventAttendance(eventID, e) {
    if (e) e.stopPropagation();
    
    // Use the existing showEventDetailsPopup which includes attendance management
    showEventDetailsPopup(eventID, e);
}

// Expose functions to global scope
window.showEventDetails = showEventDetails;
window.startEventAttendance = startEventAttendance;

document.addEventListener("DOMContentLoaded", init);

// ESC handler for popup
document.addEventListener("DOMContentLoaded", () => {
    initPopupCloseHandlers();
});