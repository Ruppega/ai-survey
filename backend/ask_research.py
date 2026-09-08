import json
import os
import re
import time
from collections import Counter

from gemini import generate

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"personas": {}, "allPersonaInterviews": []}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            return {"personas": {}, "allPersonaInterviews": []}

        memory = json.loads(content)
        memory.setdefault("personas", {})
        memory.setdefault("allPersonaInterviews", [])
        return memory
    except (json.JSONDecodeError, OSError):
        return {"personas": {}, "allPersonaInterviews": []}


def parse_json_response(response):
    if hasattr(response, "text"):
        response = response.text

    text = str(response).strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError("Gemini did not return valid JSON.")


def clean_text(value, fallback=""):
    if value is None:
        return fallback
    return str(value).strip()


def build_research_context(personas):
    """Build only the current experiment's survey + interview evidence."""
    current_ids = {
        clean_text(persona.get("id"))
        for persona in personas
        if isinstance(persona, dict) and clean_text(persona.get("id"))
    }

    memory = load_memory()
    stored_personas = memory.get("personas", {})

    survey = []
    individual_interviews = []

    for persona in personas:
        if not isinstance(persona, dict):
            continue

        persona_id = clean_text(persona.get("id"))
        stored = stored_personas.get(persona_id, {})
        conversation = stored.get("conversation", []) if isinstance(stored, dict) else []

        survey.append({
            "personaId": persona_id,
            "name": clean_text(persona.get("name"), "Unknown"),
            "age": persona.get("age"),
            "gender": clean_text(persona.get("gender")),
            "occupation": clean_text(persona.get("occupation")),
            "personality": clean_text(persona.get("personality")),
            "buyDecision": clean_text(persona.get("buyDecision")),
            "rating": persona.get("rating"),
            "reason": clean_text(persona.get("reason")),
        })

        for item in conversation:
            if not isinstance(item, dict):
                continue

            # New interview records explicitly identify the mode.
            # Legacy records are treated as individual rather than guessing.
            if item.get("mode", "individual") != "individual":
                continue

            question = clean_text(item.get("question"))
            answer = clean_text(item.get("answer"))
            if question and answer:
                individual_interviews.append({
                    "personaId": persona_id,
                    "personaName": clean_text(persona.get("name"), "Unknown"),
                    "question": question,
                    "answer": answer,
                })

    all_persona_interviews = []
    for group in memory.get("allPersonaInterviews", []):
        if not isinstance(group, dict):
            continue

        responses = []
        for response in group.get("responses", []):
            if not isinstance(response, dict):
                continue

            persona_id = clean_text(response.get("personaId"))
            if persona_id not in current_ids:
                continue

            answer = clean_text(response.get("answer"))
            if answer:
                responses.append({
                    "personaId": persona_id,
                    "personaName": clean_text(response.get("personaName"), "Unknown"),
                    "answer": answer,
                })

        if responses:
            all_persona_interviews.append({
                "question": clean_text(group.get("question")),
                "responses": responses,
            })

    total_personas = len(survey)
    preferred = sum(
        1 for item in survey
        if item["buyDecision"].lower() == "yes"
    )
    ratings = [
        float(item["rating"])
        for item in survey
        if isinstance(item.get("rating"), (int, float))
        and 1 <= float(item["rating"]) <= 5
    ]

    return {
        "survey": {
            "totalPersonas": total_personas,
            "preferred": preferred,
            "notPreferred": total_personas - preferred,
            "wouldUsePercentage": round((preferred / total_personas) * 100, 1) if total_personas else 0,
            "averageRating": round(sum(ratings) / len(ratings), 1) if ratings else 0,
            "personas": survey,
        },
        "individualInterviews": individual_interviews,
        "allPersonaInterviews": all_persona_interviews,
    }


def flatten_evidence(context):
    evidence = []

    for item in context["survey"]["personas"]:
        evidence.append({
            "type": "survey",
            "persona": item["name"],
            "text": (
                f"{item['name']} chose {item['buyDecision']} with a rating of "
                f"{item['rating']}/5. Reason: {item['reason']}"
            ),
        })

    for item in context["individualInterviews"]:
        evidence.append({
            "type": "individual interview",
            "persona": item["personaName"],
            "text": f"Q: {item['question']} A: {item['answer']}",
        })

    for group in context["allPersonaInterviews"]:
        for item in group["responses"]:
            evidence.append({
                "type": "all-persona interview",
                "persona": item["personaName"],
                "text": f"Q: {group['question']} A: {item['answer']}",
            })

    return evidence


def local_fallback(question, context):
    """Deterministic answer when Gemini is temporarily unavailable."""
    q = question.lower()
    survey = context["survey"]
    personas = survey["personas"]
    individual = context["individualInterviews"]
    groups = context["allPersonaInterviews"]

    evidence = flatten_evidence(context)

    if not personas:
        return {
            "answer": "There is no current research data to analyze yet.",
            "keyEvidence": [],
            "confidence": "Low",
        }

    # Product-use / preference questions.
    if any(term in q for term in ["would use", "use the product", "buy", "purchase", "prefer"]):
        answer = (
            f"{survey['preferred']} of {survey['totalPersonas']} personas "
            f"would use or prefer the product ({survey['wouldUsePercentage']}%). "
            f"The average rating is {survey['averageRating']}/5."
        )
        selected = [
            item for item in evidence
            if item["type"] == "survey"
        ][:4]
        return {
            "answer": answer,
            "keyEvidence": [item["text"] for item in selected],
            "confidence": "High",
        }

    # Price / cost questions.
    if any(term in q for term in ["price", "cost", "expensive", "cheap", "afford"]):
        matches = [
            item for item in evidence
            if any(term in item["text"].lower() for term in ["price", "cost", "expensive", "cheap", "afford"])
        ]
        if matches:
            return {
                "answer": "The research mentions price-related considerations in the evidence below.",
                "keyEvidence": [item["text"] for item in matches[:5]],
                "confidence": "Medium",
            }
        return {
            "answer": "The current research does not contain enough explicit evidence about price or cost.",
            "keyEvidence": [],
            "confidence": "Low",
        }

    # Concern / barrier questions.
    if any(term in q for term in ["concern", "barrier", "stop", "problem", "disadvantage", "not use", "negative"]):
        no_users = [
            item for item in personas
            if item["buyDecision"].lower() == "no"
        ]
        evidence_items = [
            f"{item['name']}: {item['reason']}"
            for item in no_users[:5]
        ]
        if evidence_items:
            return {
                "answer": f"{len(no_users)} personas did not prefer the product. Their stated reasons are the clearest current evidence of barriers.",
                "keyEvidence": evidence_items,
                "confidence": "High",
            }

    # Sentiment-ish questions from simple keyword scoring.
    if any(term in q for term in ["sentiment", "positive", "negative", "feel", "opinion"]):
        positive_words = {"good", "great", "love", "useful", "easy", "helpful", "like", "convenient", "excellent"}
        negative_words = {"bad", "poor", "hate", "difficult", "expensive", "problem", "concern", "annoying", "confusing"}
        pos = neg = 0
        for item in evidence:
            words = set(re.findall(r"[a-zA-Z]+", item["text"].lower()))
            pos += len(words & positive_words)
            neg += len(words & negative_words)
        if pos > neg:
            sentiment = "more positive"
        elif neg > pos:
            sentiment = "more negative"
        else:
            sentiment = "mixed or neutral"
        return {
            "answer": f"Based on a simple evidence-word check, the available research appears {sentiment}. This is a fallback estimate, not a full semantic sentiment analysis.",
            "keyEvidence": [item["text"] for item in evidence[:5]],
            "confidence": "Low",
        }

    # Generic research answer: show actual evidence rather than inventing a conclusion.
    selected = evidence[:6]
    if individual or groups:
        answer = (
            "The current research contains survey and interview evidence. "
            "The most directly relevant evidence available is shown below. "
            "A stronger conclusion would require semantic analysis of the full dataset."
        )
    else:
        answer = (
            "The current dataset contains survey responses but no interview evidence yet. "
            "The survey data below is the available basis for answering this question."
        )

    return {
        "answer": answer,
        "keyEvidence": [item["text"] for item in selected],
        "confidence": "Medium" if selected else "Low",
    }


