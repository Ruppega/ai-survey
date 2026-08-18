from flask import Flask, request, jsonify
from flask_cors import CORS

from agent import generate_personas, interview_persona


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# Allow React frontend to communicate with Flask backend
CORS(app)


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Persona Generator Backend Running",
        "status": "success"
    })


# =========================================================
# GENERATE PERSONAS
# =========================================================

@app.route("/generate", methods=["POST"])
def generate():

    try:

        # -------------------------------------------------
        # GET REQUEST DATA
        # -------------------------------------------------

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No data received."
            }), 400

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        required_fields = [
            "product",
            "description",
            "gender",
            "age",
            "objective",
            "count"
        ]

        for field in required_fields:

            if field not in data:

                return jsonify({
                    "error":
                        f"Missing required field: {field}"
                }), 400

        # -------------------------------------------------
        # READ VALUES
        # -------------------------------------------------

        product = str(
            data["product"]
        ).strip()

        description = str(
            data["description"]
        ).strip()

        gender = str(
            data["gender"]
        ).strip()

        age = str(
            data["age"]
        ).strip()

        objective = str(
            data["objective"]
        ).strip()

        # -------------------------------------------------
        # CONVERT COUNT TO INTEGER
        # -------------------------------------------------

        try:

            count = int(data["count"])

        except (ValueError, TypeError):

            return jsonify({
                "error":
                    "Count must be a number."
            }), 400

        # -------------------------------------------------
        # VALIDATE COUNT
        # -------------------------------------------------

        if count < 1 or count > 20:

            return jsonify({
                "error":
                    "Number of personas must be between 1 and 20."
            }), 400

        # -------------------------------------------------
        # GENERATE PERSONAS
        # -------------------------------------------------

        result = generate_personas(
            product,
            description,
            gender,
            age,
            objective,
            count
        )

        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return jsonify(result), 200

    except Exception as e:

        print(
            "GENERATE ERROR:",
            str(e)
        )

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# INTERVIEW MODE
# =========================================================

@app.route("/interview", methods=["POST"])
def interview():

    try:

        # -------------------------------------------------
        # GET REQUEST DATA
        # -------------------------------------------------

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "No interview data received."
            }), 400

        # -------------------------------------------------
        # CHECK PERSONA ID
        # -------------------------------------------------

        if "personaId" not in data:

            return jsonify({
                "error":
                    "personaId is required."
            }), 400

        # -------------------------------------------------
        # CHECK QUESTION
        # -------------------------------------------------

        if "question" not in data:

            return jsonify({
                "error":
                    "question is required."
            }), 400

        # -------------------------------------------------
        # READ VALUES
        # -------------------------------------------------

        persona_id = str(
            data["personaId"]
        ).strip()

        question = str(
            data["question"]
        ).strip()

        if not persona_id:

            return jsonify({
                "error":
                    "Persona ID cannot be empty."
            }), 400

        if not question:

            return jsonify({
                "error":
                    "Question cannot be empty."
            }), 400

        # -------------------------------------------------
        # INTERVIEW PERSONA
        # -------------------------------------------------

        result = interview_persona(
            persona_id,
            question
        )

        # -------------------------------------------------
        # RETURN RESPONSE
        # -------------------------------------------------

        return jsonify(result), 200

    except Exception as e:

        print(
            "INTERVIEW ERROR:",
            str(e)
        )

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "🧠 Persona AI Backend"
    )

    print(
        "========================================"
    )

    print(
        "Server running at:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "========================================"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )