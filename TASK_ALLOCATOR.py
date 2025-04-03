from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

TASKS_FILE = 'tasks.json'

def initialize_tasks_file():
    """Ensure tasks file exists and is valid"""
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w') as f:
            json.dump([], f)

def load_tasks():
    """Safely load tasks from JSON file"""
    try:
        initialize_tasks_file()
        
        with open(TASKS_FILE, 'r') as f:
            content = f.read()
            if not content.strip():  # Handle empty file
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tasks: {e}")
        # Reinitialize the file if corrupted
        initialize_tasks_file()
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

def validate_time_format(time_str):
    """Validate YYYY:MM:DD:HH:MM format"""
    try:
        parts = list(map(int, time_str.split(':')))
        if len(parts) != 5:
            return False
        datetime(year=parts[0], month=parts[1], day=parts[2], 
                hour=parts[3], minute=parts[4])
        return True
    except (ValueError, IndexError):
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
        try:
            # Ensure we have JSON data
            if not request.is_json:
                return jsonify({"status": "error", "message": "Request must be JSON"}), 400
                
            task_data = request.get_json()
            
            # Validate required fields
            required_fields = ['taskName', 'taskDescription', 'skillsRequired', 'startTime', 'endTime']
            for field in required_fields:
                if field not in task_data or not task_data[field]:
                    return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

            # Validate time formats
            if not validate_time_format(task_data['startTime']):
                return jsonify({"status": "error", "message": "Invalid start time format. Use YYYY:MM:DD:HH:MM"}), 400
                
            if not validate_time_format(task_data['endTime']):
                return jsonify({"status": "error", "message": "Invalid end time format. Use YYYY:MM:DD:HH:MM"}), 400

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
    # Initialize tasks file on startup
    initialize_tasks_file()
    app.run(debug=True)