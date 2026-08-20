import os

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# GEMINI CLIENT
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception(
        "GEMINI_API_KEY is not set in the .env file."
    )

client = genai.Client(
    api_key=api_key
)


# =========================================================
# GENERATE RESPONSE
# =========================================================

def generate(prompt):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text