const API_BASE_URL = "http://127.0.0.1:8000";

// --- GLOBAL STATE ---
let allStudents = [];
let allEvents = [];
let currentCalendarDate = new Date(); // State for calendar month

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
        // Note: Returning empty array is fine for rendering lists, but if you expect an object, adjust.
        // Assuming API returns lists for /students, /groups, /events, /attendance
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
    const parentView = document.getElementById("parent-view");
    const leaderBtn = document.getElementById("leader-mode-btn");
    const parentBtn = document.getElementById("parent-mode-btn");

    if (mode === "leader") {
        leaderView.style.display = "block";
        parentView.style.display = "none";
        leaderBtn.classList.add("active");
        parentBtn.classList.remove("active");
    } else {
        leaderView.style.display = "none";
        parentView.style.display = "block";
        parentBtn.classList.add("active");
        leaderBtn.classList.remove("active");
    }
}

// -----------------------------
// LEADER VIEW: STUDENTS SECTION
// -----------------------------
function toggleStudentsList() {
    const container = document.getElementById("student-section");
    const btn = document.getElementById("students-toggle-btn");

    if (container.style.display === "none" || container.style.display === "") {
        container.style.display = "block";
        btn.innerHTML = "Hide Students ▲";
    } else {
        container.style.display = "none";
        btn.innerHTML = "Show Students ▼";
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

function renderStudents(students) {
    allStudents = students; // Update global state
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
            <td class="student-name-cell">
        ${fullName}
            </td>
            <td style="width: 120px; text-align:right;">
                <button class="details-btn" data-student="${student.studentID}">
                    Details ▼
                </button>
            </td>
    `       ;
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
                    <strong>studentID:</strong> ${student.studentID}<br>
                    <strong>Age:</strong> ${student.age}<br>
                    <strong>Phone:</strong> ${student.phone || student.phoneNumber || "N/A"}<br>
                    <strong>Email:</strong> ${student.email || "N/A"}<br>
                    <strong>Group ID:</strong> ${student.groupID}<br><br>
                    <strong>Guardian(s):</strong><br>${guardianList}
                </div>
            </td>
        `;
        tableBody.appendChild(detailsRow);

        // Attach click handler
        const btn = row.querySelector(".details-btn");
        btn.addEventListener("click", () => toggleStudentDetails(student.studentID));
    });
}

// -----------------------------
// LEADER VIEW: GROUPS SECTION
// -----------------------------
function toggleGroupsList() {
    const container = document.getElementById("groups-section");
    const btn = document.getElementById("groups-toggle-btn");

    if (container.style.display === "none" || container.style.display === "") {
        container.style.display = "block";
        btn.innerHTML = "Hide Groups ▲";
    } else {
        container.style.display = "none";
        btn.innerHTML = "Show Groups ▼";
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

function renderGroups(groups) {
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

        const leaderNames = group.leaderNames?.join(", ") || "N/A";
        const members = group.memberNames?.map(m => `• ${m}`).join("<br>") || "No members assigned";

        row.innerHTML = `
            <td class="student-name-cell">
                ${group.name} 
                <div style="font-size:0.8em; color:#6b7280;">Leader(s): ${leaderNames}</div>
            </td>
            <td style="width: 120px; text-align:right;">
                <button class="details-btn" data-group="${group.groupID}">
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
                    <strong>Group Members:</strong><br>${members}
                </div>
            </td>
        `;
        tableBody.appendChild(detailsRow);

        // Attach click handler
        const btn = row.querySelector(".details-btn");
        btn.addEventListener("click", () => toggleGroupDetails(group.groupID));
    });
}

// -----------------------------
// LEADER VIEW: EVENT VIEW LOGIC
// -----------------------------
function closeEventDetailsPopup() {
    document.getElementById('event-details-popup').style.display = 'none';
}

