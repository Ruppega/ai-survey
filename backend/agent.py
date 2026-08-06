import json
import re
from gemini import generate


def generate_personas(product, description, gender, age, objective, count):

    prompt = f"""
You are a professional UX Research AI.

Generate EXACTLY {count} realistic synthetic personas.

Product Name:
{product}

Description:
{description}

Target Gender:
{gender}

Target Audience Age:
{age}

Research Objective:
{objective}

IMPORTANT RULES:
- If Target Gender is Male, EVERY persona must be male.
- If Target Gender is Female, EVERY persona must be female.
- If Target Gender is Both, generate a realistic mix of male and female personas.
- Do NOT violate the requested gender.
- Ages should match the target audience.

Return ONLY a valid JSON array.

Each persona must contain:

- name
- gender
- age
- occupation
- personality
- buyDecision ("Yes" or "No")
- rating (1-5)
- reason

Rules:
- Return ONLY JSON.
- No markdown.
- No explanation.
- No ```json.
"""

    response = generate(prompt)

    # Remove markdown if Gemini accidentally returns it
    response = response.replace("```json", "").replace("```", "").strip()

    # Extract JSON array
    match = re.search(r"\[.*\]", response, re.DOTALL)

    if not match:
        raise Exception("Gemini did not return valid JSON.\n\n" + response)

    personas = json.loads(match.group())

    yes = sum(
        1
        for persona in personas
        if persona["buyDecision"].lower() == "yes"
    )

    return {
        "preferred": yes,
        "notPreferred": len(personas) - yes,
        "total": len(personas),
        "personas": personas,
    }