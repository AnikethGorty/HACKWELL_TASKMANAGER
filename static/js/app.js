document.addEventListener("DOMContentLoaded", () => {
    const proceedButton = document.getElementById("proceed-btn");
    const sendTaskButton = document.getElementById("send-task-btn");
    const taskAllocatorScreen = document.querySelector(".task-allocator-screen");
    const welcomeScreen = document.querySelector(".welcome-screen");
    const userNameField = document.getElementById("name");
    const userNameDisplay = document.getElementById("user-name");
    const taskNameField = document.getElementById("task-name");
    const skillsField = document.getElementById("skills");
    const deadlineField = document.getElementById("deadline");
    const serverResponseDisplay = document.getElementById("server-response");

    let socket;

    // Connect to WebSocket server
    function connectWebSocket() {
        socket = new WebSocket("ws://localhost:8765");

        socket.onopen = () => {
            console.log("WebSocket connected.");
        };

        socket.onmessage = (event) => {
            serverResponseDisplay.textContent = "Server Response: " + event.data;
        };

        socket.onerror = (error) => {
            console.error("WebSocket Error: ", error);
            serverResponseDisplay.textContent = "Error: Unable to connect to server";
        };

        socket.onclose = () => {
            serverResponseDisplay.textContent = "Connection closed by server";
        };
    }

    // Handle "Proceed" button click
    proceedButton.addEventListener("click", () => {
        const userName = userNameField.value.trim();
        if (userName !== "") {
            userNameDisplay.textContent = userName;
            welcomeScreen.style.display = "none";
            taskAllocatorScreen.style.display = "block";
            connectWebSocket();
        }
    });

    // Handle "Send Task to Server" button click
    sendTaskButton.addEventListener("click", () => {
        const taskName = taskNameField.value.trim();
        const skills = skillsField.value.trim();
        const deadline = deadlineField.value;

        if (taskName && skills && deadline) {
            const taskData = {
                task_name: taskName,
                skills: skills.split(",").map(skill => skill.trim()),
                deadline: deadline
            };

            socket.send(JSON.stringify(taskData));

            taskNameField.value = "";
            skillsField.value = "";
            deadlineField.value = "";
        }
    });
});
