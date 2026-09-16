import json
import os
import re
import time
import uuid

from gemini import generate


# =========================================================
# FILE LOCATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")


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
                    "TIMEOUT",
                    "DEADLINE",
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
        return {
            "personas": {},
            "allPersonaInterviews": [],
            "askResearchHistory": [],
        }

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            return {
                "personas": {},
                "allPersonaInterviews": [],
                "askResearchHistory": [],
            }

        memory = json.loads(content)

        if not isinstance(memory, dict):
            memory = {}

        memory.setdefault("personas", {})
        memory.setdefault("allPersonaInterviews", [])
        memory.setdefault("askResearchHistory", [])

        return memory

    except (json.JSONDecodeError, OSError):
        return {
            "personas": {},
            "allPersonaInterviews": [],
            "askResearchHistory": [],
        }


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            memory,
            f,
            indent=2,
            ensure_ascii=False,
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

    # Remove Markdown code fences safely.
    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    ).strip()

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        pass

    array_match = re.search(
        r"\[.*\]",
        response,
        re.DOTALL,
    )

    if array_match:
        try:
            return json.loads(array_match.group())
        except json.JSONDecodeError:
            pass

    object_match = re.search(
        r"\{.*\}",
        response,
        re.DOTALL,
    )

    if object_match:
        try:
            return json.loads(object_match.group())
        except json.JSONDecodeError:
            pass

    raise Exception("Gemini did not return valid JSON.")


# =========================================================
# GENERATE PERSONAS
# =========================================================

MAX_PERSONAS = 100
BATCH_SIZE = 20


