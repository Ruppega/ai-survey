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

    default_memory = {
        "personas": {},
        "allPersonaInterviews": []
    }

    if not os.path.exists(MEMORY_FILE):
        return default_memory

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

        if not content:
            return default_memory

        memory = json.loads(content)

        if not isinstance(memory, dict):
            return default_memory

        if "personas" not in memory:
            memory["personas"] = {}

        if "allPersonaInterviews" not in memory:
            memory["allPersonaInterviews"] = []

        return memory

    except (
        json.JSONDecodeError,
        OSError
    ):

        return default_memory


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


def get_persona(persona_id):

    memory = load_memory()

    persona_data = memory["personas"].get(
        persona_id
    )

    if not persona_data:
        raise Exception(
            "Persona not found."
        )

    return persona_data


# =========================================================
# JSON CLEANING
# =========================================================

def parse_json_response(response):

    if hasattr(response, "text"):
        response = response.text

    response = str(response).strip()

    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        return json.loads(response)

    except json.JSONDecodeError:
        pass

    array_match = re.search(
        r"\[.*\]",
        response,
        re.DOTALL
    )

    if array_match:

        return json.loads(
            array_match.group()
        )

    object_match = re.search(
        r"\{.*\}",
        response,
        re.DOTALL
    )

    if object_match:

        return json.loads(
            object_match.group()
        )

    raise Exception(
        "Gemini did not return valid JSON."
    )


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

    except (
        ValueError,
        TypeError
    ):

        count = 20

    count = max(
        1,
        min(count, 20)
    )

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

