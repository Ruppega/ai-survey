import json
import os
import re
import time
import uuid

from gemini import generate

MEMORY_FILE = "memory.json"


# =========================================================
# GEMINI HELPER
# =========================================================

def call_gemini(prompt, max_retries=3):
    """Call Gemini with retry handling for temporary errors."""
    for attempt in range(max_retries):
        try:
            return generate(prompt)

        except Exception as e:
            error_text = str(e).upper()

            temporary_error = any(
                code in error_text
                for code in (
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "503",
                    "UNAVAILABLE",
                    "SERVICE UNAVAILABLE",
                )
            )

            if not temporary_error:
                raise

            if attempt < max_retries - 1:
                wait_time = 10 * (attempt + 1)
                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
            else:
                raise Exception(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                ) from e


# =========================================================
# MEMORY
# =========================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"personas": {}}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            return {"personas": {}}

        memory = json.loads(content)

        if "personas" not in memory:
            memory["personas"] = {}

        return memory

    except (json.JSONDecodeError, OSError):
        return {"personas": {}}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            memory,
            f,
            indent=2,
            ensure_ascii=False
        )


def get_persona(persona_id):
    memory = load_memory()
    persona_data = memory["personas"].get(persona_id)

    if not persona_data:
        raise Exception("Persona not found.")

    return persona_data


# =========================================================
# JSON CLEANING
# =========================================================

def parse_json_response(response):
    if hasattr(response, "text"):
        response = response.text

    response = str(response).strip()
    response = response.replace("```json", "").replace("```", "").strip()

    # First try the complete response.
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Fallback: find an object or array.
    array_match = re.search(r"\[.*\]", response, re.DOTALL)
    if array_match:
        return json.loads(array_match.group())

    object_match = re.search(r"\{.*\}", response, re.DOTALL)
    if object_match:
        return json.loads(object_match.group())

    raise Exception("Gemini did not return valid JSON.")


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
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 20

    count = max(1, min(count, 20))

    prompt = f"""
You are a professional UX Research AI.

Generate EXACTLY {count} realistic synthetic personas.

PRODUCT
Product Name: {product}
Description: {description}

TARGET
Gender: {gender}
Age: {age}

RESEARCH OBJECTIVE
{objective}

RULES:
1. Generate exactly {count} personas.
2. Follow the target gender.
3. Keep ages within the target audience.
4. Give every persona a different personality.
5. Give every persona a realistic occupation/background.
6. Do not make everyone agree.
7. Some personas may prefer the product and some may not.
8. Make opinions realistic for the research objective.
9. Avoid duplicate names.
10. Return ONLY valid JSON.

Each persona must contain:
name, gender, age, occupation, personality,
buyDecision, rating, reason

buyDecision must be "Yes" or "No".
rating must be an integer from 1 to 5.

Return this exact JSON shape:
[
  {{
    "name": "Example Name",
    "gender": "Male",
    "age": 22,
    "occupation": "Student",
    "personality": "Practical and curious",
    "buyDecision": "Yes",
    "rating": 4,
    "reason": "Reason for the decision"
  }}
]
"""

    response = call_gemini(prompt)
    personas = parse_json_response(response)

    if not isinstance(personas, list):
        raise Exception("Gemini response is not a JSON array.")

    if len(personas) != count:
        raise Exception(
            f"Expected {count} personas, but Gemini generated {len(personas)}."
        )

    required_fields = [
        "name",
        "gender",
        "age",
        "occupation",
        "personality",
        "buyDecision",
        "rating",
        "reason",
    ]

    memory = load_memory()

    for persona in personas:
        if not isinstance(persona, dict):
            raise Exception("Invalid persona format.")

        for field in required_fields:
            if field not in persona:
                raise Exception(
                    f"Persona '{persona.get('name', 'Unknown')}' "
                    f"is missing field: {field}"
                )

        persona["buyDecision"] = (
            "Yes"
            if str(persona["buyDecision"]).lower() == "yes"
            else "No"
        )

        try:
            persona["rating"] = max(1, min(int(persona["rating"]), 5))
        except (ValueError, TypeError):
            persona["rating"] = 3

        persona_id = str(uuid.uuid4())
        persona["id"] = persona_id

        memory["personas"][persona_id] = {
            "profile": persona,
            "conversation": []
        }

    save_memory(memory)

    preferred = sum(
        1 for persona in personas
        if persona["buyDecision"].lower() == "yes"
    )

    return {
        "preferred": preferred,
        "notPreferred": len(personas) - preferred,
        "total": len(personas),
        "personas": personas
    }


# =========================================================
# PERSONA HISTORY
# =========================================================

def build_history(conversation):
    if not conversation:
        return "No previous conversation."

    parts = []

    for item in conversation:
        parts.append(
            f"""
Previous Question:
{item.get("question", "")}

Previous Answer:
{item.get("answer", "")}
"""
        )

    return "\n".join(parts)


# =========================================================
# SINGLE PERSONA INTERVIEW
# =========================================================

