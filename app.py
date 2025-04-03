from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Store tasks in memory (replace with database in production)
tasks = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'POST':
        # Receive task data from frontend
        task_data = request.get_json()
        
        # Validate skills
        if not isinstance(task_data.get('skillsRequired'), list):
            return jsonify({"status": "error", "message": "Skills must be a list"}), 400
            
        if len(task_data['skillsRequired']) > 15:
            return jsonify({"status": "error", "message": "Maximum 15 skills allowed"}), 400
            
        if any(not isinstance(skill, str) or ' ' in skill for skill in task_data['skillsRequired']):
            return jsonify({"status": "error", "message": "Each skill must be a single word"}), 400
        
        # Add metadata
        task_data['id'] = len(tasks) + 1
        task_data['created_at'] = datetime.now().isoformat()
        task_data['skillsRequired'] = [skill.lower() for skill in task_data['skillsRequired']]  # Normalize
        
        tasks.append(task_data)
        print("New task received:", task_data)  # Debug
        return jsonify({"status": "success", "task_id": task_data['id']})
    
    # GET request - return all tasks
    return jsonify({"tasks": tasks})

if __name__ == '__main__':
    app.run(debug=True)