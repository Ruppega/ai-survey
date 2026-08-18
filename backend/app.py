from flask import Flask, request, jsonify
from flask_cors import CORS

from agent import generate_personas, interview_persona


app = Flask(__name__)

# Allow requests from React
CORS(app)


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():

    return jsonify({
        "message": "Persona Generator Backend Running"
    })


# ---------------------------------------------------------
# GENERATE PERSONAS
# ---------------------------------------------------------

@app.route("/generate", methods=["POST"])
def generate():

    try:

        data = request.get_json()

        result = generate_personas(
            data["product"],
            data["description"],
            data["gender"],
            data["age"],
            data["objective"],
            int(data["count"])
        )

        return jsonify(result)

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ---------------------------------------------------------
# INTERVIEW MODE
# ---------------------------------------------------------

@app.route("/interview", methods=["POST"])
def interview():

    try:

        data = request.get_json()

        persona_id = data["personaId"]
        question = data["question"]

        result = interview_persona(
            persona_id,
            question
        )

        return jsonify(result)

    except Exception as e:

        print("INTERVIEW ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ---------------------------------------------------------
# START SERVER
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)