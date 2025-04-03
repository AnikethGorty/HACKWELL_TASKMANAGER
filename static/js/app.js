// Global variables
const skills = [];
const maxSkills = 15;

// DOM elements
const taskForm = document.getElementById('taskForm');
const skillsContainer = document.getElementById('skillsContainer');
const skillsInput = document.getElementById('skillsInput');
const addSkillBtn = document.getElementById('addSkillBtn');
const messageDiv = document.getElementById('message');

// Initialize the application
function init() {
    // Event listeners
    addSkillBtn.addEventListener('click', addSkill);
    skillsInput.addEventListener('keypress', handleSkillInputKeypress);
    taskForm.addEventListener('submit', handleFormSubmit);
}

// Add skill to the list
function addSkill() {
    const skill = skillsInput.value.trim();
    
    if (skill && !skills.includes(skill)) {
        if (skills.length >= maxSkills) {
            showMessage(`Maximum ${maxSkills} skills allowed`, 'error');
            return;
        }
        
        skills.push(skill);
        renderSkills();
        skillsInput.value = '';
    }
}

// Handle Enter key in skills input
function handleSkillInputKeypress(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        addSkill();
    }
}

// Remove skill from the list
function removeSkill(skill) {
    const index = skills.indexOf(skill);
    if (index !== -1) {
        skills.splice(index, 1);
        renderSkills();
    }
}

// Render skills in the container
function renderSkills() {
    skillsContainer.innerHTML = skills.map(skill => 
        `<span class="skill-tag">${skill} 
         <span style="cursor:pointer; margin-left:5px;" onclick="window.removeSkill('${skill}')">×</span>
        </span>`
    ).join('');
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (skills.length === 0) {
        showMessage('Please add at least one skill', 'error');
        return;
    }

    // Get form data
    const formData = {
        taskName: document.getElementById('taskName').value,
        taskDescription: document.getElementById('taskDescription').value,
        skillsRequired: [...skills], // Create a copy of the skills array
        startTime: document.getElementById('startTime').value,
        endTime: document.getElementById('endTime').value
    };

    // Validate time format
    if (!/^\d{2}:\d{2}:\d{2}$/.test(formData.startTime) || !/^\d{2}:\d{2}:\d{2}$/.test(formData.endTime)) {
        showMessage('Time format must be DD:HH:MM', 'error');
        return;
    }

    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Failed to create task');
        }

        showMessage(`Task created successfully! ID: ${result.task_id}`, 'success');
        taskForm.reset();
        skills.length = 0;
        renderSkills();
        
    } catch (error) {
        console.error('Error:', error);
        showMessage(error.message || 'Error creating task', 'error');
    }
}

// Show message to user
function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.style.display = 'block';
    
    // Hide message after 5 seconds
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Make removeSkill available globally
window.removeSkill = removeSkill;

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);