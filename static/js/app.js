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
        skills.s