from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

TASKS_FILE = 'tasks.json'

def ensure_tasks_file():
    """Ensure tasks file exists and is valid"""
    try:
        # Create file if it doesn't exist
        if not os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'w') as f:
                json.dump([], f)
            return True
        
        # Verify file has valid content
        with open(TASKS_FILE, 'r') as f:
            content = f.read().strip()
            if not content:  # If empty, initialize with empty array
                with open(TASKS_FILE, 'w') as f:
                    json.dump([], f)
            else:
                json.loads(content)  # Test if valid JSON
        return True
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error initializing tasks file: {e}")
        # If corrupted, recreate the file
        try:
            with open(TASKS_FILE, 'w') as f:
                json.dump([], f)
            return True
        except IOError:
            return False

def load_tasks():
    """Safely load tasks from JSON file"""
    if not ensure_tasks_file():
        return []
    
    try:
        with open(TASKS_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tasks: {e}")
        return []

def save_tasks(tasks):
    """Safely save tasks to JSON file"""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
        return True
    except (IOError, TypeError) as e:
        print(f"Error saving tasks: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'GET':
        tasks = load_tasks()
        return jsonify({"tasks": tasks})
    
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
        
        try:
            task_data = request.get_json()
            
            # Validate required fields
            required_fields = ['taskName', 'taskDescription', 'skillsRequired', 'startTime', 'endTime']
            for field in required_fields:
                if field not in task_data or not task_data[field]:
                    return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
            
            # Validate skills
            if not isinstance(task_data['skillsRequired'], list):
                return jsonify({"status": "error", "message": "skillsRequired must be an array"}), 400
            
            # Load existing tasks
            tasks = load_tasks()
            
            # Add metadata
            task_data['id'] = len(tasks) + 1
            task_data['created_at'] = datetime.now().isoformat()
            
            # Save updated tasks
            tasks.append(task_data)
            if not save_tasks(tasks):
                return jsonify({"status": "error", "message": "Failed to save task"}), 500
            
            return jsonify({
                "status": "success", 
                "task_id": task_data['id'],
                "message": "Task created successfully"
            })
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    ensure_tasks_file()  # Initialize on startup
    app.run(debug=True)