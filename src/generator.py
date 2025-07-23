
from google import genai
from google.genai import types
from prompts import ontogenia, user_prompt
from src.input_output import read_lines_from_file 
import re


def call_generator(prompt, system_prompt, model):
    if model == 'gemini':
        return call_gemini_api(system_prompt, prompt)

def call_gemini_api(system_prompt,prompt):
    client = genai.Client(api_key='AIzaSyCGtMVKLrDU3lcV7hvsO4yaaTaeAbAfzi0')
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=[system_prompt]
    ),
    )
    return response.text