function showEventDetailsPopup(eventID, e) {
    if (e) e.stopPropagation(); 
    
    const event = allEvents.find(e => e.eventID === eventID);
    if (!event) return;

    const popup = document.getElementById('event-details-popup');
    
    // Construct the popup content with all the action buttons
    popup.innerHTML = `
        <button class="popup-close-btn" onclick="closeEventDetailsPopup()">&times;</button>
        <h3>${event.name}</h3>
        <p class="event-id">ID: ${event.eventID}</p>
        <div class="popup-event-info">
            <p><strong>Date:</strong> ${event.date}</p>
            <p><strong>Time:</strong> ${event.time}</p>
            <p><strong>Location:</strong> ${event.location}</p>
            ${event.customFields && event.customFields.description ? `<p><strong>Description:</strong> ${event.customFields.description}</p>` : ''}
        </div>
        <div class="popup-event-actions action-group">
            <button class="action-btn btn-check-in" onclick="demoCheckIn(${event.eventID})">Check-In</button>
            <button class="action-btn btn-check-out" onclick="demoCheckOut(${event.eventID})">Check-Out</button>
            <button class="action-btn btn-live-attendance" onclick="viewLiveAttendance(${event.eventID})">Live Attendance</button>
            <button class="action-btn btn-finalize" onclick="finalizeEvent(${event.eventID})">Finalize Event</button>
        </div>
    `;

    popup.style.display = 'block';
}

// === NEW: Switcher and List Renderer ===

// Master function to render both calendar and list views
function renderAllEventViews(events, date = currentCalendarDate) {
    // 1. Render Calendar 
    renderCalendar(events, date);
    
    // 2. Render List (always update the list data)
    renderEventList(events);

    // This ensures the current active view remains visible after a refresh (like event creation)
    const calendarBtn = document.getElementById('calendar-view-btn');
    switchEventView(calendarBtn.classList.contains('active') ? 'calendar' : 'list', false);
}

function switchEventView(mode, updateDescription = true) {
    const calendarContainer = document.getElementById('calendar-view-container');
    const listContainer = document.getElementById('list-view-container');
    const calendarBtn = document.getElementById('calendar-view-btn');
    const listBtn = document.getElementById('list-view-btn');
    const description = document.getElementById('events-view-description');

    if (mode === 'calendar') {
        calendarContainer.style.display = 'block';
        listContainer.style.display = 'none';
        calendarBtn.classList.add('active');
        listBtn.classList.remove('active');
        if (updateDescription) {
            description.innerText = "Click a day with an event to view details and action buttons.";
        }
    } else { // mode === 'list'
        calendarContainer.style.display = 'none';
        listContainer.style.display = 'block';
        listBtn.classList.add('active');
        calendarBtn.classList.remove('active');
        if (updateDescription) {
            description.innerText = "Upcoming events sorted by date. Click 'Actions' for details.";
        }
    }
}

