
from google import genai
from google.genai import types
from openai import OpenAI
import time
#from prompts import ontogenia, user_prompt
#from src.input_output import read_lines_from_file 
import re

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
api_key = os.getenv("GEMINI_API_KEY")



def call_generator(model,prompt,system_prompt='this is deliberately left blank, ignore',n=1,temperature=0):
    if model == 'gemini':
        return call_gemini_api(prompt,system_prompt,n,temperature)
    if model == 'gpt':
        return call_openai_api(prompt,system_prompt,n,temperature)

def call_gemini_api(prompt,system_prompt,n=1,temperature=0):
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=[system_prompt],
            temperature = temperature
        ),
        )
        print(response.text)
        return response.text
    except Exception as e:
        print(f'gpt returned this error: {e}')
        time.sleep(20)
        return call_gemini_api(prompt,system_prompt,n,temperature)

def call_openai_api(prompt,system_prompt,n=1,temperature=0):
    try:
        result = OpenAI(api_key = os.getenv("OPENAI_API_KEY")).chat.completions.create(model='gpt-4o-mini',messages=[
        {
            "role": "system",
            "content": [
                {"type": "text", "text": str(system_prompt)}
            ]
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": str(prompt)}
            ]
        }
        ]
        ,n=n,temperature=temperature)
        return result
    except Exception as e:
        print(f'gpt returned this error: {e}')
        time.sleep(20)
        return call_openai_api(prompt,system_prompt,n,temperature)






