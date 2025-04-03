import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Constants
TASKS_FILE = 'tasks.json'
HF_KEY = os.getenv("HUGGINGFACE_TOKEN")

# Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Skills database
skillset = [
    "Welding", "PLC-Programming", "Hydraulics", "Electrical", "Pneumatics",
    "CNC-Operation", "Machining", "Fabrication", "Automation", "Instrumentation",
    "HVAC", "Blueprint-Reading", "3D-Printing", "Quality-Control", "Robotics",
    "Laser-Cutting", "Carpentry", "Soldering", "Networking", "Motor-Repair"
]

def load_and_clear_tasks():
    """Load tasks from JSON file and then clear the file"""
    try:
        # Check if file exists
        if not os.path.exists(TASKS_FILE):
            return []
            
        # Read and parse tasks
        with open(TASKS_FILE, 'r') as f:
            content = f.read()
            if not content.strip():  # Check if file is empty
                return []
            tasks = json.loads(content)
            
        # Clear the file after reading
        with open(TASKS_FILE, 'w') as f:
            f.write('[]')
            
        return tasks if isinstance(tasks, list) else []
        
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading/clearing tasks: {e}")
        # Ensure file is cleared even if error occurs
        with open(TASKS_FILE, 'w') as f:
            f.write('[]')
        return []

def extract_required_skills(tasks):
    """Extract and flatten all skills from tasks"""
    required_skills = []
    for task in tasks:
        if 'skillsRequired' in task and isinstance(task['skillsRequired'], list):
            required_skills.extend(task['skillsRequired'])
    return list(set(required_skills))  # Remove duplicates

def find_most_similar_skills(required_skills):
    """Find most similar skills from skillset for each required skill"""
    results = []
    for skill in required_skills:
        tempdict = {}
        for j in skillset:
            embeddings = model.encode([skill, j])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            tempdict[j] = similarity

        # Find the most similar skill
        max_key, max_value = max(tempdict.items(), key=lambda x: x[1])
        results.append({
            'input_skill': skill,
            'matched_skill': max_key,
            'similarity_score': float(f"{max_value:.4f}")
        })
    return results

def parse_time_input(time_str):
    """Parse time string in YYYY:MM:DD:HH:MM format"""
    try:
        year, month, day, hour, minute = map(int, time_str.split(':'))
        return {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'original_string': time_str
        }
    except (ValueError, AttributeError):
        print(f"Invalid format! Use YYYY:MM:DD:HH:MM (e.g., 2023:12:31:23:59)")
        return None

def calculate_duration(start_time, end_time):
    """Calculate duration between two time points"""
    start = parse_time_input(start_time)
    end = parse_time_input(end_time)
    
    if not start or not end:
        return None
        
    start_dt = datetime(
        year=start['year'],
        month=start['month'],
        day=start['day'],
        hour=start['hour'],
        minute=start['minute']
    )
    
    end_dt = datetime(
        year=end['year'],
        month=end['month'],
        day=end['day'],
        hour=end['hour'],
        minute=end['minute']
    )
    
    duration = end_dt - start_dt
    return {
        'days': duration.days,
        'hours': duration.seconds // 3600,
        'minutes': (duration.seconds % 3600) // 60,
        'total_hours': duration.total_seconds() / 3600
    }

def main():
    # Load tasks and clear the file
    tasks = load_and_clear_tasks()
    
    print(f"\nFound {len(tasks)} tasks to process")
    
    # Extract skills
    required_skills = extract_required_skills(tasks)
    
    if required_skills:
        print(f"\nFound {len(required_skills)} unique skills in tasks:")
        print(", ".join(required_skills))
        
        # Find similar skills
        print("\nMatching skills to skillset:")
        matches = find_most_similar_skills(required_skills)
        for match in matches:
            print(f"Input: {match['input_skill']:20} | Match: {match['matched_skill']:20} | Score: {match['similarity_score']:.4f}")
    
    # Time analysis example
    if tasks:
        print("\nTime Analysis:")
        for task in tasks:
            print(f"\nTask: {task['taskName']}")
            duration = calculate_duration(task['startTime'], task['endTime'])
            if duration:
                print(f"Duration: {duration['days']} days, {duration['hours']} hours, {duration['minutes']} minutes")
                print(f"Total: {duration['total_hours']:.2f} hours")

    print("\nTasks file has been cleared and is ready for new tasks")

def find_matching_employees(employees, required_skills, threshold=0.7):
    """Find employees with matching skills using semantic similarity"""
    matching_employees = []
    
    for employee in employees:
        # Get employee's skills (handle missing field)
        employee_skills = employee.get('skills', [])
        if not employee_skills:
            continue
        
        # Calculate similarity for each required skill
        matches = []
        for req_skill in required_skills:
            # Encode skills
            embeddings = model.encode([req_skill] + employee_skills)
            req_embedding = embeddings[0]
            
            # Compare with each employee skill
            for i, emp_skill in enumerate(employee_skills):
                similarity = cosine_similarity(
                    [req_embedding],
                    [embeddings[i+1]]  # +1 because first embedding is req_skill
                )[0][0]
                
                if similarity >= threshold:
                    matches.append({
                        'required_skill': req_skill,
                        'employee_skill': emp_skill,
                        'similarity': float(f"{similarity:.4f}")
                    })
        
        if matches:
            # Add employee with their matches
            matching_employees.append({
                'employee_id': employee['id'],
                'name': employee.get('name', 'Unknown'),
                'position': employee.get('position', 'Unknown'),
                'matches': matches
            })
    
    return matching_employees

# Find matches
results = find_matching_employees(employees, matched_skills)


if __name__ == '__main__':
    main()