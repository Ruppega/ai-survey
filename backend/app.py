from flask import Flask, request, jsonify
from flask_cors import CORS

from agent import (
    generate_personas,
    interview_persona,
    interview_all_personas,
)

from insights_agent import generate_insights
from ask_research import answer_research_question


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Persona Generator Backend Running",
        "status": "success"
    }), 200


# =========================================================
# GENERATE PERSONAS
# =========================================================

@app.route("/generate", methods=["POST"])
def generate():

    try:

        data = request.get_json(silent=True) or {}

        product = str(
            data.get("product", "")
        ).strip()

        description = str(
            data.get("description", "")
        ).strip()

        gender = str(
            data.get("gender", "Both")
        ).strip()

        age = str(
            data.get("age", "")
        ).strip()

        objective = str(
            data.get("objective", "")
        ).strip()

        count = data.get(
            "count",
            20
        )

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        if not product:

            return jsonify({
                "error": "Product name is required."
            }), 400

        if not description:

            return jsonify({
                "error": "Product description is required."
            }), 400

        if not age:

            return jsonify({
                "error": "Target audience age is required."
            }), 400

        if not objective:

            return jsonify({
                "error": "Research objective is required."
            }), 400

        # -----------------------------------------------------
        # VALIDATE COUNT
        # -----------------------------------------------------

        try:

            count = int(count)

        except (
            ValueError,
            TypeError
        ):

            count = 20

        if count < 1:

            count = 1

        if count > 100:

            count = 100

        # -----------------------------------------------------
        # GENERATE PERSONAS
        # -----------------------------------------------------

        print()
        print("========================================")
        print("        PERSONA GENERATION")
        print("========================================")

        print(
            f"Product: {product}"
        )

        print(
            f"Gender: {gender}"
        )

        print(
            f"Age: {age}"
        )

        print(
            f"Persona count: {count}"
        )

        print("========================================")
        print()

        result = generate_personas(

            product=product,

            description=description,

            gender=gender,

            age=age,

            objective=objective,

            count=count,

        )

        return jsonify(result), 200

    except Exception as e:

        print()
        print("========================================")
        print("        GENERATE PERSONAS ERROR")
        print("========================================")

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error message:",
            str(e)
        )

        print("========================================")
        print()

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# INDIVIDUAL PERSONA INTERVIEW
# =========================================================

@app.route("/interview", methods=["POST"])
def interview():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        persona_id = data.get(
            "personaId"
        )

        question = str(
            data.get(
                "question",
                ""
            )
        ).strip()

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        if not persona_id:

            return jsonify({
                "error": "Persona ID is required."
            }), 400

        if not question:

            return jsonify({
                "error": "Question is required."
            }), 400

        # -----------------------------------------------------
        # INTERVIEW
        # -----------------------------------------------------

        print()
        print("========================================")
        print("        INDIVIDUAL INTERVIEW")
        print("========================================")

        print(
            "Persona:",
            persona_id
        )

        print(
            "Question:",
            question
        )

        print("========================================")
        print()

        result = interview_persona(

            persona_id=persona_id,

            question=question,

        )

        return jsonify(result), 200

    except Exception as e:

        print()
        print("========================================")
        print("     INDIVIDUAL INTERVIEW ERROR")
        print("========================================")

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error message:",
            str(e)
        )

        print("========================================")
        print()

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# ALL PERSONAS INTERVIEW
# =========================================================

@app.route("/interview-all", methods=["POST"])
def interview_all():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        question = str(
            data.get(
                "question",
                ""
            )
        ).strip()

        personas = data.get(
            "personas",
            []
        )

        # -----------------------------------------------------
        # VALIDATE QUESTION
        # -----------------------------------------------------

        if not question:

            return jsonify({
                "error": "Question is required."
            }), 400

        # -----------------------------------------------------
        # VALIDATE PERSONAS
        # -----------------------------------------------------

        if not isinstance(
            personas,
            list
        ) or not personas:

            return jsonify({
                "error": "No current personas were provided."
            }), 400

        # -----------------------------------------------------
        # VALIDATE PERSONA IDS
        # -----------------------------------------------------

        valid_personas = [

            persona

            for persona in personas

            if isinstance(
                persona,
                dict
            )

            and str(
                persona.get(
                    "id",
                    ""
                )
            ).strip()

        ]

        if not valid_personas:

            return jsonify({
                "error": "No valid personas were provided."
            }), 400

        # -----------------------------------------------------
        # ALL PERSONA INTERVIEW
        # -----------------------------------------------------

        print()
        print("========================================")
        print("         ALL-PERSONA INTERVIEW")
        print("========================================")

        print(
            "Personas:",
            len(valid_personas)
        )

        print(
            "Question:",
            question
        )

        print("========================================")
        print()

        result = interview_all_personas(

            question=question,

            personas=valid_personas,

        )

        return jsonify(result), 200

    except Exception as e:

        print()
        print("========================================")
        print("      ALL-PERSONA INTERVIEW ERROR")
        print("========================================")

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error message:",
            str(e)
        )

        print("========================================")
        print()

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# FALLBACK INSIGHTS
# =========================================================

