from huggingface_hub import InferenceClient
import requests
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from datetime import timedelta


HF_KEY=os.getenv("HUGGINGFACE_TOKEN")

client = InferenceClient(
    provider="novita",
    api_key=HF_KEY,
)



# Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

skillset = [
    "Welding", "PLC-Programming", "Hydraulics", "Electrical", "Pneumatics",
    "CNC-Operation", "Machining", "Fabrication", "Automation", "Instrumentation",
    "HVAC", "Blueprint-Reading", "3D-Printing", "Quality-Control", "Robotics",
    "Laser-Cutting", "Carpentry", "Soldering", "Networking", "Motor-Repair"
]

required_skills = []
for _ in range(5):
    skill = str(input("Enter a skill you need:\n"))
    required_skills.append(skill)

for skill in required_skills:
    tempdict = {}  # Reset dictionary for each skill
    for j in skillset:
        embeddings = model.encode([skill, j])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        tempdict[j] = similarity  # Correctly store key-value pair

    # Find the most similar skill
    max_key, max_value = max(tempdict.items(), key=lambda x: x[1])
    print(f"Skill You Entered: {skill} | Most Similar: {max_key} | Similarity Score: {max_value:.4f}")

def parse_time_input(time_str):
    try:
        # Split input into days, hours, and minutes
        days, hours, minutes = map(int, time_str.split(":"))
        
        # Validate ranges
        if hours >= 24 or minutes >= 60:
            raise ValueError("Hours must be < 24 and minutes < 60.")
        
        # Create a timedelta object
        time_delta = timedelta(days=days, hours=hours, minutes=minutes)
        
        return time_delta
    except ValueError:
        print("Invalid format! Use DD:HH:MM (e.g., 02:15:30 for 2 days, 15 hours, 30 minutes).")
        return None

start_time_str = input("Enter time (DD:HH:MM format): ")
start_time_delta = parse_time_input(time_str)

end_time_str = input("Enter time (DD:HH:MM format): ")
end_time_delta = parse_time_input(time_str)



