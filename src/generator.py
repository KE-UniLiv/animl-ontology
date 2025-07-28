
from google import genai
from google.genai import types
#from prompts import ontogenia, user_prompt
#from src.input_output import read_lines_from_file 
import re

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
api_key = os.getenv("API_KEY")



def call_generator(prompt, system_prompt, model):
    if model == 'gemini':
        return call_gemini_api(system_prompt, prompt)

def call_gemini_api(system_prompt,prompt):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=[system_prompt],
        temperature = 0.0
    ),
    )
    return response.text

print(call_gemini_api('bruh','rigged'))