def create_fallback_insights(personas):

    """
    Creates useful survey-based insights when Gemini
    cannot be reached because of quota or temporary errors.

    This prevents the Insights page from completely failing.
    """

    total = len(personas)

    preferred = 0

    not_preferred = 0

    ratings = []

    # -----------------------------------------------------
    # SURVEY CALCULATION
    # -----------------------------------------------------

    for persona in personas:

        if not isinstance(
            persona,
            dict
        ):

            continue

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

            pass

    # -----------------------------------------------------
    # SAFETY CORRECTION
    # -----------------------------------------------------

    if preferred + not_preferred < total:

        not_preferred = (
            total - preferred
        )

    # -----------------------------------------------------
    # WOULD USE %
    # -----------------------------------------------------

    if total > 0:

        would_use_percentage = round(

            (
                preferred /
                total
            ) * 100,

            1

        )

    else:

        would_use_percentage = 0

    # -----------------------------------------------------
    # AVERAGE RATING
    # -----------------------------------------------------

    if ratings:

        average_rating = round(

            sum(ratings) /
            len(ratings),

            1

        )

    else:

        average_rating = 0

    # -----------------------------------------------------
    # RETURN FALLBACK
    # -----------------------------------------------------

    return {

        "summary":
            f"{preferred} out of {total} personas "
            f"indicated that they would use or purchase "
            f"the product, representing "
            f"{would_use_percentage}% of the research sample.",

        "mainFinding":
            f"{would_use_percentage}% of personas "
            f"would use the product based on the survey.",

        "positiveSignals": [

            f"{preferred} of {total} personas "
            f"preferred the product.",

            f"The average product rating was "
            f"{average_rating}/5."

        ],

        "concerns": [

            f"{not_preferred} of {total} personas "
            f"did not prefer the product."

        ],

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

        "individualPersonaInsights": [],

        # -------------------------------------------------
        # PRODUCT SCORE
        # -------------------------------------------------

        "productScore": {

            "wouldUsePercentage":
                would_use_percentage,

            "preferred":
                preferred,

            "notPreferred":
                not_preferred,

            "totalPersonas":
                total,

            "averageRating":
                average_rating

        },

        # -------------------------------------------------
        # INTERVIEW STATS
        # -------------------------------------------------

        "interviewStats": {

            "individualResponses": 0,

            "individualPersonas": 0,

            "allPersonaQuestions": 0,

            "allPersonaResponses": 0,

            "allPersonaPersonas": 0,

            "totalInterviewDataPoints": 0,

            "hasIndividualInterviews": False,

            "hasAllPersonaInterviews": False

        },

        # -------------------------------------------------
        # IMPORTANT STATUS
        # -------------------------------------------------

        "insightsStatus":
            "survey_only",

        "insightsMessage":
            "Survey insights are available. "
            "AI interview analysis is temporarily "
            "unavailable because the Gemini API quota "
            "has been reached."

    }


# =========================================================
# INSIGHT EXTRACTION AGENT
# =========================================================

