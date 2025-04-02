from google import genai
from pydantic import BaseModel,Validator
from datetime import time
from typing import Dict, List, Literal
import requests




class Employee(BaseModel):
    Employee_id: int
    Skills: List[str]
    Shift: Dict[
        Literal["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        List[List[time]]  # Two lists, each containing two `time` objects
    ]
    Experience: float



    @validator("Shift", pre=True, each_item=True)
    def validate_shift(cls, shift):
        if not isinstance(shift, list) or len(shift) != 2:
            raise ValueError("Each day's shift must have exactly 2 time slots (2 lists).")
        for slot in shift:
            if not isinstance(slot, list) or len(slot) != 2:
                raise ValueError("Each time slot must contain exactly 2 time values (HH:MM:SS).")
        return shift
    
client = genai.Client(api_key="API_KEY")

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Create a list of employees with unique ID, a list of skills (each skill should be a single word, or separated by a hyphen if that is not possible), and shift(the starting time, and ending time, for each day, seven days a week), and the number of years they have in experience',
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[Employee],
        'candidate_count': 1500
    },

)

recipes_json = response.json()

with open('cookie_recipes.json', 'w') as f:
    f.write(recipes_json)



    


  
