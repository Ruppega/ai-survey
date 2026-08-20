import { useState } from "react";
import axios from "axios";
import "./Interview.css";

function Interview({
  personas,
  selectedPersona,
  onSelectPersona
}) {
  const [question, setQuestion] = useState("");
  const [askedQuestion, setAskedQuestion] = useState("");
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("individual");

  // =====================================================
  // SELECT PERSONA
  // =====================================================

  const selectPersona = (persona) => {
    onSelectPersona(persona);
    setMode("individual");
    setAnswers([]);
    setAskedQuestion("");
  };

  // =====================================================
  // INDIVIDUAL INTERVIEW
  // =====================================================

  const askSelectedPersona = async () => {
    if (!selectedPersona) {
      alert("Please select a persona first.");
      return;
    }

    if (!question.trim() || loading) {
      return;
    }

    setLoading(true);
    setAnswers([]);

    const currentQuestion = question.trim();

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/interview",
        {
          personaId: selectedPersona.id,
          question: currentQuestion
        }
      );

      setAskedQuestion(currentQuestion);

      setAnswers([
        {
          persona: selectedPersona,
          answer: response.data.answer
        }
      ]);

      setQuestion("");
    } catch (error) {
      console.error("Individual interview error:", error);

      alert(
        error.response?.data?.error ||
        "Unable to get a response from this persona."
      );
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // ALL PERSONAS - ONE BACKEND REQUEST
  // =====================================================

  const askAllPersonas = async () => {
    if (!question.trim() || loading) {
      return;
    }

    if (!personas || personas.length === 0) {
      alert("No personas are available.");
      return;
    }

    setLoading(true);
    setAnswers([]);

    const currentQuestion = question.trim();

    try {
      // IMPORTANT:
      // This is ONE HTTP request.
      // The backend makes ONE Gemini request for all personas.
      const response = await axios.post(
        "http://127.0.0.1:5000/interview-all",
        {
          question: currentQuestion
        }
      );

      setAskedQuestion(currentQuestion);
      setAnswers(response.data.answers || []);
      setQuestion("");
    } catch (error) {
      console.error("All-persona interview error:", error);

      alert(
        error.response?.data?.error ||
        "Unable to get responses from all personas."
      );
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // ENTER KEY
  // =====================================================

  const handleKeyDown = (e) => {
    if (e.key !== "Enter" || e.shiftKey) {
      return;
    }

    e.preventDefault();

    if (mode === "all") {
      askAllPersonas();
    } else {
      askSelectedPersona();
    }
  };

  return (
    <div className="interview-container">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <h2>🎤 AI Persona Interview</h2>

      <p>
        Interview one persona or ask the same question
        to all generated personas.
      </p>

      {/* ================================================= */}
      {/* MODE SWITCH */}
      {/* ================================================= */}

      <div className="interview-mode-switch">

        <button
          className={
            mode === "individual"
              ? "mode-btn active"
              : "mode-btn"
          }
          onClick={() => {
            setMode("individual");
            setAnswers([]);
            setAskedQuestion("");
          }}
        >
          👤 Individual Interview
        </button>

        <button
          className={
            mode === "all"
              ? "mode-btn active"
              : "mode-btn"
          }
          onClick={() => {
            setMode("all");
            onSelectPersona(null);
            setAnswers([]);
            setAskedQuestion("");
          }}
        >
          👥 Ask All Personas
        </button>

      </div>

      {/* ================================================= */}
      {/* PERSONA SELECTOR */}
      {/* ================================================= */}

      <div className="persona-selector">

        <h3>👥 Choose a Persona</h3>

        <div className="persona-selector-grid">

          {personas.map((persona, index) => (

            <button
              key={persona.id || index}
              className={
                selectedPersona?.id === persona.id &&
                mode === "individual"
                  ? "persona-select-btn selected"
                  : "persona-select-btn"
              }
              onClick={() => selectPersona(persona)}
            >

              <span className="selector-avatar">
                👤
              </span>

              <span>
                <strong>
                  {persona.name}
                </strong>

                <small>
                  {persona.age} years •{" "}
                  {persona.occupation}
                </small>
              </span>

            </button>

          ))}

        </div>

      </div>

      {/* ================================================= */}
      {/* SELECTED PERSONA */}
      {/* ================================================= */}

      {mode === "individual" && selectedPersona && (

        <div className="selected-persona">

          <div className="selected-persona-avatar">
            👤
          </div>

          <div>
            <h3>
              Interviewing: {selectedPersona.name}
            </h3>

            <p>
              {selectedPersona.age} years old
              {" • "}
              {selectedPersona.occupation}
            </p>

            <p>
              🧠 {selectedPersona.personality}
            </p>
          </div>

        </div>

      )}

      {/* ================================================= */}
      {/* ALL MODE INFO */}
      {/* ================================================= */}

      {mode === "all" && (

        <div className="selected-persona">

          <div className="selected-persona-avatar">
            👥
          </div>

          <div>
            <h3>
              Asking All Personas
            </h3>

            <p>
              One question will be sent to the backend,
              which generates answers for all personas
              in one Gemini request.
            </p>
          </div>

        </div>

      )}

      {/* ================================================= */}
      {/* QUESTION INPUT */}
      {/* ================================================= */}

      <div className="question-area">

        <input
          type="text"
          placeholder={
            mode === "all"
              ? "Ask the same question to all personas..."
              : selectedPersona
                ? `Ask ${selectedPersona.name} a question...`
                : "Select a persona first..."
          }
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={
            loading ||
            (mode === "individual" && !selectedPersona)
          }
        />

        <button
          onClick={
            mode === "all"
              ? askAllPersonas
              : askSelectedPersona
          }
          disabled={
            loading ||
            !question.trim() ||
            (mode === "individual" && !selectedPersona)
          }
        >
          {loading
            ? "Thinking..."
            : mode === "all"
              ? "Ask All Personas"
              : selectedPersona
                ? `Ask ${selectedPersona.name}`
                : "Select a Persona"}
        </button>

      </div>

      {/* ================================================= */}
      {/* LOADING */}
      {/* ================================================= */}

      {loading && (

        <div className="interview-loading">

          <h3>
            🧠 Generating responses...
          </h3>

          <p>
            {mode === "all"
              ? `Generating answers for ${personas.length} personas with one Gemini request...`
              : `${selectedPersona?.name} is thinking...`}
          </p>

        </div>

      )}

      {/* ================================================= */}
      {/* QUESTION */}
      {/* ================================================= */}

      {askedQuestion && !loading && (

        <div className="asked-question">

          <strong>
            ❓ Question:
          </strong>

          <p>
            {askedQuestion}
          </p>

        </div>

      )}

      {/* ================================================= */}
      {/* ANSWERS */}
      {/* ================================================= */}

      {answers.length > 0 && (

        <div className="answers-grid">

          {answers.map((item, index) => (

            <div
              className="interview-card"
              key={item.persona?.id || index}
            >

              <div className="persona-header">

                <div className="persona-avatar">
                  👤
                </div>

                <div>
                  <h3>
                    {item.persona?.name}
                  </h3>

                  <p>
                    {item.persona?.age} years old
                    {" • "}
                    {item.persona?.occupation}
                  </p>
                </div>

              </div>

              <div className="persona-info">

                <span>
                  🧠{" "}
                  {item.persona?.personality}
                </span>

                <span>
                  ⭐{" "}
                  {item.persona?.rating}/5
                </span>

              </div>

              <div className="answer-box">

                <strong>
                  💬 {item.persona?.name}:
                </strong>

                <p>
                  {item.answer}
                </p>

              </div>

            </div>

          ))}

        </div>

      )}

      {/* ================================================= */}
      {/* EMPTY STATE */}
      {/* ================================================= */}

      {!loading &&
        answers.length === 0 &&
        !askedQuestion && (

          <div className="interview-empty">

            <h3>
              {mode === "all"
                ? "👥 Ask All Personas"
                : "👤 Select a Persona"}
            </h3>

            <p>
              {mode === "all"
                ? "Ask one question and receive a distinct answer from every generated persona."
                : "Choose one persona above to start an individual AI interview."}
            </p>

          </div>

        )}

    </div>
  );
}

export default Interview;