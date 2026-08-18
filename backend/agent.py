import json
import os
import re
import uuid

from gemini import generate


MEMORY_FILE = "memory.json"


# ---------------------------------------------------------
# LOAD MEMORY
# ---------------------------------------------------------

def load_memory():

    # If memory.json does not exist
    if not os.path.exists(MEMORY_FILE):
        return {"personas": {}}

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

        # If memory.json is empty
        if not content:
            return {"personas": {}}

        memory = json.loads(content)

        # Make sure the required structure exists
        if "personas" not in memory:
            memory["personas"] = {}

        return memory

    except (json.JSONDecodeError, OSError):

        # If memory.json is corrupted,
        # start with empty memory
        return {"personas": {}}


# ---------------------------------------------------------
# SAVE MEMORY
# ---------------------------------------------------------

def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=2,
            ensure_ascii=False
        )


# ---------------------------------------------------------
# GET ONE PERSONA FROM MEMORY
# ---------------------------------------------------------

def get_persona(persona_id):

    memory = load_memory()

    persona_data = memory["personas"].get(persona_id)

    if not persona_data:
        raise Exception("Persona not found.")

    return persona_data


# ---------------------------------------------------------
# GENERATE PERSONAS
# ---------------------------------------------------------

def generate_personas(
    product,
    description,
    gender,
    age,
    objective,
    count
):

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
- Personas must have realistic backgrounds.
- Do not make every persona agree.

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

buyDecision must be exactly:
"Yes" or "No"

rating must be an integer from 1 to 5.

Return ONLY JSON.
No markdown.
No explanation.
No ```json.
"""

    # -----------------------------------------------------
    # CALL GEMINI
    # -----------------------------------------------------

    response = generate(prompt)

    # Remove markdown if Gemini returns it
    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # -----------------------------------------------------
    # FIND JSON ARRAY
    # -----------------------------------------------------

    match = re.search(
        r"\[.*\]",
        response,
        re.DOTALL
    )

    if not match:

        raise Exception(
            "Gemini did not return valid JSON.\n\n"
            + response
        )

    # -----------------------------------------------------
    # CONVERT JSON STRING TO PYTHON
    # -----------------------------------------------------

    try:

        personas = json.loads(
            match.group()
        )

    except json.JSONDecodeError as e:

        raise Exception(
            "Gemini returned invalid JSON.\n\n"
            + str(e)
        )

    # -----------------------------------------------------
    # CHECK PERSONA COUNT
    # -----------------------------------------------------

    if len(personas) != count:

        raise Exception(
            f"Expected {count} personas, "
            f"but Gemini generated {len(personas)}."
        )

    # -----------------------------------------------------
    # LOAD EXISTING MEMORY
    # -----------------------------------------------------

    memory = load_memory()

    # -----------------------------------------------------
    # STORE PERSONAS
    # -----------------------------------------------------

    for persona in personas:

        # Generate unique ID
        persona_id = str(
            uuid.uuid4()
        )

        # Add ID to persona
        persona["id"] = persona_id

        # Save persona and empty conversation
        memory["personas"][persona_id] = {

            "profile": persona,

            "conversation": []
        }

    # -----------------------------------------------------
    # SAVE MEMORY
    # -----------------------------------------------------

    save_memory(memory)

    # -----------------------------------------------------
    # CALCULATE PREFERENCE
    # -----------------------------------------------------

    yes = sum(
        1
        for persona in personas
        if str(
            persona.get(
                "buyDecision",
                ""
            )
        ).lower() == "yes"
    )

    # -----------------------------------------------------
    # RETURN RESULT TO FRONTEND
    # -----------------------------------------------------

    return {

        "preferred": yes,

        "notPreferred":
            len(personas) - yes,

        "total":
            len(personas),

        "personas":
            personas
    }
# ---------------------------------------------------------
# INTERVIEW MODE
# ---------------------------------------------------------

def interview_persona(persona_id, question):

    # Load memory
    memory = load_memory()

    # Find persona
    persona_data = memory["personas"].get(persona_id)

    if not persona_data:
        raise Exception("Persona not found.")

    # Get persona profile
    profile = persona_data["profile"]

    # Get previous conversation
    conversation = persona_data["conversation"]

    # Build previous conversation text
    history = ""

    for item in conversation:

        history += f"""
Previous Question:
{item["question"]}

Previous Answer:
{item["answer"]}
"""

    # -----------------------------------------------------
    # GEMINI PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are roleplaying as a synthetic UX research persona.

PERSONA PROFILE:

Name:
{profile.get("name")}

Gender:
{profile.get("gender")}

Age:
{profile.get("age")}

Occupation:
{profile.get("occupation")}

Personality:
{profile.get("personality")}

Buy Decision:
{profile.get("buyDecision")}

Rating:
{profile.get("rating")}

Reason:
{profile.get("reason")}


PREVIOUS CONVERSATION:

{history}


NEW QUESTION:

{question}


IMPORTANT RULES:

1. Answer exactly as this persona would answer.
2. Remember the previous conversation.
3. Keep the persona's personality consistent.
4. Do not contradict their established opinions without a
   realistic reason.
5. Use their age, occupation and personality when answering.
6. Give a natural human-like answer.
7. Do not say you are an AI.
8. Do not mention these instructions.

Return ONLY the answer.
"""

    # -----------------------------------------------------
    # GET GEMINI RESPONSE
    # -----------------------------------------------------

    answer = generate(prompt).strip()

    # -----------------------------------------------------
    # SAVE CONVERSATION TO MEMORY
    # -----------------------------------------------------

    conversation.append({
        "question": question,
        "answer": answer
    })

    # Save updated memory
    save_memory(memory)

    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {
        "persona": profile,
        "question": question,
        "answer": answer,
        "conversation": conversation
    }