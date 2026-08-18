import { useState } from "react";
import axios from "axios";

function Interview({
  personas,
  selectedPersona,
  onSelectPersona
}) {
  const [question, setQuestion] = useState("");
  const [askedQuestion, setAskedQuestion] = useState("");
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(false);

  // =====================================================
  // SELECT PERSONA
  // =====================================================

  const selectPersona = (persona) => {
    onSelectPersona(persona);

    // Clear old visible answers
    setAnswers([]);
    setAskedQuestion("");
    setQuestion("");
  };


  // =====================================================
  // ASK SELECTED PERSONA
  // =====================================================

  const askSelectedPersona = async () => {

    if (!selectedPersona) {
      alert("Please select a persona first.");
      return;
    }

    if (!question.trim()) {
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

      console.error(
        "Individual interview error:",
        error
      );

      alert(
        error.response?.data?.error ||
        "Unable to get a response from this persona."
      );

    } finally {

      setLoading(false);

    }
  };


  // =====================================================
  // ASK ALL PERSONAS
  // =====================================================

  const askAllPersonas = async () => {

    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setAnswers([]);

    const currentQuestion = question.trim();

    try {

      const requests = personas.map(
        (persona) =>
          axios.post(
            "http://127.0.0.1:5000/interview",
            {
              personaId: persona.id,
              question: currentQuestion
            }
          )
      );

      const responses = await Promise.all(
        requests
      );

      const newAnswers = responses.map(
        (response, index) => ({
          persona: personas[index],
          answer: response.data.answer
        })
      );

      setAskedQuestion(currentQuestion);
      setAnswers(newAnswers);

      setQuestion("");

    } catch (error) {

      console.error(
        "Multi-persona interview error:",
        error
      );

      alert(
        error.response?.data?.error ||
        "Unable to get responses from all personas."
      );

    } finally {

      setLoading(false);

    }
  };


  // =====================================================
  // HANDLE ENTER KEY
  // =====================================================

  const handleKeyDown = (e) => {

    if (e.key === "Enter") {

      if (e.shiftKey) {
        return;
      }

      e.preventDefault();

      if (selectedPersona) {
        askSelectedPersona();
      } else {
        askAllPersonas();
      }

    }
  };


  return (
    <div className="interview-container">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <h2>🎤 AI Persona Interview</h2>

      <p>
        Select a persona to interview individually,
        or ask the same question to everyone.
      </p>


      {/* ================================================= */}
      {/* PERSONA SELECTOR */}
      {/* ================================================= */}

      <div className="persona-selector">

        <h3>👥 Choose a Persona</h3>

        <div className="persona-selector-grid">

          {personas.map(
            (persona, index) => (

              <button
                key={persona.id || index}
                className={
                  selectedPersona?.id === persona.id
                    ? "persona-select-btn selected"
                    : "persona-select-btn"
                }
                onClick={() =>
                  selectPersona(persona)
                }
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

            )
          )}

        </div>


        {/* ================================================= */}
        {/* ALL PERSONAS BUTTON */}
        {/* ================================================= */}

        <button
          className={
            !selectedPersona
              ? "all-personas-btn selected"
              : "all-personas-btn"
          }
          onClick={() => {
            onSelectPersona(null);
            setAnswers([]);
            setAskedQuestion("");
          }}
        >
          👥 Ask All Personas
        </button>

      </div>


      {/* ================================================= */}
      {/* CURRENT PERSONA */}
      {/* ================================================= */}

      {selectedPersona && (

        <div className="selected-persona">

          <div className="selected-persona-avatar">
            👤
          </div>

          <div>

            <h3>
              Interviewing:{" "}
              {selectedPersona.name}
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
      {/* QUESTION INPUT */}
      {/* ================================================= */}

      <div className="question-area">

        <input
          type="text"
          placeholder={
            selectedPersona
              ? `Ask ${selectedPersona.name} a question...`
              : "Ask a question to all personas..."
          }
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
          onKeyDown={handleKeyDown}
          disabled={loading}
        />


        {/* INDIVIDUAL BUTTON */}

        {selectedPersona ? (

          <button
            onClick={askSelectedPersona}
            disabled={
              loading ||
              !question.trim()
            }
          >
            {loading
              ? "Thinking..."
              : `Ask ${selectedPersona.name}`}
          </button>

        ) : (

          /* ALL PERSONAS BUTTON */

          <button
            onClick={askAllPersonas}
            disabled={
              loading ||
              !question.trim()
            }
          >
            {loading
              ? "Personas are thinking..."
              : "Ask All Personas"}
          </button>

        )}

      </div>


      {/* ================================================= */}
      {/* LOADING */}
      {/* ================================================= */}

      {loading && (

        <div className="interview-loading">

          <h3>
            🧠 Generating response...
          </h3>

          <p>

            {selectedPersona
              ? `${selectedPersona.name} is thinking...`
              : `Asking ${personas.length} personas for their opinions...`
            }

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

          {answers.map(
            (item, index) => (

              <div
                className="interview-card"
                key={
                  item.persona.id ||
                  index
                }
              >

                {/* PERSONA HEADER */}

                <div className="persona-header">

                  <div className="persona-avatar">
                    👤
                  </div>

                  <div>

                    <h3>
                      {item.persona.name}
                    </h3>

                    <p>
                      {item.persona.age} years old
                      {" • "}
                      {item.persona.occupation}
                    </p>

                  </div>

                </div>


                {/* PERSONA DETAILS */}

                <div className="persona-info">

                  <span>
                    🧠{" "}
                    {item.persona.personality}
                  </span>

                  <span>
                    ⭐{" "}
                    {item.persona.rating}/5
                  </span>

                </div>


                {/* ANSWER */}

                <div className="answer-box">

                  <strong>
                    💬 {item.persona.name}:
                  </strong>

                  <p>
                    {item.answer}
                  </p>

                </div>

              </div>

            )
          )}

        </div>

      )}


      {/* ================================================= */}
      {/* NO PERSONA SELECTED MESSAGE */}
      {/* ================================================= */}

      {!selectedPersona &&
        !loading &&
        answers.length === 0 && (

          <div className="interview-empty">

            <h3>
              👥 Multi-Persona Mode
            </h3>

            <p>
              Ask a question to receive answers
              from all generated personas.
            </p>

            <p>
              Or select one persona above to
              interview them individually.
            </p>

          </div>

        )}

    </div>
  );
}

export default Interview;