import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import os
from datetime import datetime,time,timedelta

# Initialize model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Skills database
skillset = [
    "Welding", "PLC-Programming", "Hydraulics", "Electrical", "Pneumatics",
    "CNC-Operation", "Machining", "Fabrication", "Automation", "Instrumentation",
    "HVAC", "Blueprint-Reading", "3D-Printing", "Quality-Control", "Robotics",
    "Laser-Cutting", "Carpentry", "Soldering", "Networking", "Motor-Repair"
]

def calculate_daily_time_windows(start_time_str, end_time_str):
    """
    Calculate exact time windows for each day a task spans
    Returns: List of tuples (day_name, day_date, start_time, end_time)
    """
    try:
        # Parse input times
        start_time = datetime.strptime(start_time_str, "%Y:%m:%d:%H:%M")
        end_time = datetime.strptime(end_time_str, "%Y:%m:%d:%H:%M")
        
        if start_time >= end_time:
            return []

        time_windows = []
        current_day = start_time.date()
        
        while current_day <= end_time.date():
            day_name = current_day.strftime('%A').lower()
            day_date = current_day.strftime('%Y-%m-%d')
            
            # Calculate day boundaries
            day_start = datetime.combine(current_day, time.min)
            day_end = datetime.combine(current_day, time.max)
            
            # Determine actual window for this day
            window_start = max(start_time, day_start)
            window_end = min(end_time, day_end)
            
            time_windows.append({
                'day_name': day_name,
                'day_date': day_date,
                'start_time': window_start.time().strftime('%H:%M'),
                'end_time': window_end.time().strftime('%H:%M'),
                'duration_hours': (window_end - window_start).total_seconds() / 3600
            })
            
            current_day += timedelta(days=1)
        
        return time_windows
    
    except ValueError as e:
        print(f"Invalid time format: {e}")
        return []

def check_employee_availability(employee_shifts, time_windows):
    """
    Check if employee is available during all required time windows
    Returns: (is_available, unavailable_periods)
    """
    unavailable_periods = []
    
    for window in time_windows:
        day = window['day_name']
        shift = employee_shifts.get(day, {})
        
        # Employee has no shift this day
        if not shift.get('in') or not shift.get('out'):
            unavailable_periods.append({
                'day': day,
                'reason': 'No shift scheduled'
            })
            continue
        
        # Parse shift times
        try:
            shift_start = datetime.strptime(shift['in'], '%H:%M').time()
            shift_end = datetime.strptime(shift['out'], '%H:%M').time()
            task_start = datetime.strptime(window['start_time'], '%H:%M').time()
            task_end = datetime.strptime(window['end_time'], '%H:%M').time()
        except ValueError:
            unavailable_periods.append({
                'day': day,
                'reason': 'Invalid time format'
            })
            continue
        
        # Check if task window fits within shift
        if task_start < shift_start or task_end > shift_end:
            unavailable_periods.append({
                'day': day,
                'required': f"{window['start_time']}-{window['end_time']}",
                'available': f"{shift['in']}-{shift['out']}",
                'reason': 'Outside shift hours'
            })
    
    return (len(unavailable_periods) == 0, unavailable_periods)

# Example usage in your main function:
task_windows = calculate_daily_time_windows("2025:04:13:12:30", "2025:04:14:04:30")
# Returns:
# [
#   {'day_name': 'sunday', 'day_date': '2025-04-13', 'start_time': '12:30', 'end_time': '23:59', 'duration_hours': 11.5},
#   {'day_name': 'monday', 'day_date': '2025-04-14', 'start_time': '00:00', 'end_time': '04:30', 'duration_hours': 4.5}
# ]

# Then when checking employees:
for employee in matching_employees:
    is_available, conflicts = check_employee_availability(employee['shifts'], task_windows)
    employee['availability'] = {
        'is_available': is_available,
        'conflicts': conflicts if not is_available else None,
        'total_available_hours': sum(w['duration_hours'] for w in task_windows) if is_available else 0
    }


