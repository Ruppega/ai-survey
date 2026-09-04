import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY is not set in the .env file.")

client = genai.Client(api_key=api_key)

def generate(prompt):
    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response or not response.text:
        raise Exception("Gemini returned an empty response.")

    return response.text
