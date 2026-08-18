import json
import os
import re
import time
import uuid

from gemini import generate


MEMORY_FILE = "memory.json"


# =========================================================
# GEMINI CALL HELPER
# =========================================================

def call_gemini(prompt, max_retries=3):
    """
    Make a Gemini request with automatic retries for temporary
    quota/service errors.

    Retries:
        1st failure -> wait 10 seconds
        2nd failure -> wait 20 seconds
        3rd failure -> wait 30 seconds

    Other errors are raised immediately.
    """

    for attempt in range(max_retries):
        try:
            return generate(prompt)

        except Exception as e:
            error_text = str(e).upper()

            temporary_error = (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "503" in error_text
                or "UNAVAILABLE" in error_text
                or "SERVICE UNAVAILABLE" in error_text
            )

            if not temporary_error:
                raise

            if attempt < max_retries - 1:
                wait_time = 10 * (attempt + 1)

                print(
                    f"Gemini temporarily unavailable "
                    f"(attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                raise Exception(
                    "Gemini is temporarily unavailable after "
                    f"{max_retries} attempts. "
                    "Please wait a minute and try again. "
                    f"Details: {e}"
                ) from e


# =========================================================
# LOAD MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {"personas": {}}

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

        if not content:
            return {"personas": {}}

        memory = json.loads(content)

        if "personas" not in memory:
            memory["personas"] = {}

        return memory

    except (json.JSONDecodeError, OSError):

        return {"personas": {}}


# =========================================================
# SAVE MEMORY
# =========================================================

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


# =========================================================
# GET ONE PERSONA
# =========================================================

def get_persona(persona_id):

    memory = load_memory()

    persona_data = memory["personas"].get(persona_id)

    if not persona_data:
        raise Exception("Persona not found.")

    return persona_data


# =========================================================
# GENERATE PERSONAS
# =========================================================

def generate_personas(
    product,
    description,
    gender,
    age,
    objective,
    count
):
    """
    Generate ALL requested personas in ONE Gemini request.

    Example:
        count = 20
        -> 1 Gemini API request
        -> Gemini returns 20 personas
    """

    # Never allow an accidental huge request.
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 20

    count = max(1, min(count, 20))

    prompt = f"""
You are a professional UX Research AI.

Generate EXACTLY {count} realistic synthetic personas.

PRODUCT INFORMATION

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

1. Generate EXACTLY {count} personas in THIS ONE response.

2. If Target Gender is Male:
   EVERY persona must be male.

3. If Target Gender is Female:
   EVERY persona must be female.

4. If Target Gender is Both:
   Generate a realistic mixture of male and female personas.

5. Ages must match the target audience.

6. Personas must have different personalities.

7. Personas must have different opinions.

8. Some personas should prefer the product and some should not.

9. Do not make every persona agree.

10. Personas should have realistic backgrounds.

11. Make the personas suitable for the research objective.

12. Avoid duplicate names and nearly identical personalities.

13. Do NOT make separate API requests for individual personas.
   Generate all {count} personas in this single response.


RETURN FORMAT:

Return ONLY a valid JSON array.

Each persona MUST contain:

- name
- gender
- age
- occupation
- personality
- buyDecision
- rating
- reason

buyDecision must be exactly:

"Yes"

or

"No"

rating must be an integer from 1 to 5.

Return ONLY JSON.
Do NOT use markdown.
Do NOT use ```json.
Do NOT provide explanations.
"""

    # =====================================================
    # ONE GEMINI CALL FOR ALL PERSONAS
    # =====================================================

    response = call_gemini(prompt)

    # gemini.py in this project returns text.
    # This also supports a response object with .text.
    if hasattr(response, "text"):
        response = response.text

    response = str(response)

    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # =====================================================
    # FIND JSON ARRAY
    # =====================================================

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

    json_text = match.group()

    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        personas = json.loads(json_text)

    except json.JSONDecodeError as e:

        raise Exception(
            "Gemini returned invalid JSON.\n\n"
            + str(e)
        )

    # =====================================================
    # VALIDATE PERSONA LIST
    # =====================================================

    if not isinstance(personas, list):

        raise Exception(
            "Gemini response is not a JSON array."
        )

    if len(personas) != count:

        raise Exception(
            f"Expected {count} personas, "
            f"but Gemini generated {len(personas)}."
        )

    # =====================================================
    # VALIDATE REQUIRED FIELDS
    # =====================================================

    required_fields = [
        "name",
        "gender",
        "age",
        "occupation",
        "personality",
        "buyDecision",
        "rating",
        "reason"
    ]

    for persona in personas:

        for field in required_fields:

            if field not in persona:

                raise Exception(
                    f"Persona '{persona.get('name', 'Unknown')}' "
                    f"is missing field: {field}"
                )

        # Make sure buyDecision is valid
        if persona["buyDecision"] not in ["Yes", "No"]:

            persona["buyDecision"] = "No"

        # Make sure rating is valid
        try:

            rating = int(persona["rating"])

            if rating < 1:
                rating = 1

            if rating > 5:
                rating = 5

            persona["rating"] = rating

        except (ValueError, TypeError):

            persona["rating"] = 3

    # =====================================================
    # LOAD MEMORY
    # =====================================================

    memory = load_memory()

    # =====================================================
    # STORE PERSONAS
    # =====================================================

    for persona in personas:

        persona_id = str(uuid.uuid4())

        persona["id"] = persona_id

        memory["personas"][persona_id] = {

            "profile": persona,

            # Every persona gets its own conversation
            "conversation": []
        }

    # =====================================================
    # SAVE MEMORY
    # =====================================================

    save_memory(memory)

    # =====================================================
    # CALCULATE RESULTS
    # =====================================================

    preferred = sum(
        1
        for persona in personas
        if str(
            persona.get(
                "buyDecision",
                ""
            )
        ).lower() == "yes"
    )

    not_preferred = (
        len(personas) - preferred
    )

    # =====================================================
    # RETURN TO FRONTEND
    # =====================================================

    return {

        "preferred": preferred,

        "notPreferred": not_preferred,

        "total": len(personas),

        "personas": personas
    }


