from flask import Flask, request, jsonify, send_file
import json
import os
import re
import time

from flask_cors import CORS

from agent import (
    generate_personas,
    interview_persona,
    interview_all_personas,
)

from insights_agent import generate_insights
from ask_research import answer_research_question
from report_generator import generate_research_report


# =========================================================
# FILE LOCATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")
MAX_PERSONAS = 100


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# MEMORY HELPERS FOR ASK RESEARCH
# =========================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "personas": {},
            "allPersonaInterviews": [],
            "askResearchHistory": [],
        }

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            content = file.read().strip()

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
    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            memory,
            file,
            indent=2,
            ensure_ascii=False,
        )


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "Persona Generator Backend Running",
            "status": "success",
        }
    ), 200


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

        count = data.get("count", 20)

        if not product:
            return jsonify(
                {"error": "Product name is required."}
            ), 400

        if not description:
            return jsonify(
                {"error": "Product description is required."}
            ), 400

        if not age:
            return jsonify(
                {"error": "Target audience age is required."}
            ), 400

        if not objective:
            return jsonify(
                {"error": "Research objective is required."}
            ), 400

        try:
            count = int(count)
        except (ValueError, TypeError):
            count = 20

        if count < 1:
            count = 1

        if count > MAX_PERSONAS:
            count = MAX_PERSONAS

        print()
        print("========================================")
        print("        PERSONA GENERATION")
        print("========================================")
        print("Product:", product)
        print("Gender:", gender)
        print("Age:", age)
        print("Persona count requested:", count)
        print("Maximum supported personas:", MAX_PERSONAS)
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
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("========================================")
        print()

        return jsonify({"error": str(e)}), 500


# =========================================================
# INDIVIDUAL PERSONA INTERVIEW
# =========================================================

@app.route("/interview", methods=["POST"])
def interview():
    try:
        data = request.get_json(
            silent=True
        ) or {}

        persona_id = data.get("personaId")

        question = str(
            data.get("question", "")
        ).strip()

        if not persona_id:
            return jsonify(
                {"error": "Persona ID is required."}
            ), 400

        if not question:
            return jsonify(
                {"error": "Question is required."}
            ), 400

        print()
        print("========================================")
        print("        INDIVIDUAL INTERVIEW")
        print("========================================")
        print("Persona:", persona_id)
        print("Question:", question)
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
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("========================================")
        print()

        return jsonify({"error": str(e)}), 500


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
            data.get("question", "")
        ).strip()

        personas = data.get(
            "personas",
            [],
        )

        if not question:
            return jsonify(
                {"error": "Question is required."}
            ), 400

        if not isinstance(personas, list) or not personas:
            return jsonify(
                {"error": "No current personas were provided."}
            ), 400

        valid_personas = [
            persona
            for persona in personas
            if isinstance(persona, dict)
            and str(
                persona.get("id", "")
            ).strip()
        ]

        if not valid_personas:
            return jsonify(
                {"error": "No valid personas were provided."}
            ), 400

        print()
        print("========================================")
        print("         ALL-PERSONA INTERVIEW")
        print("========================================")
        print("Personas:", len(valid_personas))
        print("Question:", question)
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
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("========================================")
        print()

        return jsonify({"error": str(e)}), 500


# =========================================================
# FALLBACK INSIGHTS
# =========================================================

def create_fallback_insights(personas):
    total = len(personas)

    preferred = 0
    not_preferred = 0
    ratings = []

    for persona in personas:
        if not isinstance(persona, dict):
            continue

        decision = str(
            persona.get("buyDecision", "")
        ).strip().lower()

        if decision == "yes":
            preferred += 1

        elif decision == "no":
            not_preferred += 1

        try:
            rating = float(
                persona.get("rating", 0)
            )

            if 1 <= rating <= 5:
                ratings.append(rating)

        except (ValueError, TypeError):
            pass

    if preferred + not_preferred < total:
        not_preferred = total - preferred

    would_use_percentage = (
        round((preferred / total) * 100, 1)
        if total > 0
        else 0
    )

    average_rating = (
        round(sum(ratings) / len(ratings), 1)
        if ratings
        else 0
    )

    return {
        "summary": (
            f"{preferred} out of {total} personas indicated "
            f"that they would use or purchase the product, "
            f"representing {would_use_percentage}% of the "
            f"research sample."
        ),

        "mainFinding": (
            f"{would_use_percentage}% of personas would use "
            f"the product based on the survey."
        ),

        "positiveSignals": [
            f"{preferred} of {total} personas preferred the product.",
            f"The average product rating was {average_rating}/5.",
        ],

        "concerns": [
            f"{not_preferred} of {total} personas did not prefer the product."
        ],

        "sentiment": {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
        },

        "themes": [],
        "interviewDiscoveries": [],
        "agreementPatterns": [],
        "disagreementPatterns": [],
        "behavioralTrends": [],
        "segmentInsights": [],
        "surveyVsInterview": [],
        "individualPersonaInsights": [],

        "productScore": {
            "wouldUsePercentage": would_use_percentage,
            "preferred": preferred,
            "notPreferred": not_preferred,
            "totalPersonas": total,
            "averageRating": average_rating,
        },

        "interviewStats": {
            "individualResponses": 0,
            "individualPersonas": 0,
            "allPersonaQuestions": 0,
            "allPersonaResponses": 0,
            "allPersonaPersonas": 0,
            "totalInterviewDataPoints": 0,
            "hasIndividualInterviews": False,
            "hasAllPersonaInterviews": False,
        },

        "insightsStatus": "survey_only",

        "insightsMessage": (
            "Survey insights are available. AI interview analysis "
            "is temporarily unavailable because the Gemini API "
            "quota has been reached."
        ),
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
            [],
        )

        if not isinstance(personas, list) or not personas:
            return jsonify(
                {"error": "No current personas were provided."}
            ), 400

        valid_personas = [
            persona
            for persona in personas
            if isinstance(persona, dict)
            and str(
                persona.get("id", "")
            ).strip()
        ]

        if not valid_personas:
            return jsonify(
                {"error": "No valid current personas were provided."}
            ), 400

        print()
        print("========================================")
        print("          INSIGHTS AGENT STARTED")
        print("========================================")
        print(
            f"Analyzing {len(valid_personas)} current personas..."
        )
        print("========================================")
        print()

        try:
            result = generate_insights(
                valid_personas
            )

            if not isinstance(result, dict):
                raise Exception(
                    "Insights Agent returned an invalid response."
                )

            print("AI insights generated successfully.")

            return jsonify(result), 200

        except Exception as insights_error:
            error_text = str(insights_error)
            error_upper = error_text.upper()

            print()
            print("AI INSIGHTS ERROR")
            print("Error type:", type(insights_error).__name__)
            print("Error message:", error_text)

            quota_error = any(
                keyword in error_upper
                for keyword in (
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "QUOTA",
                    "RATE LIMIT",
                    "FREE_TIER",
                    "GENERATEREQUESTS",
                )
            )

            if quota_error:
                fallback = create_fallback_insights(
                    valid_personas
                )

                return jsonify(fallback), 200

            temporary_error = any(
                keyword in error_upper
                for keyword in (
                    "503",
                    "UNAVAILABLE",
                    "TIMEOUT",
                    "DEADLINE",
                )
            )

            if temporary_error:
                fallback = create_fallback_insights(
                    valid_personas
                )

                fallback["insightsMessage"] = (
                    "Survey insights are available. "
                    "AI interview analysis is temporarily "
                    "unavailable. Please try again later."
                )

                return jsonify(fallback), 200

            raise

    except Exception as e:
        print()
        print("========================================")
        print("        INSIGHTS ENDPOINT ERROR")
        print("========================================")
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("========================================")
        print()

        return jsonify({"error": str(e)}), 500