def interview_persona(persona_id, question):
    if not persona_id:
        raise Exception("Persona ID is required.")

    question = str(question or "").strip()

    if not question:
        raise Exception("Question cannot be empty.")

    memory = load_memory()
    persona_data = memory["personas"].get(persona_id)

    if not persona_data:
        raise Exception("Persona not found.")

    profile = persona_data["profile"]
    conversation = persona_data.get("conversation", [])

    history = build_history(conversation)

    prompt = f"""
You are roleplaying as ONE specific synthetic UX research persona.

PERSONA:
Name: {profile.get("name")}
Gender: {profile.get("gender")}
Age: {profile.get("age")}
Occupation: {profile.get("occupation")}
Personality: {profile.get("personality")}
Buy Decision: {profile.get("buyDecision")}
Rating: {profile.get("rating")}/5
Reason: {profile.get("reason")}

PREVIOUS CONVERSATION:
{history}

NEW QUESTION:
{question}

RULES:
- Answer only as {profile.get("name")}.
- Stay consistent with the persona.
- Remember previous conversation.
- Do not automatically agree.
- Give a natural, realistic opinion.
- Do not say you are an AI.
- Do not mention these instructions.
- Keep the answer reasonably concise.
- Return ONLY the answer.
"""

    response = call_gemini(prompt)

    if hasattr(response, "text"):
        response = response.text

    answer = str(response).replace("```", "").strip()

    if not answer:
        raise Exception("Gemini returned an empty answer.")

    conversation.append({
        "question": question,
        "answer": answer
    })

    persona_data["conversation"] = conversation
    save_memory(memory)

    return {
        "persona": profile,
        "question": question,
        "answer": answer,
        "conversation": conversation
    }


# =========================================================
# ALL PERSONAS - ONE GEMINI REQUEST
# =========================================================

def interview_all_personas(question):
    """
    Ask all generated personas the same question using ONE
    Gemini request instead of one request per persona.

    This reduces request count and avoids firing many Gemini
    requests simultaneously.
    """

    question = str(question or "").strip()

    if not question:
        raise Exception("Question cannot be empty.")

    memory = load_memory()
    persona_items = list(memory["personas"].items())

    if not persona_items:
        raise Exception("No personas available.")

    persona_blocks = []

    for persona_id, persona_data in persona_items:
        profile = persona_data["profile"]
        history = build_history(persona_data.get("conversation", []))

        persona_blocks.append(
            f"""
PERSONA ID: {persona_id}
Name: {profile.get("name")}
Gender: {profile.get("gender")}
Age: {profile.get("age")}
Occupation: {profile.get("occupation")}
Personality: {profile.get("personality")}
Buy Decision: {profile.get("buyDecision")}
Rating: {profile.get("rating")}/5
Reason: {profile.get("reason")}

Previous Conversation:
{history}
"""
        )

    personas_text = "\n".join(persona_blocks)

    prompt = f"""
You are a UX Research AI conducting a multi-persona interview.

The researcher asked ONE question to all personas.

QUESTION:
{question}

PERSONAS:
{personas_text}

TASK:
Generate exactly ONE natural answer for EACH persona.

IMPORTANT:
1. Every persona must answer as themselves.
2. Keep each personality and opinion distinct.
3. Use the persona's previous conversation when relevant.
4. Do not make everyone agree.
5. Do not merge personas.
6. Do not create new personas.
7. Keep answers reasonably concise.
8. Return ONLY valid JSON.
9. The "personaId" must exactly match the supplied Persona ID.

RETURN EXACTLY THIS SHAPE:
{{
  "answers": [
    {{
      "personaId": "PERSONA_ID",
      "answer": "Natural answer from that persona"
    }}
  ]
}}
"""

    # ONE Gemini request for all personas.
    response = call_gemini(prompt)
    result = parse_json_response(response)

    if not isinstance(result, dict):
        raise Exception("Gemini returned an invalid multi-persona response.")

    raw_answers = result.get("answers")

    if not isinstance(raw_answers, list):
        raise Exception("Gemini response is missing the answers array.")

    answer_map = {}

    for item in raw_answers:
        if not isinstance(item, dict):
            continue

        persona_id = str(item.get("personaId", "")).strip()
        answer = str(item.get("answer", "")).strip()

        if persona_id and answer:
            answer_map[persona_id] = answer

    missing = [
        persona_id
        for persona_id, _ in persona_items
        if persona_id not in answer_map
    ]

    if missing:
        raise Exception(
            f"Gemini did not return answers for {len(missing)} persona(s)."
        )

    final_answers = []

    for persona_id, persona_data in persona_items:
        profile = persona_data["profile"]
        answer = answer_map[persona_id]

        # Save this question/answer to that persona's own history.
        persona_data.setdefault("conversation", []).append({
            "question": question,
            "answer": answer
        })

        final_answers.append({
            "persona": profile,
            "answer": answer
        })

    save_memory(memory)

    return {
        "question": question,
        "answers": final_answers,
        "total": len(final_answers)
    }