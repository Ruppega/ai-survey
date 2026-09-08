import { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./AskResearch.css";

const SUGGESTED_QUESTIONS = [
  "What are the biggest reasons people would not use this product?",
  "Which personas are most positive about the product?",
  "Did the interviews support the survey results?",
  "What did people say about price or cost?",
  "What are the most important themes in the research?",
  "What should we improve based on the research?",
];

function AskResearch({ personas }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  const textareaRef = useRef(null);

  useEffect(() => {
    setQuestion("");
    setAnswer(null);
    setError("");
    setHistory([]);
  }, [personas]);

  const askQuestion = async (questionToAsk = question) => {
    const currentQuestion = questionToAsk.trim();

    if (!currentQuestion || loading) return;

    if (!personas || personas.length === 0) {
      setError(
        "Generate personas first so there is research data to analyze."
      );
      return;
    }

    setLoading(true);
    setError("");
    setQuestion(currentQuestion);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/ask-research",
        {
          question: currentQuestion,
          personas,
        }
      );

      const data = response.data;

      setAnswer(data);

      // Store the complete response so old questions
      // can restore their actual answer.
      setHistory((previous) => [
        {
          question: currentQuestion,
          response: data,
        },
        ...previous.filter(
          (item) => item.question !== currentQuestion
        ),
      ].slice(0, 5));
    } catch (err) {
      console.error("Ask Your Research error:", err);

      setAnswer(null);

      setError(
        err.response?.data?.error ||
          "Unable to analyze the research. Make sure the Flask backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const useSuggestion = (suggestion) => {
    setQuestion(suggestion);
    setError("");

    textareaRef.current?.focus();
  };

  const clearResearchAnswer = () => {
    setAnswer(null);
    setError("");
    setQuestion("");

    textareaRef.current?.focus();
  };

  const source =
    answer?.source === "ai"
      ? "AI analysis"
      : "Evidence fallback";

  return (
    <div className="ask-research-page">

      {/* =====================================================
          PAGE HEADER
      ====================================================== */}

      <header className="ask-research-header">

        <div className="ask-research-title-row">

          <div className="ask-research-title-icon">
            🔎
          </div>

          <div>
            <h1>Ask Your Research</h1>

            <p>
              Ask questions about what your synthetic participants actually said.
            </p>
          </div>

        </div>

        <div className="ask-research-data-pill">

          <span className="data-dot" />

          {personas?.length || 0} current personas

        </div>

      </header>


      {/* =====================================================
          INTRODUCTION
      ====================================================== */}

      <section className="ask-research-intro">

        <div className="intro-icon">
          💡
        </div>

        <div>

          <h2>
            Turn research data into answers
          </h2>

          <p>
            Ask questions in natural language. The research agent
            analyzes the current survey responses, individual interviews,
            and all-persona interviews to provide an evidence-grounded answer.
          </p>

        </div>

      </section>


      {/* =====================================================
          QUESTION INPUT
      ====================================================== */}

      <section className="ask-research-card ask-input-card">

        <div className="section-heading">

          <div>

            <span className="section-kicker">
              RESEARCH QUESTION
            </span>

            <h2>
              What do you want to know?
            </h2>

          </div>

          <span className="question-hint">
            Enter to ask • Shift + Enter for a new line
          </span>

        </div>


        <div className="research-input-wrap">

          <textarea
            ref={textareaRef}
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="e.g. What are the biggest barriers to using this product?"
            rows={4}
            maxLength={1000}
            disabled={loading}
          />


          <div className="input-bottom-row">

            <span className="character-count">
              {question.length}/1000
            </span>

            <button
              type="button"
              className="ask-button"
              onClick={() => askQuestion()}
              disabled={!question.trim() || loading}
            >

              {loading ? (
                <>
                  <span className="button-spinner" />
                  Analyzing...
                </>
              ) : (
                <>
                  Ask Research
                  <span className="ask-button-arrow">
                    →
                  </span>
                </>
              )}

            </button>

          </div>

        </div>


        {/* =================================================
            SUGGESTIONS
        ================================================== */}

        <div className="suggestions-block">

          <div className="suggestions-label">
            TRY ASKING
          </div>

          <div className="suggestions-grid">

            {SUGGESTED_QUESTIONS.map((suggestion) => (

              <button
                key={suggestion}
                type="button"
                className="suggestion-chip"
                onClick={() =>
                  useSuggestion(suggestion)
                }
                disabled={loading}
              >

                <span className="suggestion-arrow">
                  ↗
                </span>

                <span>
                  {suggestion}
                </span>

              </button>

            ))}

          </div>

        </div>

      </section>


      {/* =====================================================
          ERROR
      ====================================================== */}

      {error && (

        <div className="ask-error">

          <span className="error-icon">
            ⚠️
          </span>

          <div>

            <strong>
              Something went wrong
            </strong>

            <p>
              {error}
            </p>

          </div>

        </div>

      )}


      {/* =====================================================
          EMPTY STATE
      ====================================================== */}

      {!answer && !loading && !error && (

        <section className="ask-research-card ask-empty-state">

          <div className="empty-orbit">
            ✦
          </div>

          <h2>
            Your research answer will appear here
          </h2>

          <p>
            Ask a question above to uncover patterns,
            compare opinions, and understand what your
            participants are telling you.
          </p>


          <div className="empty-features">

            <span>
              ✓ Survey evidence
            </span>

            <span>
              ✓ Interview evidence
            </span>

            <span>
              ✓ Persona-level reasoning
            </span>

          </div>

        </section>

      )}


      {/* =====================================================
          LOADING STATE
      ====================================================== */}

      {loading && (

        <section className="ask-research-card loading-card">

          <div className="loading-animation">

            <div className="loading-orb">
              🔎
            </div>

          </div>

          <h2>
            Searching your research...
          </h2>

          <p>
            Checking survey responses and interview
            evidence for a grounded answer.
          </p>

          <div className="loading-lines">
            <span />
            <span />
            <span />
          </div>

        </section>

      )}


      {/* =====================================================
          ANSWER
      ====================================================== */}

      {answer && !loading && (

        <section className="answer-section">

          <div className="answer-top-row">

            <div>

              <span className="section-kicker">
                RESEARCH ANSWER
              </span>

              <h2>
                {answer.question}
              </h2>

            </div>


            <button
              type="button"
              className="clear-answer-btn"
              onClick={clearResearchAnswer}
            >
              + New question
            </button>

          </div>


          {/* =================================================
              MAIN ANSWER CARD
          ================================================== */}

          <div className="answer-card">

            <div className="answer-card-top">

              <div className="answer-icon">
                ✦
              </div>

              <div className="answer-meta">

                <span className="answer-label">
                  What the research says
                </span>

                <span
                  className={`confidence-badge ${
                    answer.confidence?.toLowerCase() ||
                    "medium"
                  }`}
                >
                  {answer.confidence || "Medium"} confidence
                </span>

              </div>

            </div>


            {/* MAIN ANSWER */}

            <p className="answer-text">
              {answer.answer}
            </p>


            {/* =================================================
                EVIDENCE HEADER
            ================================================== */}

            <div className="evidence-heading">

              <div>

                <h3>
                  Key evidence
                </h3>

                <p>
                  Evidence returned from the current research dataset
                </p>

              </div>

              <span className="source-badge">
                {source}
              </span>

            </div>


            {/* =================================================
                EVIDENCE LIST
            ================================================== */}

            {answer.keyEvidence?.length > 0 ? (

              <div className="evidence-list">

                {answer.keyEvidence.map(
                  (item, index) => (

                    <div
                      className="evidence-item"
                      key={`${item}-${index}`}
                    >

                      <span className="evidence-number">
                        {index + 1}
                      </span>

                      <p>
                        {item}
                      </p>

                    </div>

                  )
                )}

              </div>

            ) : (

              <div className="no-evidence">

                No specific evidence items were returned
                for this question.

              </div>

            )}


            {/* =================================================
                DATA SOURCE STATISTICS
            ================================================== */}

            <div className="source-grid">

              <div className="source-stat">

                <span className="source-stat-icon">
                  📋
                </span>

                <div>

                  <strong>
                    {answer.sources?.surveyResponses || 0}
                  </strong>

                  <small>
                    Survey responses
                  </small>

                </div>

              </div>


              <div className="source-stat">

                <span className="source-stat-icon">
                  👤
                </span>

                <div>

                  <strong>
                    {answer.sources?.individualInterviewResponses || 0}
                  </strong>

                  <small>
                    Individual interviews
                  </small>

                </div>

              </div>


              <div className="source-stat">

                <span className="source-stat-icon">
                  👥
                </span>

                <div>

                  <strong>
                    {answer.sources?.allPersonaInterviewResponses || 0}
                  </strong>

                  <small>
                    Group responses
                  </small>

                </div>

              </div>


              <div className="source-stat">

                <span className="source-stat-icon">
                  🧠
                </span>

                <div>

                  <strong>
                    {answer.sources?.totalEvidenceItems || 0}
                  </strong>

                  <small>
                    Evidence items
                  </small>

                </div>

              </div>

            </div>

          </div>

        </section>

      )}


      {/* =====================================================
          QUESTION HISTORY
      ====================================================== */}

      {history.length > 0 && (

        <section className="ask-research-card history-card">

          <div className="section-heading">

            <div>

              <span className="section-kicker">
                RECENT QUESTIONS
              </span>

              <h2>
                Your research trail
              </h2>

            </div>

            <span className="history-count">
              {history.length}
            </span>

          </div>


          <div className="history-list">

            {history.map((item, index) => (

              <button
                type="button"
                className="history-item"
                key={`${item.question}-${index}`}
                onClick={() => {
                  setQuestion(item.question);
                  setAnswer(item.response);
                  setError("");
                }}
              >

                <span className="history-index">
                  {index + 1}
                </span>

                <span className="history-question">
                  {item.question}
                </span>

                <span className="history-arrow">
                  →
                </span>

              </button>

            ))}

          </div>

        </section>

      )}

    </div>
  );
}

export default AskResearch;