function renderEventList(events) {
    const tableBody = document.getElementById("event-list-body");
    tableBody.innerHTML = '';

    if (!events || events.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:16px; color:#6b7280;">No events scheduled.</td></tr>';
        return;
    }

    // Sort events by date ascending
    const sortedEvents = [...events].sort((a, b) => {
        const dateA = new Date(`${a.date}T${a.time}`);
        const dateB = new Date(`${b.date}T${b.time}`);
        return dateA - dateB;
    });

    sortedEvents.forEach(event => {
        const row = document.createElement('tr');
        row.className = 'event-list-row';
        
        row.innerHTML = `
            <td>
                <strong>${event.name}</strong> 
                <p style="margin: 0; font-size: 0.8em; color: var(--text-muted);">${event.location}</p>
            </td>
            <td>${event.date} @ ${event.time}</td>
            <td style="width: 100px; text-align:right;">
                <button class="details-btn" onclick="showEventDetailsPopup(${event.eventID}, event)">
                    Actions
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// -----------------------------
// LEADER VIEW: CALENDAR LOGIC (Slightly adjusted)
// -----------------------------
function changeMonth(delta) {
    // Modify the global calendar date
    currentCalendarDate.setMonth(currentCalendarDate.getMonth() + delta);
    // Re-render only the calendar, as the list doesn't depend on the month view
    renderCalendar(allEvents, currentCalendarDate);
}


function renderCalendar(events, date = currentCalendarDate) {
    const calendarGrid = document.getElementById('calendar-grid');
    const monthYearDisplay = document.getElementById('current-month-year');
    if (!calendarGrid || !monthYearDisplay) return;

    calendarGrid.innerHTML = '';

    const today = new Date();
    const currentMonth = date.getMonth();
    const currentYear = date.getFullYear();

    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    monthYearDisplay.innerText = `${monthNames[currentMonth]} ${currentYear}`;

    // 1. Add Day Headers
    dayNames.forEach(day => {
        calendarGrid.innerHTML += `<div class="day-header">${day}</div>`;
    });

    // 2. Determine first day of the month
    const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay(); // 0 (Sun) to 6 (Sat)
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    // 3. Render leading empty days
    for (let i = 0; i < firstDayOfMonth; i++) {
        calendarGrid.innerHTML += `<div class="calendar-day empty"></div>`;
    }

    // 4. Render days and events
    for (let day = 1; day <= daysInMonth; day++) {
        // Format the date string as YYYY-MM-DD to match API
        const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        
        // Find events for this specific date
        const dayEvents = events.filter(event => event.date === dateString);

        let dayClass = 'calendar-day';
        const isToday = day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear();
        if (isToday) {
            dayClass += ' today';
        }

        let dayContent = `<span class="day-number">${day}</span>`;
        
        dayEvents.forEach(event => {
            // Use showEventDetailsPopup when clicking the event marker
            dayContent += `
                <span class="day-event-marker" 
                      onclick="showEventDetailsPopup(${event.eventID}, event)">
                    ${event.name}
                </span>`;
        });

        // The day cell itself is not directly clickable to show a single event, but the markers are.
        // If there are events, clicking the day shows the first event's details.
        const dayClickHandler = dayEvents.length > 0 
            ? `showEventDetailsPopup(${dayEvents[0].eventID}, event)` 
            : `event.stopPropagation();`; // Prevents general click action on empty days

        calendarGrid.innerHTML += `<div class="${dayClass}" onclick="${dayClickHandler}">${dayContent}</div>`;
    }
}


// -----------------------------
// LEADER VIEW: EVENT ACTIONS (Updated to call renderAllEventViews)
// -----------------------------
async function demoCheckIn(eventID) {
    const studentID = prompt("Enter Student ID for check-in:");
    if (!studentID) return; 
    
    const response = await fetchData(`/events/${eventID}/checkin/${studentID}`);
    if (response && response.status !== 404) { // Assuming a successful response is not an empty array or 404
         alert(`Student ${studentID} checked in successfully.`);
    } else {
         alert(`Check-in failed. Make sure student ID is correct and event exists.`);
    }
}

async function demoCheckOut(eventID) {
    const studentID = prompt("Enter Student ID for check-out:");
    if (!studentID) return;

    try {
        const res = await fetch(`${API_BASE_URL}/events/${eventID}/checkout/${studentID}`);
        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(errorText);
        }
        const data = await res.json();
        alert(`Student ${studentID} checked out. Duration: ${data.duration_minutes} minutes`);

    } catch (err) {
        console.error("Check-out error:", err);
        alert(`Checkout failed. Make sure student ${studentID} was checked in first.`);
    }
}


async function viewLiveAttendance(eventID) {
    const data = await fetchData(`/events/${eventID}/live`);
    if (data && data.count !== undefined) {
        alert(`Checked in: ${data.count}\nStudents: ${data.checkedIn.join(", ")}`);
    } else {
        alert("Could not retrieve live attendance or no one is currently checked in.");
    }
}

async function finalizeEvent(eventID) {
    const data = await fetchData(`/events/${eventID}/finalize`);
    if (data && data.totalAttendees !== undefined) {
        alert(`Event Finalized!\nTotal attendees: ${data.totalAttendees}`);
        closeEventDetailsPopup(); // Close the popup after finalizing
    } else {
        alert("Finalization failed.");
    }
    
    // Refresh the calendar and list, as the event might be removed or marked as historical
    const updatedEvents = await fetchData("/events", "events-loading");
    allEvents = updatedEvents;
    renderAllEventViews(allEvents, currentCalendarDate); // Use the new master render function
}


// -----------------------------
// LEADER VIEW: CREATE EVENT FORM (Updated to call renderAllEventViews)
// -----------------------------
document.getElementById('create-event-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const newEvent = {
        eventID: Date.now(),
        name: document.getElementById('event-name').value,
        date: document.getElementById('event-date').value,
        time: document.getElementById('event-time').value,
        location: document.getElementById('event-location').value,
        customFields: {
            description: document.getElementById('event-description').value,
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
            throw new Error(`Failed to create event: ${errorData.detail}`);
        }
        
        const result = await response.json();
        
        this.reset();
        alert(`Event '${newEvent.name}' created successfully! ID: ${result.eventID}`);
        
        // Re-fetch all events and re-render the calendar and list
        const updatedEvents = await fetchData("/events", "events-loading");
        allEvents = updatedEvents; // Update global state
        renderAllEventViews(allEvents, currentCalendarDate);


    } catch (error) {
        console.error("Creation error:", error);
        alert(`Error creating event: ${error.message || "Could not connect to the API."}`);
    }
});


// -----------------------------
// PARENT VIEW FUNCTIONS (UNCHANGED)
// -----------------------------
async function handleStudentLookup(e) {
    e.preventDefault();
    const studentID = document.getElementById('student-id-input').value;
    const contentDiv = document.getElementById('parent-dashboard-content');
    const nameDisplay = document.getElementById('parent-student-name');
    
    const student = allStudents.find(s => String(s.studentID) === studentID);
    if (!student) {
        alert(`Student ID ${studentID} not found.`);
        document.getElementById('parent-attendance-loading').style.display = 'none';
        contentDiv.style.display = 'none';
        return;
    }
    
    const studentName = `${student.firstName} ${student.lastName}`;
    nameDisplay.innerText = `Welcome, ${studentName}! (ID: ${studentID})`;
    
    const attendanceHistory = await fetchData(`/attendance/${studentID}`, 'parent-attendance-loading');
    
    renderParentUpcomingEvents(studentID, allEvents);
    renderParentAttendanceHistory(attendanceHistory);
    
    contentDiv.style.display = 'block';
}

function renderParentUpcomingEvents(studentID, events) {
    const container = document.getElementById('parent-upcoming-events');
    container.innerHTML = '';

    if (events.length === 0) {
        container.innerHTML = '<p>No upcoming events scheduled.</p>';
        return;
    }

    events.forEach(event => {
        // Mock registration status for parent view
        // In a real app, this would be an API call: /events/{eventID}/registration/{studentID}
        const isRegistered = Math.random() > 0.5; 
        const statusClass = isRegistered ? 'status-registered' : 'status-not-registered';
        const statusText = isRegistered ? 'Registered' : 'Not Registered';

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

function renderParentAttendanceHistory(records) {
    const tableBody = document.getElementById("parent-attendance-body");
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
                <td>${record.checkInTime ? new Date(record.checkInTime).toLocaleTimeString() : "N/A"}</td>
            </tr>
        `;
    });
}


// -----------------------------
// INITIAL LOAD (Updated to use renderAllEventViews)
// -----------------------------
document.getElementById('student-lookup-form').addEventListener('submit', handleStudentLookup);

async function init() {
    // Note: We are passing the loading element IDs to the fetchData function
    const students = await fetchData("/students", "students-loading");
    renderStudents(students);

    const groups = await fetchData("/groups", "groups-loading");
    renderGroups(groups);

    // Initial event load
    const events = await fetchData("/events", "events-loading");
    allEvents = events; // Set global events
    
    // Set initial view and render both data representations
    switchEventView('calendar', false);
    renderAllEventViews(allEvents, currentCalendarDate);
    
    switchView("leader");
}

document.addEventListener("DOMContentLoaded", init);