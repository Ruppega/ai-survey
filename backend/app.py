from flask import Flask, request, jsonify
from flask_cors import CORS

from agent import (
    generate_personas,
    interview_persona,
    interview_all_personas,
)

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "message": "Persona Generator Backend Running"
    })


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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


@app.route("/interview-all", methods=["POST"])
def interview_all():
    """
    Ask the same question to the CURRENT personas only.

    The frontend sends the personas generated for the currently
    selected product. The backend passes that exact list to the
    interview agent, so previous product personas are not reused.
    Gemini is called once for the whole current persona set.
    """
    try:
        data = request.get_json() or {}

        question = data.get("question", "").strip()
        personas = data.get("personas", [])

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
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )