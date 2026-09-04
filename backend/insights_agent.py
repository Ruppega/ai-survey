import json
import os
import re
import time

from gemini import generate


MEMORY_FILE = "memory.json"


# =========================================================
# MEMORY
# =========================================================

def load_memory():
    """
    Load the persistent interview memory.

    The current agent.py stores:
        memory["personas"][persona_id] = {
            "profile": {...},
            "conversation": [...]
        }

    This Insights Agent reads that structure directly.
    """

    if not os.path.exists(MEMORY_FILE):
        return {
            "personas": {},
            "allPersonaInterviews": []
        }

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

        if not content:
            return {
                "personas": {},
                "allPersonaInterviews": []
            }

        memory = json.loads(content)

        if not isinstance(memory, dict):
            return {
                "personas": {},
                "allPersonaInterviews": []
            }

        memory.setdefault("personas", {})
        memory.setdefault("allPersonaInterviews", [])

        return memory

    except Exception as e:

        print(
            "Memory loading error:",
            str(e)
        )

        return {
            "personas": {},
            "allPersonaInterviews": []
        }


# =========================================================
# GEMINI HELPER
# =========================================================

def call_gemini(prompt, max_retries=3):

    """
    Call Gemini with retry handling.
    """

    for attempt in range(max_retries):

        try:

            response = generate(prompt)

            if hasattr(response, "text"):
                return response.text

            return str(response)

        except Exception as e:

            error_text = str(e).upper()

            temporary_error = any(
                code in error_text
                for code in (
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "503",
                    "UNAVAILABLE",
                    "SERVICE UNAVAILABLE"
                )
            )

            print(
                f"Gemini error on attempt "
                f"{attempt + 1}: {e}"
            )

            if not temporary_error:
                raise

            if attempt < max_retries - 1:

                wait_time = 5 * (
                    attempt + 1
                )

                print(
                    f"Retrying Gemini in "
                    f"{wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise Exception(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                ) from e


# =========================================================
# JSON PARSER
# =========================================================

def parse_json_response(response):

    if hasattr(response, "text"):
        response = response.text

    response = str(response).strip()

    # Remove markdown code fences
    response = re.sub(
        r"^```json\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"^```\s*",
        "",
        response
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    response = response.strip()

    # Direct JSON
    try:

        return json.loads(response)

    except json.JSONDecodeError:
        pass

    # Try extracting an object
    object_match = re.search(
        r"\{.*\}",
        response,
        re.DOTALL
    )

    if object_match:

        try:

            return json.loads(
                object_match.group()
            )

        except json.JSONDecodeError:
            pass

    # Try extracting an array
    array_match = re.search(
        r"\[.*\]",
        response,
        re.DOTALL
    )

    if array_match:

        try:

            return json.loads(
                array_match.group()
            )

        except json.JSONDecodeError:
            pass

    print(
        "Gemini returned invalid JSON:"
    )

    print(response)

    raise Exception(
        "Insights Agent received invalid JSON."
    )


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_question(question):

    """
    Normalize interview questions so that the same
    all-persona question can be detected across personas.
    """

    if not question:
        return ""

    question = str(question).strip().lower()

    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question


# =========================================================
# BUILD CURRENT PERSONA DATA
# =========================================================

def build_current_personas(personas):

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

        raise Exception(
            "No valid current personas available."
        )

    return current_personas


# =========================================================
# SURVEY ANALYSIS
# =========================================================

def calculate_survey_statistics(
    current_personas
):

    total_personas = len(
        current_personas
    )

    preferred = 0
    ratings = []

    for persona in current_personas:

        decision = str(
            persona.get(
                "buyDecision",
                ""
            )
        ).strip().lower()

        if decision == "yes":
            preferred += 1

        try:

            rating = float(
                persona.get(
                    "rating",
                    0
                )
            )

            if 1 <= rating <= 5:
                ratings.append(rating)

        except (
            ValueError,
            TypeError
        ):

            pass

    not_preferred = (
        total_personas - preferred
    )

    would_use_percentage = round(
        (
            preferred /
            total_personas
        ) * 100,
        1
    ) if total_personas else 0

    average_rating = round(
        sum(ratings) /
        len(ratings),
        1
    ) if ratings else 0

    return {
        "totalPersonas": total_personas,
        "preferred": preferred,
        "notPreferred": not_preferred,
        "wouldUsePercentage":
            would_use_percentage,
        "averageRating":
            average_rating
    }


# =========================================================
# INTERVIEW EXTRACTION
# =========================================================

def extract_interviews(current_personas):
    """
    Extract interview data for the CURRENT experiment.

    New records are stored explicitly by mode:
      - individual interviews -> persona conversation with mode=individual
      - all-persona interviews -> memory[allPersonaInterviews]

    Older records without mode are treated as individual records. This is
    intentional: an individual interview must never disappear merely because
    another persona was asked the same question.
    """

    memory = load_memory()
    memory_personas = memory.get("personas", {})

    individual_interviews = []
    all_persona_interviews = []
    grouped_questions = {}

    current_ids = {
        str(persona.get("id", "")).strip()
        for persona in current_personas
        if isinstance(persona, dict) and str(persona.get("id", "")).strip()
    }

    persona_by_id = {
        str(persona.get("id")).strip(): persona
        for persona in current_personas
        if isinstance(persona, dict) and str(persona.get("id", "")).strip()
    }

    # -----------------------------------------------------
    # INDIVIDUAL INTERVIEWS
    # -----------------------------------------------------
    for persona_id in current_ids:
        stored = memory_personas.get(persona_id, {})
        if not isinstance(stored, dict):
            continue

        conversation = stored.get("conversation", [])
        if not isinstance(conversation, list):
            continue

        persona = persona_by_id.get(persona_id, {})

        for item in conversation:
            if not isinstance(item, dict):
                continue

            question = str(item.get("question", "")).strip()
            answer = str(item.get("answer", "")).strip()

            if not question or not answer:
                continue

            # Explicit mode is authoritative.
            mode = str(item.get("mode", "individual")).strip().lower()

            if mode != "individual":
                continue

            individual_interviews.append({
                "mode": "individual",
                "personaId": persona_id,
                "personaName": persona.get("name", stored.get("profile", {}).get("name", "Unknown")),
                "question": question,
                "answer": answer
            })

    # -----------------------------------------------------
    # ALL-PERSONA INTERVIEWS
    # -----------------------------------------------------
    stored_group_interviews = memory.get("allPersonaInterviews", [])

    if isinstance(stored_group_interviews, list):
        for group in stored_group_interviews:
            if not isinstance(group, dict):
                continue

            question = str(group.get("question", "")).strip()
            responses = group.get("responses", [])

            if not question or not isinstance(responses, list):
                continue

            group_records = []

            for response in responses:
                if not isinstance(response, dict):
                    continue

                persona_id = str(response.get("personaId", "")).strip()
                answer = str(response.get("answer", "")).strip()

                if persona_id not in current_ids or not answer:
                    continue

                persona = persona_by_id.get(persona_id, {})

                record = {
                    "mode": "all",
                    "personaId": persona_id,
                    "personaName": response.get(
                        "personaName",
                        persona.get("name", "Unknown")
                    ),
                    "question": question,
                    "answer": answer
                }

                all_persona_interviews.append(record)
                group_records.append({
                    "personaId": persona_id,
                    "personaName": record["personaName"],
                    "answer": answer
                })

            if group_records:
                normalized = normalize_question(question)
                grouped_questions[normalized] = {
                    "question": question,
                    "responses": group_records
                }

    all_persona_question_groups = list(grouped_questions.values())

    individual_count = len(individual_interviews)
    all_persona_question_count = len(all_persona_question_groups)
    all_persona_response_count = len(all_persona_interviews)

    personas_with_individual = len({
        item["personaId"] for item in individual_interviews
    })

    personas_in_group = len({
        item["personaId"] for item in all_persona_interviews
    })

    return {
        "individualInterviews": individual_interviews,
        "allPersonaInterviews": all_persona_interviews,
        "allPersonaQuestionGroups": all_persona_question_groups,
        "stats": {
            "individualResponses": individual_count,
            "individualPersonas": personas_with_individual,
            "allPersonaQuestions": all_persona_question_count,
            "allPersonaResponses": all_persona_response_count,
            "allPersonaPersonas": personas_in_group,
            "totalInterviewDataPoints": (
                individual_count + all_persona_response_count
            )
        }
    }


# =========================================================
# PERSONA DATA FOR GEMINI
# =========================================================

def build_persona_data(
    current_personas
):

    result = []

    for persona in current_personas:

        result.append({

            "id":
                persona.get("id"),

            "name":
                persona.get("name"),

            "age":
                persona.get("age"),

            "gender":
                persona.get("gender"),

            "occupation":
                persona.get("occupation"),

            "personality":
                persona.get("personality"),

            "buyDecision":
                persona.get("buyDecision"),

            "rating":
                persona.get("rating"),

            "reason":
                persona.get("reason")

        })

    return result


# =========================================================
# EMPTY DEFAULT INSIGHTS
# =========================================================

def default_insights():

    return {

        "summary": "",

        "mainFinding": "",

        "positiveSignals": [],

        "concerns": [],

        "sentiment": {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        },

        "themes": [],

        "interviewDiscoveries": [],

        "agreementPatterns": [],

        "disagreementPatterns": [],

        "behavioralTrends": [],

        "segmentInsights": [],

        "surveyVsInterview": [],

        "individualPersonaInsights": []

    }


# =========================================================
# INSIGHTS AGENT
# =========================================================

def generate_insights(personas):

    """
    Main Insights Agent.

    Combines:

        1. Survey responses
        2. Individual interviews
        3. All-persona interviews

    Only the current experiment's personas are analyzed.
    """

    # -----------------------------------------------------
    # Validate current personas
    # -----------------------------------------------------

    if not isinstance(
        personas,
        list
    ) or not personas:

        raise Exception(
            "No current personas available for insights."
        )

    current_personas = build_current_personas(
        personas
    )

    total_personas = len(
        current_personas
    )

    print(
        "\n========================================"
    )

    print(
        "INSIGHTS AGENT"
    )

    print(
        f"Current personas: {total_personas}"
    )

    print(
        "========================================"
    )

    # -----------------------------------------------------
    # Survey
    # -----------------------------------------------------

    survey = calculate_survey_statistics(
        current_personas
    )

    print(
        "Survey:",
        survey
    )

    # -----------------------------------------------------
    # Interviews
    # -----------------------------------------------------

    interview_data = extract_interviews(
        current_personas
    )

    individual_interviews = (
        interview_data[
            "individualInterviews"
        ]
    )

    all_persona_interviews = (
        interview_data[
            "allPersonaInterviews"
        ]
    )

    all_persona_question_groups = (
        interview_data[
            "allPersonaQuestionGroups"
        ]
    )

    interview_stats = (
        interview_data["stats"]
    )

    print(
        "Individual interview responses:",
        interview_stats[
            "individualResponses"
        ]
    )

    print(
        "All-persona questions:",
        interview_stats[
            "allPersonaQuestions"
        ]
    )

    print(
        "All-persona responses:",
        interview_stats[
            "allPersonaResponses"
        ]
    )

    # -----------------------------------------------------
    # Prepare interview data
    # -----------------------------------------------------

    research_package = {

        "surveyResearch": {

            "totalPersonas":
                survey["totalPersonas"],

            "preferred":
                survey["preferred"],

            "notPreferred":
                survey["notPreferred"],

            "wouldUsePercentage":
                survey[
                    "wouldUsePercentage"
                ],

            "averageRating":
                survey[
                    "averageRating"
                ]
        },

        "personas":
            build_persona_data(
                current_personas
            ),

        "individualInterviews":
            individual_interviews,

        "allPersonaInterviews":
            all_persona_interviews,

        "allPersonaQuestionGroups":
            all_persona_question_groups

    }

    # -----------------------------------------------------
    # If there are NO interviews
    # -----------------------------------------------------

    no_interviews = (
        len(individual_interviews) == 0
        and
        len(all_persona_interviews) == 0
    )

    # -----------------------------------------------------
    # Gemini prompt
    # -----------------------------------------------------

    prompt = f"""
You are an expert UX Research Insights Agent.

You are analyzing ONE CURRENT PRODUCT RESEARCH EXPERIMENT.

IMPORTANT RULES:

1. Analyze ONLY the research data provided below.
2. Do NOT assume there are 20 personas.
3. The current experiment contains EXACTLY {total_personas} personas.
4. Do NOT create additional personas.
5. Do NOT use information from previous experiments.
6. Do NOT invent interview responses.
7. Every insight must be supported by the supplied research data.
8. If interview data is limited, clearly reflect that.
9. Distinguish survey findings from interview findings.
10. Use the persona's survey decision and rating when discussing survey results.
11. Use actual interview responses when discussing interview findings.
12. Do not claim that an interview occurred if there is no interview response.

SURVEY DATA:

{json.dumps(
    research_package["surveyResearch"],
    indent=2,
    ensure_ascii=False
)}

PERSONAS:

{json.dumps(
    research_package["personas"],
    indent=2,
    ensure_ascii=False
)}

INDIVIDUAL INTERVIEWS:

{json.dumps(
    research_package["individualInterviews"],
    indent=2,
    ensure_ascii=False
)}

ALL-PERSONA INTERVIEW RESPONSES:

{json.dumps(
    research_package["allPersonaInterviews"],
    indent=2,
    ensure_ascii=False
)}

ALL-PERSONA QUESTION GROUPS:

{json.dumps(
    research_package["allPersonaQuestionGroups"],
    indent=2,
    ensure_ascii=False
)}

INTERVIEW DATA AVAILABLE:

Individual responses:
{len(individual_interviews)}

All-persona questions:
{len(all_persona_question_groups)}

All-persona responses:
{len(all_persona_interviews)}

Now analyze the research.

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "summary": "2-4 sentence overall research summary",

    "mainFinding": "The most important finding",

    "positiveSignals": [
        "Positive research signal supported by evidence"
    ],

    "concerns": [
        "Concern or barrier supported by evidence"
    ],

    "sentiment": {{
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }},

    "themes": [
        {{
            "theme": "Theme name",
            "agreement": 0,
            "sentiment": "Positive",
            "description": "What the interview data shows"
        }}
    ],

    "interviewDiscoveries": [
        {{
            "type": "Need",
            "title": "Discovery title",
            "description": "What was discovered",
            "evidence": "Specific evidence from interviews"
        }}
    ],

    "agreementPatterns": [
        {{
            "topic": "Topic",
            "percentage": 0,
            "description": "What personas agreed about"
        }}
    ],

    "disagreementPatterns": [
        {{
            "topic": "Topic",
            "description": "How personas differed"
        }}
    ],

    "behavioralTrends": [
        "Observed behavioral trend"
    ],

    "segmentInsights": [
        {{
            "segment": "Segment name",
            "personaCount": 0,
            "wouldUsePercentage": 0,
            "averageRating": 0,
            "reasoning": "Why this segment behaves this way"
        }}
    ],

    "surveyVsInterview": [
        {{
            "topic": "Topic",
            "surveySignal": "What the survey indicates",
            "interviewSignal": "What interviews indicate",
            "interpretation": "How they relate",
            "direction": "Supports Survey"
        }}
    ],

    "individualPersonaInsights": [
        {{
            "persona": "Persona name",
            "surveyDecision": "Yes",
            "surveyRating": 4,
            "interviewSentiment": "Positive",
            "keyFinding": "Key finding from this persona",
            "supportsSurvey": true
        }}
    ]
}}

VALID VALUES FOR surveyVsInterview.direction:

"Supports Survey"
"Challenges Survey"
"Adds Detail"

VALID VALUES FOR sentiment labels:

"Positive"
"Neutral"
"Negative"

IMPORTANT:

If there are no interviews, return empty arrays for:

themes
interviewDiscoveries
agreementPatterns
disagreementPatterns
behavioralTrends
surveyVsInterview
individualPersonaInsights

and set:

sentiment = {{
    "positive": 0,
    "neutral": 0,
    "negative": 0
}}

Do not invent interview findings.
"""

    # -----------------------------------------------------
    # No interview data:
    # We still ask Gemini to summarize survey data.
    # -----------------------------------------------------

    if no_interviews:

        print(
            "No interview records found."
        )

    # -----------------------------------------------------
    # Call Gemini
    # -----------------------------------------------------

    response = call_gemini(
        prompt
    )

    insights = parse_json_response(
        response
    )

    if not isinstance(
        insights,
        dict
    ):

        raise Exception(
            "Gemini insights response "
            "must be a JSON object."
        )

    # -----------------------------------------------------
    # Merge defaults
    # -----------------------------------------------------

    defaults = default_insights()

    for key, value in defaults.items():

        if key not in insights:

            insights[key] = value

    # -----------------------------------------------------
    # Force empty interview sections if
    # there is actually no interview data.
    # -----------------------------------------------------

    if no_interviews:

        insights["sentiment"] = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

        insights["themes"] = []

        insights[
            "interviewDiscoveries"
        ] = []

        insights[
            "agreementPatterns"
        ] = []

        insights[
            "disagreementPatterns"
        ] = []

        insights[
            "behavioralTrends"
        ] = []

        insights[
            "surveyVsInterview"
        ] = []

        insights[
            "individualPersonaInsights"
        ] = []

    # -----------------------------------------------------
    # ALWAYS use Python-calculated survey statistics
    # -----------------------------------------------------

    insights["productScore"] = {

        "wouldUsePercentage":
            survey[
                "wouldUsePercentage"
            ],

        "preferred":
            survey[
                "preferred"
            ],

        "notPreferred":
            survey[
                "notPreferred"
            ],

        "totalPersonas":
            survey[
                "totalPersonas"
            ],

        "averageRating":
            survey[
                "averageRating"
            ]
    }

    # -----------------------------------------------------
    # Interview statistics
    # -----------------------------------------------------

    insights["interviewStats"] = {

        "individualResponses":
            interview_stats[
                "individualResponses"
            ],

        "individualPersonas":
            interview_stats[
                "individualPersonas"
            ],

        "allPersonaQuestions":
            interview_stats[
                "allPersonaQuestions"
            ],

        "allPersonaResponses":
            interview_stats[
                "allPersonaResponses"
            ],

        "allPersonaPersonas":
            interview_stats[
                "allPersonaPersonas"
            ],

        "totalInterviewDataPoints":
            interview_stats[
                "totalInterviewDataPoints"
            ],

        "hasIndividualInterviews":
            interview_stats[
                "individualResponses"
            ] > 0,

        "hasAllPersonaInterviews":
            interview_stats[
                "allPersonaQuestions"
            ] > 0
    }

    # -----------------------------------------------------
    # Ensure summary exists
    # -----------------------------------------------------

    if not str(
        insights.get(
            "summary",
            ""
        )
    ).strip():

        insights["summary"] = (
            f"Out of {survey['totalPersonas']} "
            f"personas, "
            f"{survey['wouldUsePercentage']}% "
            f"indicated that they would use "
            f"or purchase the product."
        )

    # -----------------------------------------------------
    # Ensure main finding exists
    # -----------------------------------------------------

    if not str(
        insights.get(
            "mainFinding",
            ""
        )
    ).strip():

        insights["mainFinding"] = (
            f"{survey['preferred']} of "
            f"{survey['totalPersonas']} personas "
            f"preferred the product."
        )

    # -----------------------------------------------------
    # Debug output
    # -----------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "INSIGHTS GENERATED"
    )

    print(
        f"Personas: {total_personas}"
    )

    print(
        f"Individual interviews: "
        f"{interview_stats['individualResponses']}"
    )

    print(
        f"All-persona questions: "
        f"{interview_stats['allPersonaQuestions']}"
    )

    print(
        f"All-persona responses: "
        f"{interview_stats['allPersonaResponses']}"
    )

    print(
        "========================================\n"
    )

    return insights