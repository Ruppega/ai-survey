import { useState } from "react";
import axios from "axios";

function Interview({ persona }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setAnswer("");

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/interview",
        {
          personaId: persona.id,
          question: question
        }
      );

      setAnswer(response.data.answer);
    } catch (error) {
      console.error("Interview error:", error);

      setAnswer(
        "Unable to get a response from this persona."
      );
    }

    setLoading(false);
  };

  return (
    <div className="interview-container">

      <h2>🎤 Interview Persona</h2>

      <h3>{persona.name}</h3>

      <p>
        Ask {persona.name} a question and see how this
        persona responds.
      </p>

      <input
        type="text"
        placeholder="Ask a question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <button
        onClick={askQuestion}
        disabled={loading}
      >
        {loading ? "Thinking..." : "Ask"}
      </button>

      {answer && (
        <div className="answer-box">

          <strong>{persona.name}:</strong>

          <p>{answer}</p>

        </div>
      )}

    </div>
  );
}

export default Interview;