def _build_persona_prompt(
    product,
    description,
    gender,
    age,
    objective,
    batch_count,
    existing_names=None,
):
    existing_names = existing_names or []

    existing_names_text = (
        ", ".join(existing_names)
        if existing_names
        else "None yet"
    )

    return f"""
You are a professional UX Research AI.

Generate EXACTLY {batch_count} realistic synthetic personas for the product below.
This is one batch of a larger research sample, so every persona should be different
from the others. Prefer names that are not already used, but do not sacrifice
persona quality just to force name uniqueness.

PRODUCT
Product Name: {product}
Description: {description}

TARGET
Gender: {gender}
Age: {age}

RESEARCH OBJECTIVE
{objective}

NAMES ALREADY USED — DO NOT REUSE:
{existing_names_text}

RULES:
1. Generate exactly {batch_count} personas.
2. Follow the target gender.
3. Keep ages within the target audience.
4. Give every persona a different personality.
5. Give every persona a realistic occupation/background.
6. Do not make everyone agree.
7. Some personas may prefer the product and some may not.
8. Make opinions realistic for the research objective.
9. Prefer names that are not in the existing list.
10. Make the personas themselves meaningfully different even if a name happens to repeat.
11. Return ONLY valid JSON.

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


def _validate_and_prepare_personas(personas, expected_count, used_names):
    if not isinstance(personas, list):
        raise Exception("Gemini response is not a JSON array.")

    if len(personas) != expected_count:
        raise Exception(
            f"Expected {expected_count} personas in this batch, "
            f"but Gemini generated {len(personas)}."
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

    prepared = []
    batch_names = set()

    for persona in personas:
        if not isinstance(persona, dict):
            raise Exception("Invalid persona format.")

        for field in required_fields:
            if field not in persona:
                raise Exception(
                    f"Persona '{persona.get('name', 'Unknown')}' "
                    f"is missing field: {field}"
                )

        name = str(persona.get("name", "")).strip()
        if not name:
            raise Exception("Persona name cannot be empty.")

        name_key = name.casefold()

        # Do not fail an entire 20-person batch just because Gemini
        # repeated a name. A name collision does not mean the personas
        # are the same person: each persona still gets a unique UUID
        # and has its own profile, opinion, and conversation history.
        # We keep the name as generated so we never create artificial
        # names such as "Marcus Vance 2".
        batch_names.add(name_key)

        persona["name"] = name
        persona["buyDecision"] = (
            "Yes"
            if str(persona["buyDecision"]).strip().lower() == "yes"
            else "No"
        )

        try:
            persona["rating"] = max(
                1,
                min(int(persona["rating"]), 5),
            )
        except (ValueError, TypeError):
            persona["rating"] = 3

        persona_id = str(uuid.uuid4())
        persona["id"] = persona_id

        prepared.append(persona)

    return prepared, batch_names


def generate_personas(
    product,
    description,
    gender,
    age,
    objective,
    count,
):
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 20

    count = max(1, min(count, MAX_PERSONAS))

    print()
    print("========================================")
    print("      GENERATING SYNTHETIC PERSONAS")
    print("========================================")
    print(f"Requested personas: {count}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Number of batches: {(count + BATCH_SIZE - 1) // BATCH_SIZE}")
    print("========================================")

    # Generate in small batches because one Gemini request for 100
    # complete personas can become too large and may be less reliable.
    all_personas = []
    used_names = set()

    remaining = count
    batch_number = 1

    while remaining > 0:
        batch_count = min(BATCH_SIZE, remaining)

        print()
        print(
            f"[Persona Generation] Batch {batch_number}: "
            f"generating {batch_count} personas..."
        )

        # Retry the whole batch if Gemini returns a duplicate name or
        # the wrong number of personas.
        batch_personas = None
        last_error = None

        for batch_attempt in range(1, 4):
            try:
                prompt = _build_persona_prompt(
                    product=product,
                    description=description,
                    gender=gender,
                    age=age,
                    objective=objective,
                    batch_count=batch_count,
                    existing_names=sorted(used_names),
                )

                response = call_gemini(prompt)
                raw_personas = parse_json_response(response)

                prepared, batch_names = _validate_and_prepare_personas(
                    raw_personas,
                    expected_count=batch_count,
                    used_names=used_names,
                )

                batch_personas = prepared
                used_names.update(batch_names)
                break

            except Exception as e:
                last_error = e
                print(
                    f"[Persona Generation] Batch {batch_number} "
                    f"attempt {batch_attempt} failed: {e}"
                )

                if batch_attempt < 3:
                    time.sleep(2)

        if batch_personas is None:
            raise Exception(
                f"Unable to generate persona batch {batch_number}. "
                f"Last error: {last_error}"
            )

        all_personas.extend(batch_personas)
        remaining -= batch_count

        print(
            f"[Persona Generation] Batch {batch_number} complete. "
            f"Total generated: {len(all_personas)}/{count}"
        )

        batch_number += 1

    # Safety check before saving anything.
    if len(all_personas) != count:
        raise Exception(
            f"Expected {count} personas, but generated {len(all_personas)}."
        )

    memory = load_memory()

    # A new product generation starts a new research session.
    # Old personas/interviews/Ask Research results cannot leak
    # into the new research session.
    memory["personas"] = {}
    memory["allPersonaInterviews"] = []
    memory["askResearchHistory"] = []

    for persona in all_personas:
        memory["personas"][persona["id"]] = {
            "profile": persona,
            "conversation": [],
        }

    save_memory(memory)

    preferred = sum(
        1
        for persona in all_personas
        if persona["buyDecision"].lower() == "yes"
    )

    print()
    print("========================================")
    print("       PERSONA GENERATION COMPLETE")
    print("========================================")
    print(f"Total personas: {len(all_personas)}")
    print(f"Preferred: {preferred}")
    print(f"Not preferred: {len(all_personas) - preferred}")
    print("========================================")
    print()

    return {
        "preferred": preferred,
        "notPreferred": len(all_personas) - preferred,
        "total": len(all_personas),
        "personas": all_personas,
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
Previous Question: {item.get("question", "")}
Previous Answer: {item.get("answer", "")}
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

    answer = str(response).strip()

    answer = re.sub(
        r"^```(?:text)?\s*",
        "",
        answer,
        flags=re.IGNORECASE,
    )

    answer = re.sub(
        r"\s*```$",
        "",
        answer,
    ).strip()

    if not answer:
        raise Exception("Gemini returned an empty answer.")

    conversation.append(
        {
            "mode": "individual",
            "question": question,
            "answer": answer,
            "timestamp": time.time(),
        }
    )

    persona_data["conversation"] = conversation

    save_memory(memory)

    return {
        "persona": profile,
        "question": question,
        "answer": answer,
        "conversation": conversation,
    }


# =========================================================
# ALL PERSONAS - ONE GEMINI REQUEST
# =========================================================

def interview_all_personas(question, personas):
    """
    Ask the same question to ONLY the personas supplied by the
    current frontend generation.

    Gemini is called once for the complete current persona set.
    """

    question = str(question or "").strip()

    if not question:
        raise Exception("Question cannot be empty.")

    if not isinstance(personas, list) or not personas:
        raise Exception("No current personas provided.")

    current_personas = []

    for persona in personas:
        if not isinstance(persona, dict):
            continue

        persona_id = str(
            persona.get("id", "")
        ).strip()

        if not persona_id:
            continue

        current_personas.append(persona)

    if not current_personas:
        raise Exception("No valid current personas provided.")

    persona_blocks = []

    for profile in current_personas:
        persona_id = str(
            profile.get("id")
        ).strip()

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
"""
        )

    personas_text = "\n".join(persona_blocks)

    prompt = f"""
You are a UX Research AI conducting a multi-persona interview.

The researcher asked ONE question to the CURRENT PERSONAS below.

QUESTION:
{question}

CURRENT PERSONAS:
{personas_text}

TASK:
Generate exactly ONE natural answer for EACH CURRENT PERSONA.

IMPORTANT:
1. Use ONLY the supplied current personas.
2. Do NOT use personas from memory.
3. Do NOT create new personas.
4. Do NOT reuse personas from previous products.
5. Every supplied persona must receive exactly one answer.
6. Every persona must answer as themselves.
7. Keep each personality and opinion distinct.
8. Do not merge personas.
9. Do not make everyone agree.
10. Keep answers reasonably concise.
11. Return ONLY valid JSON.
12. The "personaId" must exactly match the supplied Persona ID.

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

    response = call_gemini(prompt)
    result = parse_json_response(response)

    if not isinstance(result, dict):
        raise Exception(
            "Gemini returned an invalid multi-persona response."
        )

    raw_answers = result.get("answers")

    if not isinstance(raw_answers, list):
        raise Exception(
            "Gemini response is missing the answers array."
        )

    answer_map = {}

    for item in raw_answers:
        if not isinstance(item, dict):
            continue

        persona_id = str(
            item.get("personaId", "")
        ).strip()

        answer = str(
            item.get("answer", "")
        ).strip()

        if persona_id and answer:
            answer_map[persona_id] = answer

    current_ids = [
        str(persona.get("id")).strip()
        for persona in current_personas
    ]

    missing = [
        persona_id
        for persona_id in current_ids
        if persona_id not in answer_map
    ]

    if missing:
        raise Exception(
            f"Gemini did not return answers for "
            f"{len(missing)} current persona(s)."
        )

    final_answers = []
    memory = load_memory()

    for profile in current_personas:
        persona_id = str(
            profile.get("id")
        ).strip()

        answer = answer_map[persona_id]

        persona_data = memory.get(
            "personas",
            {},
        ).get(persona_id)

        if persona_data:
            persona_data.setdefault(
                "conversation",
                [],
            ).append(
                {
                    "mode": "all",
                    "question": question,
                    "answer": answer,
                    "timestamp": time.time(),
                }
            )

        final_answers.append(
            {
                "persona": profile,
                "answer": answer,
            }
        )

    memory.setdefault(
        "allPersonaInterviews",
        [],
    ).append(
        {
            "question": question,
            "responses": [
                {
                    "personaId": str(
                        item["persona"].get("id", "")
                    ).strip(),
                    "personaName": item["persona"].get(
                        "name",
                        "Unknown",
                    ),
                    "answer": item["answer"],
                }
                for item in final_answers
            ],
            "timestamp": time.time(),
        }
    )

    save_memory(memory)

    return {
        "question": question,
        "answers": final_answers,
        "total": len(final_answers),
    }
