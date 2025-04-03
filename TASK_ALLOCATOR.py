import json
from datetime import timedelta
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

def get_latest_tasks():
    """Retrieve tasks from the shared JSON file"""
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
            return tasks
    except (FileNotFoundError, json.JSONDecodeError):
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
    # Load tasks and extract skills
    tasks = get_latest_tasks()
    required_skills = extract_required_skills(tasks)
    
    print(f"\nFound {len(required_skills)} unique skills in tasks:")
    print(", ".join(required_skills))
    
    # Find similar skills
    if required_skills:
        print("\nMatching skills to skillset:")
        matches = find_most_similar_skills(required_skills)
        for match in matches:
            print(f"Input: {match['input_skill']:20} | Match: {match['matched_skill']:20} | Score: {match['similarity_score']:.4f}")
    
    # Time analysis example
    print("\nTime Analysis:")
    start_time = "2023:12:01:09:00"  # Example from tasks
    end_time = "2023:12:02:17:30"    # Example from tasks
    
    duration = calculate_duration(start_time, end_time)
    if duration:
        print(f"Duration between {start_time} and {end_time}:")
        print(f"{duration['days']} days, {duration['hours']} hours, {duration['minutes']} minutes")
        print(f"Total: {duration['total_hours']:.2f} hours")

if __name__ == '__main__':
    main()