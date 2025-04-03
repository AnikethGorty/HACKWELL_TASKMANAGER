document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    let isDarkMode = false;
    let userName = '';
    let wsConnection = null;
    let serverResponse = "No response yet";

    // Render welcome screen initially
    renderWelcomeScreen();

    function toggleDarkMode() {
        isDarkMode = !isDarkMode;
        document.body.classList.toggle('dark-mode', isDarkMode);
        document.body.classList.toggle('light-mode', !isDarkMode);
    }

    function renderWelcomeScreen() {
        app.innerHTML = `
            <div class="navbar">
                <h1>Task Allocator</h1>
                <button class="btn ${isDarkMode ? 'btn-dark' : 'btn-light'}" id="toggleDarkMode">
                    ${isDarkMode ? '☀️' : '🌙'}
                </button>
            </div>
            <div class="container">
                <div class="card">
                    <h2>Enter Your Name</h2>
                    <input type="text" id="nameInput" class="form-control" placeholder="Your Name">
                    <button class="btn btn-primary" id="proceedBtn">Proceed</button>
                </div>
            </div>
        `;

        document.getElementById('toggleDarkMode').addEventListener('click', toggleDarkMode);
        document.getElementById('proceedBtn').addEventListener('click', () => {
            const nameInput = document.getElementById('nameInput');
            if (nameInput.value.trim()) {
                userName = nameInput.value.trim();
                renderTaskAllocator();
            } else {
                alert('Please enter your name');
            }
        });
    }

    let socket;

function connectWebSocket() {
    socket = new WebSocket('ws://localhost:8765');

    socket.onopen = () => {
        console.log("WebSocket connected");
        document.getElementById('serverResponse').textContent = "Connected to server";
    };

    socket.onmessage = (event) => {
        document.getElementById('serverResponse').textContent = event.data;
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        document.getElementById('serverResponse').textContent = "Connection error";
    };

    socket.onclose = () => {
        console.log("WebSocket disconnected");
        document.getElementById('serverResponse').textContent = "Disconnected";
    };
}

// Call this when your page loads
connectWebSocket();

// Use this function to send tasks
function sendTaskToServer(taskData) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(taskData));
    } else {
        console.error("WebSocket is not connected");
        // Optionally reconnect
        connectWebSocket();
    }
}

    function renderTaskAllocator() {
        let selectedDeadline = null;

        function connectWebSocket() {
            try {
                wsConnection = new WebSocket('ws://localhost:8765');

                wsConnection.onmessage = (event) => {
                    serverResponse = `Server Response: ${event.data}`;
                    updateServerResponse();
                };

                wsConnection.onerror = () => {
                    serverResponse = "Error: Unable to connect to server";
                    updateServerResponse();
                };

                wsConnection.onclose = () => {
                    serverResponse = "Connection closed by server";
                    updateServerResponse();
                };
            } catch (e) {
                serverResponse = `Connection failed: ${e}`;
                updateServerResponse();
            }
        }

        function updateServerResponse() {
            const responseElement = document.getElementById('serverResponse');
            if (responseElement) {
                responseElement.textContent = serverResponse;
            }
        }

        function sendTaskToServer() {
            const taskName = document.getElementById('taskName').value.trim();
            const skills = document.getElementById('skills').value.split(',').map(s => s.trim()).filter(s => s);

            if (taskName && selectedDeadline && wsConnection) {
                const taskData = {
                    task_name: taskName,
                    deadline: formatDate(selectedDeadline),
                    skills: skills
                };

                wsConnection.send(JSON.stringify(taskData));
                serverResponse = "Task sent to server";
                updateServerResponse();

                // Clear form
                document.getElementById('taskName').value = '';
                document.getElementById('skills').value = '';
                selectedDeadline = null;
                updateDeadlineDisplay();
            }
        }

        function formatDate(date) {
            return date.toISOString().split('T')[0];
        }

        function updateDeadlineDisplay() {
            const deadlineDisplay = document.getElementById('deadlineDisplay');
            if (deadlineDisplay) {
                deadlineDisplay.textContent = selectedDeadline 
                    ? `Deadline: ${formatDate(selectedDeadline)}` 
                    : 'Select Deadline';
            }
        }

        async function selectDeadline() {
            try {
                // Using HTML5 date input as a simple alternative
                const dateString = prompt('Enter deadline (YYYY-MM-DD):');
                if (dateString) {
                    const date = new Date(dateString);
                    if (!isNaN(date.getTime())) {
                        selectedDeadline = date;
                        updateDeadlineDisplay();
                    } else {
                        alert('Invalid date format. Please use YYYY-MM-DD.');
                    }
                }
            } catch (e) {
                console.error('Error selecting date:', e);
            }
        }

        connectWebSocket();

        app.innerHTML = `
            <div class="navbar">
                <h1>Welcome, ${userName}</h1>
                <button class="btn ${isDarkMode ? 'btn-dark' : 'btn-light'}" id="toggleDarkMode">
                    ${isDarkMode ? '☀️' : '🌙'}
                </button>
            </div>
            <div class="container">
                <div class="card">
                    <h2>Create New Task</h2>
                    <input type="text" id="taskName" class="form-control" placeholder="Task Name">
                    <input type="text" id="skills" class="form-control" placeholder="Skills (comma-separated)">
                    <div class="deadline-display" id="deadlineDisplay">Select Deadline</div>
                    <button class="btn btn-primary" id="selectDeadlineBtn">Select Deadline</button>
                    <button class="btn btn-primary" id="sendTaskBtn">Send Task to Server</button>
                    <div class="server-response" id="serverResponse">${serverResponse}</div>
                </div>
            </div>
        `;

        document.getElementById('toggleDarkMode').addEventListener('click', toggleDarkMode);
        document.getElementById('selectDeadlineBtn').addEventListener('click', selectDeadline);
        document.getElementById('sendTaskBtn').addEventListener('click', sendTaskToServer);
    }
});