@app.route("/insights", methods=["POST"])
def insights():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        personas = data.get(
            "personas",
            []
        )

        # -----------------------------------------------------
        # VALIDATE PERSONAS
        # -----------------------------------------------------

        if not isinstance(
            personas,
            list
        ) or not personas:

            return jsonify({
                "error": "No current personas were provided."
            }), 400

        # -----------------------------------------------------
        # VALID PERSONAS ONLY
        # -----------------------------------------------------

        valid_personas = [

            persona

            for persona in personas

            if isinstance(
                persona,
                dict
            )

            and str(
                persona.get(
                    "id",
                    ""
                )
            ).strip()

        ]

        if not valid_personas:

            return jsonify({
                "error": "No valid current personas were provided."
            }), 400

        # -----------------------------------------------------
        # START INSIGHTS
        # -----------------------------------------------------

        print()
        print("========================================")
        print("          INSIGHTS AGENT STARTED")
        print("========================================")

        print(
            f"Analyzing {len(valid_personas)} "
            f"current personas..."
        )

        print("========================================")
        print()

        # -----------------------------------------------------
        # RUN AI INSIGHTS AGENT
        # -----------------------------------------------------

        try:

            result = generate_insights(
                valid_personas
            )

            # -------------------------------------------------
            # VALIDATE RESULT
            # -------------------------------------------------

            if not isinstance(
                result,
                dict
            ):

                raise Exception(
                    "Insights Agent returned "
                    "an invalid response."
                )

            print()
            print("========================================")
            print("       INSIGHTS AGENT SUCCESS")
            print("========================================")

            print(
                "AI insights generated successfully."
            )

            print("========================================")
            print()

            return jsonify(
                result
            ), 200

        except Exception as insights_error:

            error_text = str(
                insights_error
            )

            error_upper = (
                error_text.upper()
            )

            print()
            print("========================================")
            print("       AI INSIGHTS ERROR")
            print("========================================")

            print(
                "Error type:",
                type(insights_error).__name__
            )

            print(
                "Error message:",
                error_text
            )

            print("========================================")
            print()

            # -------------------------------------------------
            # GEMINI QUOTA / RATE LIMIT
            # -------------------------------------------------

            quota_error = any(

                keyword in error_upper

                for keyword in [

                    "429",

                    "RESOURCE_EXHAUSTED",

                    "QUOTA",

                    "RATE LIMIT",

                    "FREE_TIER",

                    "GENERATEREQUESTS"

                ]

            )

            if quota_error:

                print(
                    "[Insights] Gemini quota "
                    "limit detected."
                )

                print(
                    "[Insights] Returning "
                    "survey-based fallback."
                )

                fallback = (
                    create_fallback_insights(
                        valid_personas
                    )
                )

                return jsonify(
                    fallback
                ), 200

            # -------------------------------------------------
            # TEMPORARY GEMINI ERROR
            # -------------------------------------------------

            temporary_error = any(

                keyword in error_upper

                for keyword in [

                    "503",

                    "UNAVAILABLE",

                    "TIMEOUT",

                    "DEADLINE"

                ]

            )

            if temporary_error:

                fallback = (
                    create_fallback_insights(
                        valid_personas
                    )
                )

                fallback[
                    "insightsMessage"
                ] = (
                    "Survey insights are available. "
                    "AI interview analysis is temporarily "
                    "unavailable. Please try again later."
                )

                return jsonify(
                    fallback
                ), 200

            # -------------------------------------------------
            # OTHER AI ERROR
            # -------------------------------------------------

            raise insights_error

    except Exception as e:

        print()
        print("========================================")
        print("        INSIGHTS ENDPOINT ERROR")
        print("========================================")

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error message:",
            str(e)
        )

        print("========================================")
        print()

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "error": "HTTP method not allowed."
    }), 405


# =========================================================
# START SERVER
# =========================================================


# =========================================================
# ASK YOUR RESEARCH
# =========================================================

@app.route("/ask-research", methods=["POST"])
def ask_research():
    try:
        data = request.get_json(silent=True) or {}

        question = str(
            data.get("question", "")
        ).strip()

        personas = data.get("personas", [])

        if not question:
            return jsonify({
                "error": "Question is required."
            }), 400

        if not isinstance(personas, list) or not personas:
            return jsonify({
                "error": "No current personas were provided."
            }), 400

        valid_personas = [
            persona
            for persona in personas
            if isinstance(persona, dict)
            and str(persona.get("id", "")).strip()
        ]

        if not valid_personas:
            return jsonify({
                "error": "No valid current personas were provided."
            }), 400

        print()
        print("========================================")
        print("          ASK YOUR RESEARCH")
        print("========================================")
        print("Personas:", len(valid_personas))
        print("Question:", question)
        print("========================================")
        print()

        result = answer_research_question(
            question=question,
            personas=valid_personas,
        )

        return jsonify(result), 200

    except Exception as e:
        print()
        print("========================================")
        print("       ASK YOUR RESEARCH ERROR")
        print("========================================")
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("========================================")
        print()

        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":

    print()
    print("========================================")
    print("      PERSONA RESEARCH BACKEND")
    print("========================================")

    print(
        "Server: http://127.0.0.1:5000"
    )

    print(
        "Status: Running"
    )

    print("========================================")
    print()

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )