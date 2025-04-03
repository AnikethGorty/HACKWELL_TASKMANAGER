import json
from datetime import datetime, time, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import os

# Initialize model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Skills database
skillset = [
    "Welding", "PLC-Programming", "Hydraulics", "Electrical", "Pneumatics",
    "CNC-Operation", "Machining", "Fabrication", "Automation", "Instrumentation",
    "HVAC", "Blueprint-Reading", "3D-Printing", "Quality-Control", "Robotics",
    "Laser-Cutting", "Carpentry", "Soldering", "Networking", "Motor-Repair"
]

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
        
        task_embedding = model.encode([task_skill])[0]
        
        for skill in skillset:
            skill_embedding = model.encode([skill])[0]
            similarity = cosine_similarity([task_embedding], [skill_embedding])[0][0]
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = skill
        
        if best_match and highest_similarity > 0.6:
            matched_skills.append({
                'input_skill': task_skill,
                'matched_skill': best_match,
                'similarity': float(f"{highest_similarity:.4f}")
            })
    
    return matched_skills

def load_employees(employees_file):
    """Load employee data from JSON file"""
    try:
        with open(employees_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {employees_file}: {e}")
        return []

def calculate_daily_time_windows(start_time_str, end_time_str):
    """Calculate exact time windows for each day a task spans"""
    try:
        start_time = datetime.strptime(start_time_str, "%Y:%m:%d:%H:%M")
        end_time = datetime.strptime(end_time_str, "%Y:%m:%d:%H:%M")
        
        if start_time >= end_time:
            return []

        time_windows = []
        current_day = start_time
        
        while current_day.date() <= end_time.date():
            day_name = current_day.strftime('%A').lower()
            day_date = current_day.strftime('%Y-%m-%d')
            
            day_start = max(current_day, datetime.combine(current_day.date(), time.min))
            day_end = min(
                end_time,
                datetime.combine(current_day.date(), time(23, 59, 59)))
            
            time_windows.append({
                'day_name': day_name,
                'day_date': day_date,
                'start_time': day_start.time().strftime('%H:%M'),
                'end_time': day_end.time().strftime('%H:%M'),
                'duration_hours': round((day_end - day_start).total_seconds() / 3600, 2)
            })
            
            current_day = datetime.combine(current_day.date() + timedelta(days=1), time.min)
        
        return time_windows
    except ValueError as e:
        print(f"Invalid time format: {e}")
        return []

def check_employee_availability(employee, time_windows):
    """Check if employee is available during required time windows"""
    unavailable_periods = []
    total_available_hours = 0
    
    for window in time_windows:
        day = window['day_name']
        shift_in_key = f"{day}_in"
        shift_out_key = f"{day}_out"
        
        # Check if shift exists for this day
        if shift_in_key not in employee['shifts'] or shift_out_key not in employee['shifts']:
            unavailable_periods.append({
                'day': day,
                'reason': 'No shift scheduled'
            })
            continue
            
        shift_in = employee['shifts'][shift_in_key]
        shift_out = employee['shifts'][shift_out_key]
        
        # Skip if shift times are null
        if shift_in is None or shift_out is None:
            unavailable_periods.append({
                'day': day,
                'reason': 'No shift scheduled'
            })
            continue
        
        try:
            # Parse times (handle 24:48 as 00:48 next day)
            def parse_time(time_str):
                if time_str == '24:00' or time_str == '24:48':  # Handle special cases
                    return datetime.strptime('23:59', '%H:%M').time()
                return datetime.strptime(time_str, '%H:%M').time()
            
            shift_start = parse_time(shift_in)
            shift_end = parse_time(shift_out)
            task_start = datetime.strptime(window['start_time'], '%H:%M').time()
            task_end = datetime.strptime(window['end_time'], '%H:%M').time()
            
            # Only unavailable if ENTIRE shift is before OR after task window
            if (shift_end < task_start) or (shift_start > task_end):
                unavailable_periods.append({
                    'day': day,
                    'reason': 'Shift completely outside task window',
                    'shift_hours': f"{shift_in}-{shift_out}",
                    'task_hours': f"{window['start_time']}-{window['end_time']}"
                })
            else:
                # Calculate overlapping hours
                overlap_start = max(shift_start, task_start)
                overlap_end = min(shift_end, task_end)
                overlap_hours = (datetime.combine(datetime.today(), overlap_end) - 
                               datetime.combine(datetime.today(), overlap_start)).total_seconds() / 3600
                total_available_hours += max(0, overlap_hours)
                
        except ValueError as e:
            unavailable_periods.append({
                'day': day,
                'reason': f'Invalid time format: {str(e)}'
            })
    
    return {
        'is_available': len(unavailable_periods) == 0,
        'unavailable_periods': unavailable_periods if unavailable_periods else None,
        'total_available_hours': round(total_available_hours, 2)
    }    
    
    """Check if employee is available during required time windows"""
    unavailable_periods = []
    total_available_hours = 0
    
    for window in time_windows:
        day = window['day_name']
        shift = employee['shifts'].get(day, {})
        
        # Skip if no shift scheduled
        if not shift.get('in') or not shift.get('out'):
            unavailable_periods.append({
                'day': day,
                'reason': 'No shift scheduled'
            })
            continue
        
        try:
            shift_start = datetime.strptime(shift['in'], '%H:%M').time()
            shift_end = datetime.strptime(shift['out'], '%H:%M').time()
            task_start = datetime.strptime(window['start_time'], '%H:%M').time()
            task_end = datetime.strptime(window['end_time'], '%H:%M').time()
            
            # Only unavailable if ENTIRE shift is before OR after task window
            if (shift_end < task_start) or (shift_start > task_end):
                unavailable_periods.append({
                    'day': day,
                    'reason': 'Shift completely outside task window',
                    'shift_hours': f"{shift['in']}-{shift['out']}",
                    'task_hours': f"{window['start_time']}-{window['end_time']}"
                })
            else:
                # Calculate overlapping hours
                overlap_start = max(shift_start, task_start)
                overlap_end = min(shift_end, task_end)
                overlap_hours = (datetime.combine(datetime.today(), overlap_end) - 
                               datetime.combine(datetime.today(), overlap_start)).total_seconds() / 3600
                total_available_hours += max(0, overlap_hours)
                
        except ValueError:
            unavailable_periods.append({
                'day': day,
                'reason': 'Invalid time format'
            })
    
    return {
        'is_available': len(unavailable_periods) == 0,
        'unavailable_periods': unavailable_periods if unavailable_periods else None,
        'total_available_hours': round(total_available_hours, 2)
    }
    """Check if employee is available during required time windows"""
    unavailable_periods = []
    total_available_hours = 0
    
    for window in time_windows:
        day = window['day_name']
        shift = employee['shifts'].get(day, {})
        
        if not shift.get('in') or not shift.get('out'):
            unavailable_periods.append({
                'day': day,
                'reason': 'No shift scheduled'
            })
            continue
        
        try:
            shift_start = datetime.strptime(shift['in'], '%H:%M').time()
            shift_end = datetime.strptime(shift['out'], '%H:%M').time()
            task_start = datetime.strptime(window['start_time'], '%H:%M').time()
            task_end = datetime.strptime(window['end_time'], '%H:%M').time()
            
            if task_start >= shift_start and task_end <= shift_end:
                total_available_hours += window['duration_hours']
            else:
                unavailable_periods.append({
                    'day': day,
                    'required': f"{window['start_time']}-{window['end_time']}",
                    'available': f"{shift['in']}-{shift['out']}",
                    'reason': 'Outside shift hours'
                })
        except ValueError:
            unavailable_periods.append({
                'day': day,
                'reason': 'Invalid time format'
            })
    
    return {
        'is_available': len(unavailable_periods) == 0,
        'unavailable_periods': unavailable_periods if unavailable_periods else None,
        'total_available_hours': total_available_hours
    }

def main():
    # Load and clear tasks
    tasks = load_and_clear_tasks()
    if not tasks:
        print("No tasks found in tasks.json")
        return

    # Load employees data
    employees = load_employees('employees_data.json')
    if not employees:
        print("No employees data loaded")
        return

    all_results = []
    
    for task in tasks:
        if not task.get('skillsRequired'):
            continue
            
        print(f"\nProcessing Task {task.get('id')}: {task.get('taskName')}")
        
        # Match skills to skillset
        matched_skills = match_to_skillset(task['skillsRequired'])
        if not matched_skills:
            print("No matching skills found in skillset")
            continue
        
        required_skills = [m['matched_skill'] for m in matched_skills]
        
        # Calculate task time windows
        time_windows = calculate_daily_time_windows(
            task['startTime'], 
            task['endTime']
        )
        if not time_windows:
            print("Invalid task time range")
            continue
        
        # Find matching employees
        matching_employees = []
        for employee in employees:
            employee_skills = employee.get('skills', {})
            common_skills = {
                skill: prof for skill, prof in employee_skills.items()
                if skill in required_skills and prof >= 5
            }
            
            if common_skills:
                availability = check_employee_availability(employee, time_windows)
                matching_employees.append({
                    'employee_id': employee['employee_id'],
                    'skills': employee_skills,
                    'matched_skills': common_skills,
                    'shifts': employee['shifts'],
                    'availability': availability
                })
        
        # Sort by availability and proficiency
        matching_employees.sort(
            key=lambda x: (
                x['availability']['is_available'],
                sum(x['matched_skills'].values()),
                x['availability']['total_available_hours']
            ),
            reverse=True
        )
        
        # Store results
        task_result = {
            'task_id': task.get('id'),
            'task_name': task.get('taskName'),
            'time_windows': time_windows,
            'required_skills': required_skills,
            'matching_employees': matching_employees,
            'best_candidates': [
                emp for emp in matching_employees 
                if emp['availability']['is_available']
            ][:3]  # Top 3 available candidates
        }
        all_results.append(task_result)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'task_allocations_{timestamp}.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nAllocation complete. Results saved to {output_file}")

if __name__ == '__main__':
    main()