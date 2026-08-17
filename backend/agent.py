import json
import os
import re
import uuid

from gemini import generate


MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"personas": {}}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


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
- If Target Gender is Both, generate a realistic mix of male and female.
- Ages must match the target audience.
- Personas must have different personalities and opinions.
- Some personas may prefer the product and some may not.

Return ONLY a valid JSON array.

Each persona must contain:

- name
- gender
- age
- occupation
- personality
- buyDecision
- rating
- reason

buyDecision must be exactly "Yes" or "No".

rating must be an integer from 1 to 5.

Return ONLY JSON.
No markdown.
No explanation.
No ```json.
"""

    response = generate(prompt)

    # Remove markdown if Gemini returns it
    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # Find JSON array
    match = re.search(r"\[.*\]", response, re.DOTALL)

    if not match:
        raise Exception(
            "Gemini did not return valid JSON.\n\n" + response
        )

    personas = json.loads(match.group())

    # Check count
    if len(personas) != count:
        raise Exception(
            f"Expected {count} personas, "
            f"but Gemini generated {len(personas)}."
        )

    # Load existing memory
    memory = load_memory()

    # Add every persona to memory
    for persona in personas:

        persona_id = str(uuid.uuid4())

        persona["id"] = persona_id

        memory["personas"][persona_id] = {
            "profile": persona,
            "conversation": []
        }

    # Save memory
    save_memory(memory)

    # Calculate preference
    yes = sum(
        1
        for persona in personas
        if str(persona.get("buyDecision", "")).lower() == "yes"
    )

    return {
        "preferred": yes,
        "notPreferred": len(personas) - yes,
        "total": len(personas),
        "personas": personas
    }