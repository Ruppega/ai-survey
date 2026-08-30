from flask import Flask, request, jsonify
from flask_cors import CORS

from agent import (
    generate_personas,
    interview_persona,
    interview_all_personas,
    extract_insights,
)


app = Flask(__name__)
CORS(app)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "message": "Persona Generator Backend Running"
    })


# =========================================================
# GENERATE PERSONAS
# =========================================================

@app.route("/generate", methods=["POST"])
def generate():

    try:

        data = request.get_json() or {}

        result = generate_personas(

            product=data.get("product", ""),

            description=data.get("description", ""),

            gender=data.get("gender", "Both"),

            age=data.get("age", ""),

            objective=data.get("objective", ""),

            count=data.get("count", 20),

        )

        return jsonify(result), 200

    except Exception as e:

        print("Generate error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# INDIVIDUAL PERSONA INTERVIEW
# =========================================================

@app.route("/interview", methods=["POST"])
def interview():

    try:

        data = request.get_json() or {}

        result = interview_persona(

            persona_id=data.get("personaId"),

            question=data.get("question"),

        )

        return jsonify(result), 200

    except Exception as e:

        print("Individual interview error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# ALL PERSONAS INTERVIEW
# =========================================================

@app.route("/interview-all", methods=["POST"])
def interview_all():

    try:

        data = request.get_json() or {}

        question = str(
            data.get("question", "")
        ).strip()

        personas = data.get(
            "personas",
            []
        )

        if not question:

            return jsonify({
                "error": "Question is required."
            }), 400


        if not isinstance(personas, list) or not personas:

            return jsonify({
                "error": "No current personas were provided."
            }), 400


        result = interview_all_personas(

            question=question,

            personas=personas,

        )

        return jsonify(result), 200

    except Exception as e:

        print("All-persona interview error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# INSIGHT EXTRACTION AGENT
# =========================================================

@app.route("/insights", methods=["POST"])
def insights():

    try:

        data = request.get_json() or {}

        personas = data.get(
            "personas",
            []
        )

        if not isinstance(personas, list) or not personas:

            return jsonify({
                "error": "No personas provided for insight analysis."
            }), 400


        result = extract_insights(
            personas
        )

        return jsonify(result), 200

    except Exception as e:

        print("Insight extraction error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )