import json
import os
import re
import time

from gemini import generate


# =========================================================
# CONFIGURATION
# =========================================================

MEMORY_FILE = "memory.json"


# =========================================================
# MEMORY
# =========================================================

def load_memory():
    """
    Load persistent interview memory.

    Expected structure:

    memory = {
        "personas": {
            "persona_id": {
                "profile": {...},
                "conversation": [
                    {
                        "question": "...",
                        "answer": "...",
                        "timestamp": ...
                    }
                ]
            }
        }
    }
    """

    if not os.path.exists(MEMORY_FILE):
        print("[Insights] memory.json not found.")

        return {
            "personas": {},
            "allPersonaInterviews": []
        }

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read().strip()

        if not content:
            print("[Insights] memory.json is empty.")

            return {
                "personas": {},
                "allPersonaInterviews": []
            }

        memory = json.loads(content)

        if not isinstance(memory, dict):
            print("[Insights] memory.json root is not an object.")

            return {
                "personas": {},
                "allPersonaInterviews": []
            }

        memory.setdefault("personas", {})
        memory.setdefault("allPersonaInterviews", [])

        return memory

    except json.JSONDecodeError as e:

        print(
            "[Insights] Invalid JSON in memory.json:",
            str(e)
        )

        return {
            "personas": {},
            "allPersonaInterviews": []
        }

    except Exception as e:

        print(
            "[Insights] Memory loading error:",
            type(e).__name__,
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

    IMPORTANT:
    This version does NOT hide the original Gemini error.
    The real error is printed in the Flask terminal.
    """

    last_error = None

    for attempt in range(max_retries):

        try:

            print()
            print("========================================")
            print(
                f"Calling Gemini for insights "
                f"(attempt {attempt + 1}/{max_retries})"
            )
            print("========================================")

            response = generate(prompt)

            if response is None:
                raise Exception(
                    "Gemini returned an empty response."
                )

            # Gemini response object
            if hasattr(response, "text"):

                text = response.text

                if text and str(text).strip():

                    print(
                        "[Insights] Gemini response received."
                    )

                    return str(text).strip()

                raise Exception(
                    "Gemini response contained no text."
                )

            # String response
            response_text = str(response).strip()

            if response_text:

                print(
                    "[Insights] Gemini response received."
                )

                return response_text

            raise Exception(
                "Gemini returned an empty response."
            )

        except Exception as e:

            last_error = e

            print()
            print("========================================")
            print("          GEMINI API ERROR")
            print("========================================")

            print("Attempt:")
            print(
                f"{attempt + 1}/{max_retries}"
            )

            print()

            print("Error type:")
            print(type(e).__name__)

            print()

            print("Error message:")
            print(str(e))

            print()
            print("========================================")
            print()

            error_text = str(e).upper()

            # Temporary / rate-limit errors
            temporary_error = any(
                code in error_text
                for code in [
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "503",
                    "UNAVAILABLE",
                    "SERVICE UNAVAILABLE",
                    "DEADLINE",
                    "TIMEOUT"
                ]
            )

            if not temporary_error:

                # Do not retry errors such as:
                # invalid API key
                # invalid model
                # invalid request
                # malformed request

                raise

            if attempt < max_retries - 1:

                wait_time = 5 * (attempt + 1)

                print(
                    f"[Insights] Temporary Gemini error."
                )

                print(
                    f"[Insights] Retrying in "
                    f"{wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                print(
                    "[Insights] Gemini failed after "
                    f"{max_retries} attempts."
                )

    # If we reach here, preserve the real exception.
    if last_error:

        raise Exception(
            "Gemini Insights Agent failed after "
            f"{max_retries} attempts: "
            f"{type(last_error).__name__}: "
            f"{str(last_error)}"
        ) from last_error

    raise Exception(
        "Gemini Insights Agent failed unexpectedly."
    )


# =========================================================
# JSON PARSER
# =========================================================

def parse_json_response(response):

    """
    Safely parse JSON returned by Gemini.

    Handles:
    - normal JSON
    - ```json ... ```
    - ``` ... ```
    - JSON embedded in additional text
    """

    if response is None:

        raise Exception(
            "Gemini returned no response."
        )

    if hasattr(response, "text"):

        response = response.text

    response = str(response).strip()

    if not response:

        raise Exception(
            "Gemini returned an empty response."
        )

    # -----------------------------------------------------
    # Remove markdown code fences
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Direct JSON
    # -----------------------------------------------------

    try:

        return json.loads(response)

    except json.JSONDecodeError:
        pass

    # -----------------------------------------------------
    # Extract JSON object
    # -----------------------------------------------------

    first_object = response.find("{")
    last_object = response.rfind("}")

    if (
        first_object != -1
        and last_object != -1
        and last_object > first_object
    ):

        possible_json = response[
            first_object:last_object + 1
        ]

        try:

            return json.loads(
                possible_json
            )

        except json.JSONDecodeError:
            pass

    # -----------------------------------------------------
    # Extract JSON array
    # -----------------------------------------------------

    first_array = response.find("[")
    last_array = response.rfind("]")

    if (
        first_array != -1
        and last_array != -1
        and last_array > first_array
    ):

        possible_json = response[
            first_array:last_array + 1
        ]

        try:

            return json.loads(
                possible_json
            )

        except json.JSONDecodeError:
            pass

    # -----------------------------------------------------
    # Failed
    # -----------------------------------------------------

    print()
    print("========================================")
    print("GEMINI RETURNED INVALID JSON")
    print("========================================")

    print(response)

    print("========================================")
    print()

    raise Exception(
        "Insights Agent received invalid JSON "
        "from Gemini."
    )


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_question(question):

    """
    Normalize interview questions.

    Example:

    "What features do you like?"
    " what features do you like? "

    become the same normalized question.
    """

    if not question:
        return ""

    question = str(
        question
    ).strip().lower()

    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question


# =========================================================
# BUILD CURRENT PERSONAS
# =========================================================

def build_current_personas(personas):

    current_personas = []

    if not isinstance(personas, list):

        raise Exception(
            "Personas must be provided as a list."
        )

    for persona in personas:

        if not isinstance(persona, dict):
            continue

        persona_id = str(
            persona.get(
                "id",
                ""
            )
        ).strip()

        if not persona_id:
            continue

        current_personas.append(
            persona
        )

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

    not_preferred = 0

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

        elif decision == "no":

            not_preferred += 1

    # Safety correction
    if preferred + not_preferred < total_personas:

        not_preferred = (
            total_personas - preferred
        )

    # -----------------------------------------------------
    # Ratings
    # -----------------------------------------------------

    for persona in current_personas:

        try:

            rating = float(
                persona.get(
                    "rating",
                    0
                )
            )

            if 1 <= rating <= 5:

                ratings.append(
                    rating
                )

        except (
            ValueError,
            TypeError
        ):

            continue

    # -----------------------------------------------------
    # Percentage
    # -----------------------------------------------------

    if total_personas > 0:

        would_use_percentage = round(
            (
                preferred /
                total_personas
            ) * 100,
            1
        )

    else:

        would_use_percentage = 0

    # -----------------------------------------------------
    # Average rating
    # -----------------------------------------------------

    if ratings:

        average_rating = round(
            sum(ratings) /
            len(ratings),
            1
        )

    else:

        average_rating = 0

    return {

        "totalPersonas":
            total_personas,

        "preferred":
            preferred,

        "notPreferred":
            not_preferred,

        "wouldUsePercentage":
            would_use_percentage,

        "averageRating":
            average_rating
    }


# =========================================================
# INTERVIEW EXTRACTION
# =========================================================

def extract_interviews(
    current_personas
):

    """
    Extract interview conversations belonging ONLY
    to the current personas.

    Current agent.py stores interviews under:

        memory["personas"][persona_id]["conversation"]

    Since older records do not contain an explicit
    interview mode, repeated questions across multiple
    personas are treated as all-persona interview questions.
    """

    memory = load_memory()

    memory_personas = memory.get(
        "personas",
        {}
    )

    if not isinstance(
        memory_personas,
        dict
    ):

        memory_personas = {}

    # -----------------------------------------------------
    # Current persona IDs
    # -----------------------------------------------------

    current_ids = {

        str(
            persona.get(
                "id",
                ""
            )
        ).strip()

        for persona in current_personas

        if persona.get("id")
    }

    print()
    print(
        "[Insights] Current persona IDs:",
        list(current_ids)
    )

    # -----------------------------------------------------
    # Collect conversations
    # -----------------------------------------------------

    conversations = {}

    for persona in current_personas:

        persona_id = str(
            persona.get(
                "id",
                ""
            )
        ).strip()

        stored = memory_personas.get(
            persona_id
        )

        if not isinstance(
            stored,
            dict
        ):

            conversations[
                persona_id
            ] = []

            continue

        conversation = stored.get(
            "conversation",
            []
        )

        if not isinstance(
            conversation,
            list
        ):

            conversation = []

        conversations[
            persona_id
        ] = conversation

    # -----------------------------------------------------
    # Debug conversation counts
    # -----------------------------------------------------

    print(
        "[Insights] Conversation counts:"
    )

    for persona_id, conversation in conversations.items():

        print(
            f"  {persona_id}: "
            f"{len(conversation)} records"
        )

    # -----------------------------------------------------
    # Count question occurrences
    # -----------------------------------------------------

    question_occurrences = {}

    for persona_id, conversation in conversations.items():

        for item in conversation:

            if not isinstance(
                item,
                dict
            ):

                continue

            question = str(
                item.get(
                    "question",
                    ""
                )
            ).strip()

            answer = str(
                item.get(
                    "answer",
                    ""
                )
            ).strip()

            if not question or not answer:
                continue

            normalized = normalize_question(
                question
            )

            if not normalized:
                continue

            if normalized not in question_occurrences:

                question_occurrences[
                    normalized
                ] = {

                    "question":
                        question,

                    "personas":
                        []
                }

            question_occurrences[
                normalized
            ]["personas"].append(
                persona_id
            )

    # -----------------------------------------------------
    # Identify all-persona questions
    # -----------------------------------------------------

    all_persona_questions = {

        question_key

        for question_key, data
        in question_occurrences.items()

        if len(
            set(
                data["personas"]
            )
        ) >= 2
    }

    print(
        "[Insights] Unique interview questions:",
        len(question_occurrences)
    )

    print(
        "[Insights] Detected all-persona questions:",
        len(all_persona_questions)
    )

    # -----------------------------------------------------
    # Separate interviews
    # -----------------------------------------------------

    individual_interviews = []

    all_persona_interviews = []

    for persona in current_personas:

        persona_id = str(
            persona.get(
                "id",
                ""
            )
        ).strip()

        conversation = conversations.get(
            persona_id,
            []
        )

        for item in conversation:

            if not isinstance(
                item,
                dict
            ):

                continue

            question = str(
                item.get(
                    "question",
                    ""
                )
            ).strip()

            answer = str(
                item.get(
                    "answer",
                    ""
                )
            ).strip()

            if not question or not answer:
                continue

            normalized = normalize_question(
                question
            )

            record = {

                "personaId":
                    persona_id,

                "personaName":
                    persona.get(
                        "name",
                        "Unknown"
                    ),

                "question":
                    question,

                "answer":
                    answer
            }

            if normalized in all_persona_questions:

                all_persona_interviews.append(
                    record
                )

            else:

                individual_interviews.append(
                    record
                )

    # -----------------------------------------------------
    # Group all-persona questions
    # -----------------------------------------------------

    grouped_questions = {}

    for record in all_persona_interviews:

        normalized = normalize_question(
            record["question"]
        )

        if normalized not in grouped_questions:

            grouped_questions[
                normalized
            ] = {

                "question":
                    record["question"],

                "responses":
                    []
            }

        grouped_questions[
            normalized
        ]["responses"].append({

            "personaId":
                record["personaId"],

            "personaName":
                record["personaName"],

            "answer":
                record["answer"]
        })

    all_persona_question_groups = list(
        grouped_questions.values()
    )

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    individual_count = len(
        individual_interviews
    )

    all_persona_question_count = len(
        all_persona_question_groups
    )

    all_persona_response_count = len(
        all_persona_interviews
    )

    personas_with_individual = len({

        item["personaId"]

        for item in individual_interviews
    })

    personas_in_group = len({

        item["personaId"]

        for item in all_persona_interviews
    })

    total_data_points = (
        individual_count
        +
        all_persona_response_count
    )

    return {

        "individualInterviews":
            individual_interviews,

        "allPersonaInterviews":
            all_persona_interviews,

        "allPersonaQuestionGroups":
            all_persona_question_groups,

        "stats": {

            "individualResponses":
                individual_count,

            "individualPersonas":
                personas_with_individual,

            "allPersonaQuestions":
                all_persona_question_count,

            "allPersonaResponses":
                all_persona_response_count,

            "allPersonaPersonas":
                personas_in_group,

            "totalInterviewDataPoints":
                total_data_points
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
                persona.get(
                    "id"
                ),

            "name":
                persona.get(
                    "name"
                ),

            "age":
                persona.get(
                    "age"
                ),

            "gender":
                persona.get(
                    "gender"
                ),

            "occupation":
                persona.get(
                    "occupation"
                ),

            "personality":
                persona.get(
                    "personality"
                ),

            "buyDecision":
                persona.get(
                    "buyDecision"
                ),

            "rating":
                persona.get(
                    "rating"
                ),

            "reason":
                persona.get(
                    "reason"
                )
        })

    return result


# =========================================================
# DEFAULT INSIGHTS
# =========================================================

def default_insights():

    return {

        "summary":
            "",

        "mainFinding":
            "",

        "positiveSignals":
            [],

        "concerns":
            [],

        "sentiment": {

            "positive":
                0,

            "neutral":
                0,

            "negative":
                0
        },

        "themes":
            [],

        "interviewDiscoveries":
            [],

        "agreementPatterns":
            [],

        "disagreementPatterns":
            [],

        "behavioralTrends":
            [],

        "segmentInsights":
            [],

        "surveyVsInterview":
            [],

        "individualPersonaInsights":
            []
    }


# =========================================================
# NORMALIZE GEMINI INSIGHTS
# =========================================================

def normalize_insights(
    insights
):

    defaults = default_insights()

    if not isinstance(
        insights,
        dict
    ):

        raise Exception(
            "Gemini insights response "
            "must be a JSON object."
        )

    # Add missing fields
    for key, default_value in defaults.items():

        if key not in insights:

            insights[key] = default_value

    # -----------------------------------------------------
    # Sentiment
    # -----------------------------------------------------

    if not isinstance(
        insights.get("sentiment"),
        dict
    ):

        insights["sentiment"] = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

    for key in [
        "positive",
        "neutral",
        "negative"
    ]:

        try:

            insights["sentiment"][key] = int(
                insights["sentiment"].get(
                    key,
                    0
                )
            )

        except (
            ValueError,
            TypeError
        ):

            insights["sentiment"][key] = 0

    # -----------------------------------------------------
    # Arrays
    # -----------------------------------------------------

    array_fields = [

        "positiveSignals",
        "concerns",
        "themes",
        "interviewDiscoveries",
        "agreementPatterns",
        "disagreementPatterns",
        "behavioralTrends",
        "segmentInsights",
        "surveyVsInterview",
        "individualPersonaInsights"
    ]

    for field in array_fields:

        if not isinstance(
            insights.get(field),
            list
        ):

            insights[field] = []

    return insights


# =========================================================
# BUILD PROMPT
# =========================================================

def build_prompt(
    research_package,
    total_personas,
    interview_stats
):

    survey_json = json.dumps(
        research_package[
            "surveyResearch"
        ],
        indent=2,
        ensure_ascii=False
    )

    personas_json = json.dumps(
        research_package[
            "personas"
        ],
        indent=2,
        ensure_ascii=False
    )

    individual_json = json.dumps(
        research_package[
            "individualInterviews"
        ],
        indent=2,
        ensure_ascii=False
    )

    all_persona_json = json.dumps(
        research_package[
            "allPersonaInterviews"
        ],
        indent=2,
        ensure_ascii=False
    )

    grouped_json = json.dumps(
        research_package[
            "allPersonaQuestionGroups"
        ],
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are an expert UX Research Insights Agent.

You are analyzing ONE CURRENT PRODUCT RESEARCH EXPERIMENT.

CURRENT EXPERIMENT SIZE:
{total_personas} personas

IMPORTANT RULES:

1. Analyze ONLY the data supplied in this prompt.
2. Do NOT assume there are 20 personas.
3. Do NOT create additional personas.
4. Do NOT use information from previous experiments.
5. Do NOT invent interview responses.
6. Every interview insight must be supported by an actual interview response.
7. Distinguish survey findings from interview findings.
8. Use survey buyDecision and rating for survey analysis.
9. Use actual interview answers for interview analysis.
10. Do not claim an interview occurred if no interview response exists.
11. If interview data is limited, clearly state that.
12. Agreement percentages must be based only on supplied interview data.
13. Do not make unsupported demographic assumptions.
14. Segment insights should use information actually present in persona data.
15. Keep findings concise and useful for a UX researcher.
16. Return ONLY valid JSON.
17. Do not wrap the JSON in markdown code fences.

==================================================
SURVEY DATA
==================================================

{survey_json}

==================================================
PERSONA DATA
==================================================

{personas_json}

==================================================
INDIVIDUAL INTERVIEW RESPONSES
==================================================

{individual_json}

==================================================
ALL-PERSONA INTERVIEW RESPONSES
==================================================

{all_persona_json}

==================================================
ALL-PERSONA QUESTION GROUPS
==================================================

{grouped_json}

==================================================
INTERVIEW COUNTS
==================================================

Individual responses:
{interview_stats["individualResponses"]}

Personas with individual interviews:
{interview_stats["individualPersonas"]}

All-persona questions:
{interview_stats["allPersonaQuestions"]}

All-persona responses:
{interview_stats["allPersonaResponses"]}

Personas represented in all-persona interviews:
{interview_stats["allPersonaPersonas"]}

Total interview data points:
{interview_stats["totalInterviewDataPoints"]}

==================================================
TASK
==================================================

Analyze the complete research.

Identify:

- Overall research summary
- Main product finding
- Positive signals
- Concerns
- Interview sentiment
- Recurring themes
- Interview discoveries
- Agreement patterns
- Disagreement patterns
- Behavioral trends
- Persona segments
- Survey vs interview relationships
- Individual persona findings

==================================================
REQUIRED JSON STRUCTURE
==================================================

{{
    "summary": "2-4 sentence overall research summary",

    "mainFinding": "The most important research finding",

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

==================================================
VALID VALUES
==================================================

surveyVsInterview.direction:

"Supports Survey"
"Challenges Survey"
"Adds Detail"

sentiment:

"Positive"
"Neutral"
"Negative"

==================================================
NO INTERVIEW DATA
==================================================

If there are zero interview responses:

themes = []

interviewDiscoveries = []

agreementPatterns = []

disagreementPatterns = []

behavioralTrends = []

surveyVsInterview = []

individualPersonaInsights = []

sentiment must be:

{{
    "positive": 0,
    "neutral": 0,
    "negative": 0
}}

Do NOT invent interview findings.
"""


    return prompt


# =========================================================
# MAIN INSIGHTS AGENT
# =========================================================

def generate_insights(
    personas
):

    """
    Main Insights Agent.

    Combines:

    1. Survey responses
    2. Individual interviews
    3. All-persona interviews
    """

    # -----------------------------------------------------
    # Validate personas
    # -----------------------------------------------------

    if not isinstance(
        personas,
        list
    ) or not personas:

        raise Exception(
            "No current personas available "
            "for insights."
        )

    current_personas = (
        build_current_personas(
            personas
        )
    )

    total_personas = len(
        current_personas
    )

    print()
    print("========================================")
    print("          INSIGHTS AGENT")
    print("========================================")

    print(
        f"Current personas: {total_personas}"
    )

    # -----------------------------------------------------
    # Survey analysis
    # -----------------------------------------------------

    survey = (
        calculate_survey_statistics(
            current_personas
        )
    )

    print(
        "[Insights] Survey statistics:",
        survey
    )

    # -----------------------------------------------------
    # Interview extraction
    # -----------------------------------------------------

    interview_data = (
        extract_interviews(
            current_personas
        )
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
        interview_data[
            "stats"
        ]
    )

    print()
    print(
        "[Insights] Individual responses:",
        interview_stats[
            "individualResponses"
        ]
    )

    print(
        "[Insights] Individual personas:",
        interview_stats[
            "individualPersonas"
        ]
    )

    print(
        "[Insights] All-persona questions:",
        interview_stats[
            "allPersonaQuestions"
        ]
    )

    print(
        "[Insights] All-persona responses:",
        interview_stats[
            "allPersonaResponses"
        ]
    )

    # -----------------------------------------------------
    # Build research package
    # -----------------------------------------------------

    research_package = {

        "surveyResearch": {

            "totalPersonas":
                survey[
                    "totalPersonas"
                ],

            "preferred":
                survey[
                    "preferred"
                ],

            "notPreferred":
                survey[
                    "notPreferred"
                ],

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
    # Determine interview availability
    # -----------------------------------------------------

    no_interviews = (

        len(
            individual_interviews
        ) == 0

        and

        len(
            all_persona_interviews
        ) == 0
    )

    if no_interviews:

        print()
        print(
            "[Insights] No interview records found."
        )

    else:

        print()
        print(
            "[Insights] Interview data detected."
        )

    # -----------------------------------------------------
    # Build Gemini prompt
    # -----------------------------------------------------

    prompt = build_prompt(
        research_package,
        total_personas,
        interview_stats
    )

    print()
    print(
        "[Insights] Prompt prepared."
    )

    print(
        "[Insights] Prompt length:",
        len(prompt),
        "characters"
    )

    # -----------------------------------------------------
    # Call Gemini
    # -----------------------------------------------------

    response = call_gemini(
        prompt
    )

    # -----------------------------------------------------
    # Parse response
    # -----------------------------------------------------

    insights = parse_json_response(
        response
    )

    # -----------------------------------------------------
    # Normalize response
    # -----------------------------------------------------

    insights = normalize_insights(
        insights
    )

    # -----------------------------------------------------
    # If no interviews, force empty interview data
    # -----------------------------------------------------

    if no_interviews:

        insights["sentiment"] = {

            "positive":
                0,

            "neutral":
                0,

            "negative":
                0
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
    # ALWAYS calculate product score in Python
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
    # Ensure summary
    # -----------------------------------------------------

    if not str(
        insights.get(
            "summary",
            ""
        )
    ).strip():

        insights["summary"] = (

            f"Out of "
            f"{survey['totalPersonas']} "
            f"personas, "
            f"{survey['wouldUsePercentage']}% "
            f"indicated that they would use "
            f"or purchase the product."
        )

    # -----------------------------------------------------
    # Ensure main finding
    # -----------------------------------------------------

    if not str(
        insights.get(
            "mainFinding",
            ""
        )
    ).strip():

        insights["mainFinding"] = (

            f"{survey['preferred']} of "
            f"{survey['totalPersonas']} "
            f"personas preferred the product."
        )

    # -----------------------------------------------------
    # Final debug output
    # -----------------------------------------------------

    print()
    print("========================================")
    print("       INSIGHTS GENERATED")
    print("========================================")

    print(
        f"Personas: {total_personas}"
    )

    print(
        "Product score:",
        survey[
            "wouldUsePercentage"
        ],
        "%"
    )

    print(
        "Individual interviews:",
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

    print(
        "Total interview data points:",
        interview_stats[
            "totalInterviewDataPoints"
        ]
    )

    print("========================================")
    print()

    return insights