name,
gender,
age,
occupation,
personality,
buyDecision,
rating,
reason

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

    personas = parse_json_response(
        response
    )

    if not isinstance(personas, list):

        raise Exception(
            "Gemini response is not a JSON array."
        )

    if len(personas) != count:

        raise Exception(
            f"Expected {count} personas, "
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

    # =====================================================
    # START NEW RESEARCH EXPERIMENT
    # =====================================================

    memory = load_memory()

    # IMPORTANT:
    # A new product generation starts a completely
    # new research experiment.

    # Remove previous personas.
    memory["personas"] = {}

    # Remove previous all-persona interview data.
    memory["allPersonaInterviews"] = []

    # =====================================================
    # VALIDATE AND SAVE PERSONAS
    # =====================================================

    for persona in personas:

        if not isinstance(
            persona,
            dict
        ):

            raise Exception(
                "Invalid persona format."
            )

        for field in required_fields:

            if field not in persona:

                raise Exception(
                    f"Persona "
                    f"'{persona.get('name', 'Unknown')}' "
                    f"is missing field: {field}"
                )

        # Normalize buy decision.

        persona["buyDecision"] = (
            "Yes"
            if str(
                persona["buyDecision"]
            ).lower() == "yes"
            else "No"
        )

        # Normalize rating.

        try:

            persona["rating"] = max(
                1,
                min(
                    int(persona["rating"]),
                    5
                )
            )

        except (
            ValueError,
            TypeError
        ):

            persona["rating"] = 3

        # Create unique persona ID.

        persona_id = str(
            uuid.uuid4()
        )

        persona["id"] = persona_id

        # Store persona with EMPTY
        # individual interview history.

        memory["personas"][persona_id] = {

            "profile": persona,

            "conversation": []

        }

    save_memory(memory)

    # =====================================================
    # BASIC SURVEY RESULTS
    # =====================================================

    preferred = sum(

        1
        for persona in personas

        if persona[
            "buyDecision"
        ].lower() == "yes"

    )

    not_preferred = (
        len(personas)
        - preferred
    )

    return {

        "preferred":
            preferred,

        "notPreferred":
            not_preferred,

        "total":
            len(personas),

        "personas":
            personas

    }


# =========================================================
# PERSONA HISTORY
# =========================================================

def build_history(conversation):

    if not conversation:

        return (
            "No previous conversation."
        )

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

def interview_persona(
    persona_id,
    question
):

    if not persona_id:

        raise Exception(
            "Persona ID is required."
        )

    question = str(
        question or ""
    ).strip()

    if not question:

        raise Exception(
            "Question cannot be empty."
        )

    memory = load_memory()

    persona_data = (
        memory["personas"]
        .get(persona_id)
    )

    if not persona_data:

        raise Exception(
            "Persona not found."
        )

    profile = persona_data[
        "profile"
    ]

    conversation = (
        persona_data.get(
            "conversation",
            []
        )
    )

    history = build_history(
        conversation
    )

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

    response = call_gemini(
        prompt
    )

    if hasattr(
        response,
        "text"
    ):

        response = response.text

    answer = str(
        response
    ).replace(
        "```",
        ""
    ).strip()

    if not answer:

        raise Exception(
            "Gemini returned an empty answer."
        )

    # =====================================================
    # SAVE ONLY INDIVIDUAL INTERVIEW
    # =====================================================

    conversation.append({

        "mode":
            "individual",

        "question":
            question,

        "answer":
            answer

    })

    persona_data[
        "conversation"
    ] = conversation

    save_memory(memory)

    return {

        "persona":
            profile,

        "question":
            question,

        "answer":
            answer,

        "conversation":
            conversation

    }


# =========================================================
# ALL PERSONAS - ONE GEMINI REQUEST
# =========================================================

def interview_all_personas(
    question,
    personas
):

    """
    Ask the same question to ONLY the
    current frontend personas.

    Gemini is called ONCE for the
    complete current persona set.

    Group interview responses are stored
    separately from individual interviews.
    """

    question = str(
        question or ""
    ).strip()

    if not question:

        raise Exception(
            "Question cannot be empty."
        )

    if (
        not isinstance(
            personas,
            list
        )
        or not personas
    ):

        raise Exception(
            "No current personas provided."
        )

    # =====================================================
    # VALIDATE CURRENT PERSONAS
    # =====================================================

    current_personas = []

    for persona in personas:

        if not isinstance(
            persona,
            dict
        ):

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
            "No valid current personas provided."
        )

    # =====================================================
    # BUILD PERSONA PROMPT
    # =====================================================

    persona_blocks = []

    for profile in current_personas:

        persona_id = str(
            profile.get(
                "id"
            )
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

    personas_text = "\n".join(
        persona_blocks
    )

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

    # =====================================================
    # ONE GEMINI REQUEST
    # =====================================================

    response = call_gemini(
        prompt
    )

    result = parse_json_response(
        response
    )

    if not isinstance(
        result,
        dict
    ):

        raise Exception(
            "Gemini returned an invalid "
            "multi-persona response."
        )

    raw_answers = result.get(
        "answers"
    )

    if not isinstance(
        raw_answers,
        list
    ):

        raise Exception(
            "Gemini response is missing "
            "the answers array."
        )

    # =====================================================
    # BUILD ANSWER MAP
    # =====================================================

    answer_map = {}

    for item in raw_answers:

        if not isinstance(
            item,
            dict
        ):

            continue

        persona_id = str(
            item.get(
                "personaId",
                ""
            )
        ).strip()

        answer = str(
            item.get(
                "answer",
                ""
            )
        ).strip()

        if persona_id and answer:

            answer_map[
                persona_id
            ] = answer

    current_ids = [

        str(
            persona.get(
                "id"
            )
        ).strip()

        for persona
        in current_personas

    ]

    missing = [

        persona_id

        for persona_id
        in current_ids

        if persona_id
        not in answer_map

    ]

    if missing:

        raise Exception(

            f"Gemini did not return "
            f"answers for {len(missing)} "
            f"current persona(s)."

        )

    # =====================================================
    # SAVE ALL-PERSONA INTERVIEW
    # =====================================================

    memory = load_memory()

    memory.setdefault(
        "allPersonaInterviews",
        []
    )

    all_persona_record = {

        "question":
            question,

        "responses":
            []

    }

    final_answers = []

    for profile in current_personas:

        persona_id = str(
            profile.get(
                "id"
            )
        ).strip()

        answer = answer_map[
            persona_id
        ]

        # IMPORTANT:
        # Do NOT add this answer to the
        # individual conversation.
        #
        # It belongs exclusively to
        # the all-persona interview.

        all_persona_record[
            "responses"
        ].append({

            "personaId":
                persona_id,

            "personaName":
                profile.get(
                    "name",
                    "Unknown"
                ),

            "answer":
                answer

        })

        final_answers.append({

            "persona":
                profile,

            "answer":
                answer

        })

    memory[
        "allPersonaInterviews"
    ].append(
        all_persona_record
    )

    save_memory(memory)

    return {

        "question":
            question,

        "answers":
            final_answers,

        "total":
            len(final_answers)

    }


# =========================================================
# INSIGHT EXTRACTION AGENT
# =========================================================

def extract_insights(personas):

    if (
        not isinstance(
            personas,
            list
        )
        or not personas
    ):

        raise Exception(
            "No personas provided for "
            "insight analysis."
        )

    # =====================================================
    # BASIC SURVEY STATISTICS
    # =====================================================

    total = len(personas)

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
        total
        - preferred
    )

    would_use_score = round(

        (
            preferred
            / total
        ) * 100,

        1

    )

    ratings = []

    for persona in personas:

        try:

            ratings.append(
                float(
                    persona.get(
                        "rating",
                        0
                    )
                )
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    average_rating = (

        round(
            sum(ratings)
            / len(ratings),
            1
        )

        if ratings

        else 0

    )

    # =====================================================
    # LOAD MEMORY
    # =====================================================

    memory = load_memory()

    current_persona_ids = set()

    for persona in personas:

        persona_id = str(
            persona.get(
                "id",
                ""
            )
        ).strip()

        if persona_id:

            current_persona_ids.add(
                persona_id
            )

    # =====================================================
    # BUILD INDIVIDUAL INTERVIEW DATA
    # =====================================================

    individual_interviews = {}

    persona_data = []

    for persona in personas:

        persona_id = str(
            persona.get(
                "id",
                ""
            )
        ).strip()

        conversation = []

        stored_persona = (
            memory
            .get(
                "personas",
                {}
            )
            .get(
                persona_id
            )
        )

        if stored_persona:

            conversation = (
                stored_persona
                .get(
                    "conversation",
                    []
                )
            )

        # -------------------------------------------------
        # Only keep TRUE individual interviews.
        #
        # This also protects against old memory entries
        # that may not contain a mode field.
        # -------------------------------------------------

        individual_conversation = []

        for item in conversation:

            if not isinstance(
                item,
                dict
            ):

                continue

            mode = item.get(
                "mode"
            )

            # New records explicitly use "individual".
            if mode == "individual":

                individual_conversation.append(
                    item
                )

            # Legacy records without mode are treated
            # as individual for compatibility.
            elif mode is None:

                individual_conversation.append(
                    item
                )

        persona_name = persona.get(
            "name",
            "Unknown Persona"
        )

        individual_interviews[
            persona_name
        ] = individual_conversation

        persona_data.append({

            "id":
                persona_id,

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
                ),

            "individualInterview":
                individual_conversation

        })

    # =====================================================
    # GET ALL-PERSONA INTERVIEWS
    # =====================================================

    all_persona_interviews = (
        memory.get(
            "allPersonaInterviews",
            []
        )
    )

    cleaned_all_interviews = []

    for interview in all_persona_interviews:

        if not isinstance(
            interview,
            dict
        ):

            continue

        responses = interview.get(
            "responses",
            []
        )

        if not isinstance(
            responses,
            list
        ):

            continue

        cleaned_responses = []

        for response in responses:

            if not isinstance(
                response,
                dict
            ):

                continue

            persona_id = str(
                response.get(
                    "personaId",
                    ""
                )
            ).strip()

            # Only include current personas.

            if persona_id in current_persona_ids:

                cleaned_responses.append({

                    "personaId":
                        persona_id,

                    "personaName":
                        response.get(
                            "personaName",
                            "Unknown"
                        ),

                    "answer":
                        response.get(
                            "answer",
                            ""
                        )

                })

        if cleaned_responses:

            cleaned_all_interviews.append({

                "question":
                    interview.get(
                        "question",
                        ""
                    ),

                "responses":
                    cleaned_responses

            })

    # =====================================================
    # BUILD COMPLETE RESEARCH PACKAGE
    # =====================================================

    research_package = {

        "surveyResearch": {

            "totalPersonas":
                total,

            "preferred":
                preferred,

            "notPreferred":
                not_preferred,

            "wouldUsePercentage":
                would_use_score,

            "averageRating":
                average_rating,

            "personas":
                persona_data

        },

        "individualInterviews":
            individual_interviews,

        "allPersonaInterviews":
            cleaned_all_interviews

    }

    research_data = json.dumps(

        research_package,

        indent=2,

        ensure_ascii=False

    )

    # =====================================================
    # INSIGHT AGENT PROMPT
    # =====================================================

    prompt = f"""
You are an expert UX Research Insight Extraction Agent.

You are analyzing research collected from THREE sources:

1. Persona survey responses
2. Individual persona interviews
3. All-persona group interviews

Your job is to produce clear, visualizable,
evidence-based product insights.

===========================================================
IMPORTANT
===========================================================

Do NOT analyze only the survey.

Interview information is extremely important.

You MUST analyze:

- Survey responses
- Individual interviews
- All-persona interviews

when available.

You must clearly distinguish between them.

Do not invent information.

===========================================================
RESEARCH DATA
===========================================================

{research_data}


===========================================================
A. SURVEY ANALYSIS
===========================================================

Analyze:

- Would-use percentage
- Buy decisions
- Ratings
- Survey reasons
- Persona characteristics


===========================================================
B. INDIVIDUAL INTERVIEW ANALYSIS
===========================================================

Analyze each persona's individual interview.

Identify:

- Important opinions
- Motivations
- Concerns
- Feature preferences
- Objections
- Usage expectations
- Purchase motivations
- New information discovered during interview
- Changes compared with the original survey reason

If there are no individual interviews,
do not invent them.


===========================================================
C. ALL-PERSONA INTERVIEW ANALYSIS
===========================================================

Analyze the responses given by multiple personas
to the same questions.

Identify:

- Strong agreement
- Moderate agreement
- Disagreement
- Minority opinions
- Repeated concerns
- Repeated positive reactions
- Common feature requests
- Differences between persona groups


===========================================================
D. SURVEY VS INTERVIEW COMPARISON
===========================================================

Compare the original survey results with interview evidence.

Look for:

1. Survey YES + interview supports YES
2. Survey NO + interview supports NO
3. Survey YES + interview reveals concerns
4. Survey NO + interview reveals possible interest

Only report contradictions when they are supported.

Do not invent contradictions.


===========================================================
E. BEHAVIORAL PATTERNS
===========================================================

Identify meaningful behavioral patterns involving:

- Price sensitivity
- Feature priorities
- Convenience
- Trust
- Quality
- Usage habits
- Purchase motivation
- Product concerns
- Switching behavior
- Decision factors

Only include patterns supported by the data.


===========================================================
F. SENTIMENT
===========================================================

Estimate sentiment across the available research.

Return:

positive
neutral
negative

The three values MUST add up to exactly 100.


===========================================================
G. RECURRING THEMES
===========================================================

Identify 3 to 6 meaningful recurring themes.

Each theme must contain:

- theme
- agreement
- sentiment
- description

The agreement value should represent the approximate
percentage of current personas whose evidence supports
the theme.

Use only evidence from the research.


===========================================================
H. INTERVIEW DISCOVERIES
===========================================================

Identify important findings that were discovered
through interviews.

Classify each as:

positive
neutral
negative
contradiction

Each discovery must contain:

- type
- title
- description
- evidence

Evidence should briefly explain which interview responses
support the discovery.


===========================================================
I. AGREEMENT PATTERNS
===========================================================

Identify the strongest areas of agreement.

Each item must contain:

- topic
- percentage
- description

Use approximate percentages only when supported by
the number of personas.


===========================================================
J. DISAGREEMENT PATTERNS
===========================================================

Identify meaningful areas where personas differ.

Each item must contain:

- topic
- description


===========================================================
K. BEHAVIORAL TRENDS
===========================================================

Identify 3 to 6 behavioral trends.

Each should be concise and evidence-based.


===========================================================
L. SEGMENT INSIGHTS
===========================================================

Create meaningful persona segments using:

- Age
- Occupation
- Personality
- Buying behavior
- Interview behavior
- Feature priorities

For each segment return:

- segment
- personaCount
- wouldUsePercentage
- averageRating
- reasoning


===========================================================
M. SURVEY VS INTERVIEW
===========================================================

Identify important topics where interviews:

- Support the survey
- Challenge the survey
- Add detail to the survey

Return:

- topic
- surveySignal
- interviewSignal
- interpretation
- direction

Direction MUST be exactly one of:

"Supports Survey"

"Challenges Survey"

"Adds Detail"


===========================================================
N. RESEARCH CONCLUSION
===========================================================

The final summary should answer:

- Do users appear interested in the product?
- Why?
- What are the strongest positive signals?
- What are the biggest concerns?
- What did interviews reveal that the survey did not?
- Are there meaningful differences between personas?
- What should the product team pay attention to?


===========================================================
RETURN ONLY VALID JSON
===========================================================

Return EXACTLY this structure:

{{
  "summary": "",

  "sentiment": {{
    "positive": 0,
    "neutral": 0,
    "negative": 0
  }},

  "themes": [
    {{
      "theme": "",
      "agreement": 0,
      "sentiment": "",
      "description": ""
    }}
  ],

  "interviewDiscoveries": [
    {{
      "type": "",
      "title": "",
      "description": "",
      "evidence": ""
    }}
  ],

  "agreementPatterns": [
    {{
      "topic": "",
      "percentage": 0,
      "description": ""
    }}
  ],

  "disagreementPatterns": [
    {{
      "topic": "",
      "description": ""
    }}
  ],

  "behavioralTrends": [
    ""
  ],

  "segmentInsights": [
    {{
      "segment": "",
      "personaCount": 0,
      "wouldUsePercentage": 0,
      "averageRating": 0,
      "reasoning": ""
    }}
  ],

  "surveyVsInterview": [
    {{
      "topic": "",
      "surveySignal": "",
      "interviewSignal": "",
      "interpretation": "",
      "direction": ""
    }}
  ]
}}


===========================================================
FINAL RULES
===========================================================

1. Use ONLY information supported by the research data.
2. Do not invent persona opinions.
3. Do not invent interview responses.
4. Do not invent statistics.
5. Do not ignore interview data.
6. Clearly distinguish survey evidence from interview evidence.
7. Prioritize repeated patterns over isolated comments.
8. Highlight meaningful contradictions.
9. Keep descriptions concise.
10. Sentiment percentages MUST add up to 100.
11. Do not create fake interviews when interview data is empty.
12. If there are no interview responses, say so through the
    evidence rather than pretending interviews occurred.
"""

    # =====================================================
    # CALL GEMINI
    # =====================================================

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
            "Gemini returned invalid "
            "insight data."
        )

    # =====================================================
    # RELIABLE PRODUCT SCORE
    # =====================================================

    insights["productScore"] = {

        "wouldUsePercentage":
            would_use_score,

        "preferred":
            preferred,

        "notPreferred":
            not_preferred,

        "totalPersonas":
            total,

        "averageRating":
            average_rating

    }

    # =====================================================
    # INTERVIEW STATISTICS
    # =====================================================

    individual_count = sum(

        len(conversation)

        for conversation
        in individual_interviews.values()

    )

    all_persona_question_count = len(
        cleaned_all_interviews
    )

    personas_with_individual_interviews = sum(

        1

        for conversation
        in individual_interviews.values()

        if conversation

    )

    personas_with_group_interviews = set()

    for interview in cleaned_all_interviews:

        for response in interview.get(
            "responses",
            []
        ):

            persona_id = response.get(
                "personaId"
            )

            if persona_id:

                personas_with_group_interviews.add(
                    persona_id
                )

    insights["interviewStats"] = {

        "individualInterviewResponses":
            individual_count,

        "allPersonaQuestions":
            all_persona_question_count,

        "personasInterviewed":
            personas_with_individual_interviews,

        "personasInAllPersonaInterviews":
            len(
                personas_with_group_interviews
            ),

        "hasIndividualInterviews":
            individual_count > 0,

        "hasAllPersonaInterviews":
            all_persona_question_count > 0

    }

    return insights