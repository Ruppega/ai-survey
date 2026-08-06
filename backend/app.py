from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import generate_personas

app = Flask(__name__)

# Allow requests from React
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "message": "Persona Generator Backend Running"
    })


@app.route("/generate", methods=["POST"])
def generate():

    try:
        data = request.get_json()

        result = generate_personas(
            data["product"],
            data["description"],
            data["gender"],      # <-- NEW
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


if __name__ == "__main__":
    app.run(debug=True)