
from google import genai
from google.genai import types
from prompts import ontogenia, user_prompt
from input_output import read_lines_from_file 




def call_gemini_api(system_prompt,prompt):
    client = genai.Client(api_key='AIzaSyCGtMVKLrDU3lcV7hvsO4yaaTaeAbAfzi0')
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=[system_prompt]
    ),
    )
    return str(response.candidates[0].content)