def ask_gemini(question, context):
    compact_context = {
        "survey": context["survey"],
        "individualInterviews": context["individualInterviews"],
        "allPersonaInterviews": context["allPersonaInterviews"],
    }

    prompt = f"""
You are the Ask Your Research agent inside a UX research application.

Answer the researcher's question using ONLY the CURRENT RESEARCH DATA below.

STRICT RULES:
1. Do not invent personas, quotes, statistics, interviews, or findings.
2. Do not use knowledge from previous experiments.
3. Distinguish survey evidence from interview evidence.
4. If the data is insufficient, say so clearly.
5. When making a numeric claim, use only numbers present in the supplied data or simple calculations from them.
6. When useful, name the persona(s) that support the conclusion.
7. Do not claim an interview happened unless an interview record is supplied.
8. Keep the answer concise but useful for a researcher.
9. Return ONLY valid JSON.

RESEARCHER QUESTION:
{question}

CURRENT RESEARCH DATA:
{json.dumps(compact_context, indent=2, ensure_ascii=False)}

Return exactly:
{{
  "answer": "A concise evidence-grounded answer",
  "keyEvidence": [
    "Specific evidence from the supplied data"
  ],
  "confidence": "High"
}}

confidence must be exactly one of: High, Medium, Low.
"""

    # One request only. Ask Your Research should fail fast to its deterministic fallback
    # rather than consuming multiple quota attempts.
    response = generate(prompt)
    result = parse_json_response(response)

    if not isinstance(result, dict):
        raise ValueError("Invalid Ask Your Research response.")

    answer = clean_text(result.get("answer"))
    evidence = result.get("keyEvidence", [])
    confidence = clean_text(result.get("confidence"), "Medium").title()

    if confidence not in {"High", "Medium", "Low"}:
        confidence = "Medium"

    if not answer:
        raise ValueError("Ask Your Research returned an empty answer.")

    if not isinstance(evidence, list):
        evidence = []

    evidence = [clean_text(item) for item in evidence if clean_text(item)]

    return {
        "answer": answer,
        "keyEvidence": evidence[:8],
        "confidence": confidence,
    }


def answer_research_question(question, personas):
    question = clean_text(question)

    if not question:
        raise ValueError("Question is required.")

    if not isinstance(personas, list) or not personas:
        raise ValueError("No current personas were provided.")

    current_personas = [
        persona for persona in personas
        if isinstance(persona, dict) and clean_text(persona.get("id"))
    ]

    if not current_personas:
        raise ValueError("No valid current personas were provided.")

    context = build_research_context(current_personas)

    survey_personas = context["survey"]["personas"]
    interview_count = (
        len(context["individualInterviews"])
        + sum(len(group["responses"]) for group in context["allPersonaInterviews"])
    )

    try:
        result = ask_gemini(question, context)
        source = "ai"
    except Exception as error:
        print("[Ask Your Research] Gemini unavailable:", str(error))
        result = local_fallback(question, context)
        source = "fallback"

    return {
        "question": question,
        "answer": result["answer"],
        "keyEvidence": result.get("keyEvidence", []),
        "confidence": result.get("confidence", "Medium"),
        "source": source,
        "sources": {
            "surveyResponses": len(survey_personas),
            "individualInterviewResponses": len(context["individualInterviews"]),
            "allPersonaQuestions": len(context["allPersonaInterviews"]),
            "allPersonaInterviewResponses": sum(
                len(group["responses"])
                for group in context["allPersonaInterviews"]
            ),
            "personas": len(current_personas),
            "totalEvidenceItems": len(flatten_evidence(context)),
        },
        "generatedAt": time.time(),
    }