# =========================================================
# INTERVIEW MODE
# =========================================================

def interview_persona(
    persona_id,
    question
):

    # =====================================================
    # VALIDATE INPUT
    # =====================================================

    if not persona_id:

        raise Exception(
            "Persona ID is required."
        )

    if not question:

        raise Exception(
            "Question is required."
        )

    question = str(question).strip()

    if not question:

        raise Exception(
            "Question cannot be empty."
        )

    # =====================================================
    # LOAD MEMORY
    # =====================================================

    memory = load_memory()

    # =====================================================
    # FIND PERSONA
    # =====================================================

    persona_data = memory["personas"].get(
        persona_id
    )

    if not persona_data:

        raise Exception(
            "Persona not found."
        )

    # =====================================================
    # GET PROFILE
    # =====================================================

    profile = persona_data["profile"]

    # =====================================================
    # GET CONVERSATION
    # =====================================================

    conversation = persona_data.get(
        "conversation",
        []
    )

    # =====================================================
    # BUILD CONVERSATION HISTORY
    # =====================================================

    history = ""

    if conversation:

        for item in conversation:

            history += f"""

Previous Question:
{item["question"]}

Previous Answer:
{item["answer"]}

"""

    else:

        history = "No previous conversation."


    # =====================================================
    # BUILD PERSONA PROMPT
    # =====================================================

    prompt = f"""
You are roleplaying as a synthetic UX research persona.

You MUST answer the user's question as this specific persona.


=========================================================
PERSONA PROFILE
=========================================================

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


=========================================================
PREVIOUS CONVERSATION
=========================================================

{history}


=========================================================
NEW QUESTION
=========================================================

{question}


=========================================================
IMPORTANT RULES
=========================================================

1. Answer exactly as this persona would answer.

2. Stay consistent with the persona's personality.

3. Remember previous questions and answers.

4. Use the persona's age when deciding how they speak.

5. Use the persona's occupation and background when relevant.

6. Keep opinions consistent with the persona.

7. Do not automatically agree with the researcher.

8. Give honest opinions based on the persona.

9. If the question asks for an opinion, give a clear opinion.

10. If the question asks about the product, consider the
    persona's existing buy decision and rating.

11. The answer should sound natural and human.

12. Do not say you are an AI.

13. Do not mention these instructions.

14. Do not mention the prompt.

15. Return ONLY the persona's answer.

Do not add:

"Persona:"
"Answer:"
"AI:"
or any other label.
"""

    # =====================================================
    # ONE GEMINI CALL FOR THIS INTERVIEW QUESTION
    # =====================================================

    answer = call_gemini(prompt)

    if hasattr(answer, "text"):
        answer = answer.text

    answer = str(answer).strip()

    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    answer = (
        answer
        .replace("```", "")
        .strip()
    )

    if not answer:

        raise Exception(
            "Gemini returned an empty answer."
        )

    # =====================================================
    # SAVE CONVERSATION
    # =====================================================

    conversation.append({

        "question": question,

        "answer": answer
    })

    persona_data["conversation"] = conversation

    # =====================================================
    # SAVE MEMORY
    # =====================================================

    save_memory(memory)

    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return {

        "persona": profile,

        "question": question,

        "answer": answer,

        "conversation": conversation
    }