def load_and_clear_tasks():
    """Load tasks from JSON file and clear it"""
    try:
        if not os.path.exists('tasks.json') or os.path.getsize('tasks.json') == 0:
            return []
            
        with open('tasks.json', 'r') as f:
            tasks = json.load(f)
            
        with open('tasks.json', 'w') as f:
            json.dump([], f)
            
        return tasks if isinstance(tasks, list) else []
    except Exception as e:
        print(f"Error loading/clearing tasks: {e}")
        return []

def match_to_skillset(task_skills):
    """Match task skills to predefined skillset"""
    matched_skills = []
    
    for task_skill in task_skills:
        highest_similarity = 0
        best_match = None
        
        # Encode task skill once
        task_embedding = model.encode([task_skill])[0]
        
        # Compare with all skills in skillset
        for skill in skillset:
            skill_embedding = model.encode([skill])[0]
            similarity = cosine_similarity([task_embedding], [skill_embedding])[0][0]
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = skill
        
        if best_match and highest_similarity > 0.6:  # Threshold
            matched_skills.append({
                'input_skill': task_skill,
                'matched_skill': best_match,
                'similarity': float(f"{highest_similarity:.4f}")
            })
    
    return matched_skills

def find_employees_with_skills(employees_file, required_skills):
    """Find employees with matching skills including shift data"""
    try:
        with open(employees_file) as f:
            employees = json.load(f)
    except Exception as e:
        print(f"Error loading {employees_file}: {e}")
        return []

    matching_employees = []
    
    for employee in tqdm(employees, desc="Searching employees"):
        employee_skills = employee.get('skills', {})
        if not employee_skills:
            continue
        
        # Check if employee has any required skills with proficiency >= 5
        common_skills = {
            skill: proficiency 
            for skill, proficiency in employee_skills.items() 
            if skill in required_skills and proficiency >= 5
        }
        
        if common_skills:
            # Format shifts data
            shifts = employee.get('shifts', {})
            formatted_shifts = {}
            
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 
                       'friday', 'saturday', 'sunday']:
                in_key = f"{day}_in"
                out_key = f"{day}_out"
                formatted_shifts[day] = {
                    'in': shifts.get(in_key),
                    'out': shifts.get(out_key)
                }
            
            matching_employees.append({
                'employee_id': employee.get('employee_id'),
                'skills': employee_skills,
                'matched_skills': common_skills,
                'shifts': formatted_shifts,
                'average_proficiency': sum(common_skills.values()) / len(common_skills)
            })
    
    # Sort by average proficiency (highest first)
    matching_employees.sort(key=lambda x: x['average_proficiency'], reverse=True)
    
    return matching_employees

def main():
    # Step 1: Load and clear tasks
    tasks = load_and_clear_tasks()
    if not tasks:
        print("No tasks found in tasks.json")
        return

    all_results = []
    
    for task in tasks:
        # Step 2: Get skills from task
        task_skills = task.get('skillsRequired', [])
        if not task_skills:
            continue
            
        print(f"\nProcessing Task {task.get('id')}: {task.get('taskName')}")
        print(f"Original Skills: {', '.join(task_skills)}")
        
        # Step 3 & 4: Match to skillset
        matched_skills = match_to_skillset(task_skills)
        if not matched_skills:
            print("No matching skills found in skillset")
            continue
            
        # Extract just the matched skill names
        required_skills = [match['matched_skill'] for match in matched_skills]
        print(f"Matched Skills: {', '.join(required_skills)}")
        
        # Step 5: Find employees with these skills
        matching_employees = find_employees_with_skills('employees_data.json', required_skills)
        
        # Store results
        task_result = {
            'task_id': task.get('id'),
            'task_name': task.get('taskName'),
            'start_time': task.get('startTime'),
            'end_time': task.get('endTime'),
            'original_skills': task_skills,
            'skill_matches': matched_skills,
            'matching_employees': matching_employees,
            'match_count': len(matching_employees)
        }
        all_results.append(task_result)
        
        print(f"Found {len(matching_employees)} matching employees")
    
    # Save complete results with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'task_allocations_{timestamp}.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nAll results saved to {output_file}")

if __name__ == '__main__':
    main()