# =========================================================
# RESEARCH REPORT GENERATION
# =========================================================

@app.route("/generate-report", methods=["POST"])
def generate_report():
    try:
        data = request.get_json(
            silent=True
        ) or {}

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

        personas = data.get(
            "personas",
            [],
        )

        # Optional: Results can pass already-generated AI insights.
        # This prevents a second Gemini request during PDF generation.
        insights = data.get("insights")

        if not isinstance(personas, list) or not personas:
            return jsonify(
                {"error": "No personas available for report."}
            ), 400

        valid_personas = [
            persona
            for persona in personas
            if isinstance(persona, dict)
        ]

        if not valid_personas:
            return jsonify(
                {"error": "No valid personas available for report."}
            ), 400

        print()
        print("========================================")
        print("        RESEARCH REPORT GENERATION")
        print("========================================")
        print("Product:", product or "Research Study")
        print("Personas:", len(valid_personas))
        print("========================================")
        print()

        # report_generator.py reads the current session's
        # Ask Research history from memory.json.
        pdf_buffer = generate_research_report(
            product=product,
            description=description,
            gender=gender,
            age=age,
            objective=objective,
            personas=valid_personas,
            insights=insights,
        )

        safe_product = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            product or "research",
        ).strip("_")

        filename = (
            f"{safe_product or 'research'}_report.pdf"
        )

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        print()
        print("========================================")
        print("       RESEARCH REPORT ERROR")
        print("========================================")
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("========================================")
        print()

        return jsonify({"error": str(e)}), 500


# =========================================================
# ASK YOUR RESEARCH
# =========================================================

@app.route("/ask-research", methods=["POST"])
def ask_research():
    try:
        data = request.get_json(
            silent=True
        ) or {}

        question = str(
            data.get("question", "")
        ).strip()

        personas = data.get(
            "personas",
            [],
        )

        if not question:
            return jsonify(
                {"error": "Question is required."}
            ), 400

        if not isinstance(personas, list) or not personas:
            return jsonify(
                {"error": "No current personas were provided."}
            ), 400

        valid_personas = [
            persona
            for persona in personas
            if isinstance(persona, dict)
            and str(
                persona.get("id", "")
            ).strip()
        ]

        if not valid_personas:
            return jsonify(
                {"error": "No valid current personas were provided."}
            ), 400

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

        # -----------------------------------------------------
        # SAVE ASK RESEARCH RESULT
        # -----------------------------------------------------
        # This is the important new part.
        #
        # Every Ask Research question and its result is saved
        # against the CURRENT research generation.
        #
        # The next /generate call clears this list, so results
        # from an older product cannot appear in a new report.
        # -----------------------------------------------------

        memory = load_memory()

        memory.setdefault(
            "askResearchHistory",
            [],
        )

        memory["askResearchHistory"].append(
            {
                "question": question,
                "result": result,
                "timestamp": time.time(),
                "personaCount": len(valid_personas),
            }
        )

        save_memory(memory)

        return jsonify(
            {
                **result,
                "savedToResearchHistory": True,
            }
        ), 200

    except Exception as e:
        print()
        print("========================================")
        print("       ASK YOUR RESEARCH ERROR")
        print("========================================")
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("========================================")
        print()

        return jsonify({"error": str(e)}), 500


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):
    return jsonify(
        {"error": "Endpoint not found."}
    ), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(
        {"error": "HTTP method not allowed."}
    ), 405


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    print()
    print("========================================")
    print("      PERSONA RESEARCH BACKEND")
    print("========================================")
    print("Server: http://127.0.0.1:5000")
    print("Status: Running")
    print("========================================")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
