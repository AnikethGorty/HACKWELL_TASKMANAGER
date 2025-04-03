from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# File to store tasks
TASKS_FILE = 'tasks.json'

def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    tasks = load_tasks()
    
    if request.method == 'POST':
        try:
            task_data = request.get_json()
            
            # Validation (same as before)
            required_fields = ['taskName', 'taskDescription', 'skillsRequired', 'startTime', 'endTime']
            for field in required_fields:
                if field not in task_data or not task_data[field]:
                    return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

            if len(task_data['skillsRequired']) > 15:
                return jsonify({"status": "error", "message": "Maximum 15 skills allowed"}), 400
                
            # Add metadata
            task_data['id'] = len(tasks) + 1
            task_data['created_at'] = datetime.now().isoformat()
            
            tasks.append(task_data)
            save_tasks(tasks)
            
            return jsonify({
                "status": "success", 
                "task_id": task_data['id'],
                "message": "Task created successfully"
            })

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # GET request
    return jsonify({"tasks": tasks})

if __name__ == '__main__':
    app.run(debug=True)