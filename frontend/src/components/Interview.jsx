import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./Interview.css";

function Interview({
  personas,
  selectedPersona,
  onSelectPersona,
  interviewMessages,
  setInterviewMessages
}) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("individual");

  const chatEndRef = useRef(null);

  // =========================================================
  // CURRENT CHAT
  // =========================================================

  const currentPersonaId = selectedPersona?.id;

  const messages =
    mode === "individual"
      ? interviewMessages[currentPersonaId] || []
      : interviewMessages.all || [];

  // =========================================================
  // RESET UI WHEN A COMPLETELY NEW PERSONA SET IS GENERATED
  // =========================================================

  useEffect(() => {
    setQuestion("");
    setLoading(false);
    setMode("individual");
  }, [personas]);

  // =========================================================
  // AUTO SCROLL
  // =========================================================

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages, loading]);

  // =========================================================
  // SELECT PERSONA
  // =========================================================

  const selectPersona = (persona) => {
    onSelectPersona(persona);

    setMode("individual");
    setQuestion("");

    // IMPORTANT:
    // Do NOT clear the persona's previous messages.
    //
    // If Persona 1 already has a conversation,
    // it will automatically appear again.
  };

  // =========================================================
  // SWITCH MODE
  // =========================================================

  const switchMode = (newMode) => {
    setMode(newMode);
    setQuestion("");

    if (newMode === "all") {
      onSelectPersona(null);
    }
  };

  // =========================================================
  // INDIVIDUAL INTERVIEW
  // =========================================================

  const askSelectedPersona = async () => {
    if (!selectedPersona) {
      alert("Please select a persona first.");
      return;
    }

    const currentQuestion = question.trim();

    if (!currentQuestion || loading) {
      return;
    }

    const personaId = selectedPersona.id;

    // =====================================================
    // ADD USER MESSAGE
    // =====================================================

    setInterviewMessages((previous) => ({
      ...previous,

      [personaId]: [
        ...(previous[personaId] || []),
        {
          type: "user",
          text: currentQuestion
        }
      ]
    }));

    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/interview",
        {
          personaId: personaId,
          question: currentQuestion
        }
      );

      // ===================================================
      // ADD PERSONA RESPONSE
      // ===================================================

      setInterviewMessages((previous) => ({
        ...previous,

        [personaId]: [
          ...(previous[personaId] || []),
          {
            type: "persona",
            persona: selectedPersona,
            text:
              response.data.answer ||
              "The persona did not provide a response."
          }
        ]
      }));

    } catch (error) {
      console.error(
        "Individual interview error:",
        error
      );

      // ===================================================
      // ADD ERROR MESSAGE
      // ===================================================

      setInterviewMessages((previous) => ({
        ...previous,

        [personaId]: [
          ...(previous[personaId] || []),
          {
            type: "error",
            text:
              error.response?.data?.error ||
              "Unable to get a response from this persona."
          }
        ]
      }));

    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ALL PERSONAS INTERVIEW
  // =========================================================

  const askAllPersonas = async () => {
    const currentQuestion = question.trim();

    if (!currentQuestion || loading) {
      return;
    }

    if (!personas || personas.length === 0) {
      alert("No personas are available.");
      return;
    }

    // =====================================================
    // ADD USER MESSAGE
    // =====================================================

    setInterviewMessages((previous) => ({
      ...previous,

      all: [
        ...(previous.all || []),
        {
          type: "user",
          text: currentQuestion
        }
      ]
    }));

    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/interview-all",
        {
          question: currentQuestion,
          personas: personas
        }
      );

      const newAnswers =
        response.data.answers || [];

      // ===================================================
      // ADD ALL PERSONA RESPONSES
      // ===================================================

      setInterviewMessages((previous) => ({
        ...previous,

        all: [
          ...(previous.all || []),

          ...newAnswers.map((item) => ({
            type: "persona",
            persona: item.persona,
            text:
              item.answer ||
              "The persona did not provide a response."
          }))
        ]
      }));

    } catch (error) {
      console.error(
        "All-persona interview error:",
        error
      );

      setInterviewMessages((previous) => ({
        ...previous,

        all: [
          ...(previous.all || []),
          {
            type: "error",
            text:
              error.response?.data?.error ||
              "Unable to get responses from all personas."
          }
        ]
      }));

    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // SEND MESSAGE
  // =========================================================

  const sendMessage = () => {
    if (mode === "all") {
      askAllPersonas();
    } else {
      askSelectedPersona();
    }
  };

  // =========================================================
  // ENTER KEY
  // =========================================================

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // =========================================================
  // CLEAR CURRENT CHAT
  // =========================================================

  const clearChat = () => {
    if (
      mode === "individual" &&
      selectedPersona
    ) {
      setInterviewMessages((previous) => ({
        ...previous,
        [selectedPersona.id]: []
      }));
    }

    if (mode === "all") {
      setInterviewMessages((previous) => ({
        ...previous,
        all: []
      }));
    }

    setQuestion("");
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="interview-container">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="interview-header">

        <div>

          <h2>
            🎤 AI Persona Interview
          </h2>

          <p>
            Have a natural conversation with your selected
            persona or compare responses from all personas.
          </p>

        </div>

        {messages.length > 0 && (
          <button
            type="button"
            className="clear-chat-btn"
            onClick={clearChat}
          >
            🗑 Clear Chat
          </button>
        )}

      </div>

      {/* =================================================
          MODE SWITCH
      ================================================= */}

      <div className="interview-mode-switch">

        <button
          type="button"
          className={
            mode === "individual"
              ? "mode-btn active"
              : "mode-btn"
          }
          onClick={() =>
            switchMode("individual")
          }
        >
          👤 Individual Interview
        </button>

        <button
          type="button"
          className={
            mode === "all"
              ? "mode-btn active"
              : "mode-btn"
          }
          onClick={() =>
            switchMode("all")
          }
        >
          👥 Ask All Personas
        </button>

      </div>

      {/* =================================================
          PERSONA SELECTOR
      ================================================= */}

      <div className="persona-selector">

        <div className="selector-heading">

          <div>

            <h3>
              👥 Choose a Persona
            </h3>

            <p>
              Select who you want to interview.
            </p>

          </div>

          <span className="persona-count">
            {personas.length} personas
          </span>

        </div>

        <div className="persona-selector-grid">

          {personas.map((persona, index) => (

            <button
              type="button"
              key={persona.id || index}
              className={
                selectedPersona?.id === persona.id &&
                mode === "individual"
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

          ))}

        </div>

      </div>

      {/* =================================================
          ACTIVE PERSONA
      ================================================= */}

      {mode === "individual" &&
        selectedPersona && (

        <div className="selected-persona">

          <div className="selected-persona-avatar">
            👤
          </div>

          <div className="selected-persona-content">

            <div className="selected-persona-title">

              <div>

                <h3>
                  {selectedPersona.name}
                </h3>

                <p>
                  {selectedPersona.age} years old
                  {" • "}
                  {selectedPersona.occupation}
                </p>

              </div>

              <span className="active-badge">
                ● Active
              </span>

            </div>

            <p className="persona-personality">
              🧠 {selectedPersona.personality}
            </p>

          </div>

        </div>

      )}

      {/* =================================================
          ALL PERSONAS INFO
      ================================================= */}

      {mode === "all" && (

        <div className="selected-persona">

          <div className="selected-persona-avatar">
            👥
          </div>

          <div className="selected-persona-content">

            <div className="selected-persona-title">

              <div>

                <h3>
                  All Personas
                </h3>

                <p>
                  Compare how different personas respond
                  to the same question.
                </p>

              </div>

              <span className="active-badge">
                ● {personas.length} Voices
              </span>

            </div>

          </div>

        </div>

      )}

      {/* =================================================
          CHAT WINDOW
      ================================================= */}

      <div className="chat-wrapper">

        <div className="chat-header">

          <div>

            <strong>
              {mode === "all"
                ? "👥 Persona Panel"
                : selectedPersona
                  ? `💬 Chat with ${selectedPersona.name}`
                  : "💬 Persona Chat"}
            </strong>

            <span>
              {mode === "all"
                ? "Multiple persona perspectives"
                : selectedPersona
                  ? "Conversation-aware interview"
                  : "Select a persona to begin"}
            </span>

          </div>

          <span className="memory-indicator">
            🧠 Memory On
          </span>

        </div>

        <div className="chat-messages">

          {/* =================================================
              EMPTY STATE
          ================================================= */}

          {messages.length === 0 && !loading && (

            <div className="chat-empty">

              <div className="chat-empty-icon">
                💬
              </div>

              <h3>
                Start the conversation
              </h3>

              <p>
                Ask a question and the persona will respond
                based on their personality, preferences,
                and previous conversation.
              </p>

              <div className="suggested-questions">

                <button
                  type="button"
                  disabled={
                    mode === "individual" &&
                    !selectedPersona
                  }
                  onClick={() =>
                    setQuestion(
                      "What matters most to you when choosing a product like this?"
                    )
                  }
                >
                  What matters most to you?
                </button>

                <button
                  type="button"
                  disabled={
                    mode === "individual" &&
                    !selectedPersona
                  }
                  onClick={() =>
                    setQuestion(
                      "What would make you choose this product?"
                    )
                  }
                >
                  What would make you choose it?
                </button>

                <button
                  type="button"
                  disabled={
                    mode === "individual" &&
                    !selectedPersona
                  }
                  onClick={() =>
                    setQuestion(
                      "What concerns would stop you from using it?"
                    )
                  }
                >
                  What concerns you?
                </button>

              </div>

            </div>

          )}

          {/* =================================================
              MESSAGES
          ================================================= */}

          {messages.map((message, index) => (

            <div
              key={index}
              className={
                message.type === "user"
                  ? "chat-message user-message"
                  : message.type === "error"
                    ? "chat-message error-message"
                    : "chat-message persona-message"
              }
            >

              {message.type === "user" ? (

                <>
                  <div className="message-content">

                    <span className="message-label">
                      You
                    </span>

                    <p>
                      {message.text}
                    </p>

                  </div>

                  <div className="message-avatar">
                    👤
                  </div>
                </>

              ) : (

                <>
                  <div className="message-avatar persona-message-avatar">
                    👤
                  </div>

                  <div className="message-content">

                    <div className="persona-message-name">

                      <span>
                        {message.type === "error"
                          ? "System"
                          : message.persona?.name ||
                            "Persona"}
                      </span>

                      {message.type !== "error" && (
                        <small>
                          {message.persona?.occupation}
                        </small>
                      )}

                    </div>

                    <p>
                      {message.text}
                    </p>

                  </div>

                </>

              )}

            </div>

          ))}

          {/* =================================================
              TYPING INDICATOR
          ================================================= */}

          {loading && (

            <div className="chat-message persona-message">

              <div className="message-avatar persona-message-avatar">
                👤
              </div>

              <div className="message-content">

                <div className="persona-message-name">

                  <span>
                    {mode === "all"
                      ? "Personas"
                      : selectedPersona?.name ||
                        "Persona"}
                  </span>

                </div>

                <div className="typing-indicator">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>

            </div>

          )}

          <div ref={chatEndRef} />

        </div>

        {/* =================================================
            INPUT
        ================================================= */}

        <div className="chat-input-area">

          <input
            type="text"
            value={question}
            placeholder={
              mode === "all"
                ? "Ask the same question to all personas..."
                : selectedPersona
                  ? `Message ${selectedPersona.name}...`
                  : "Select a persona first..."
            }
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            onKeyDown={handleKeyDown}
            disabled={
              loading ||
              (mode === "individual" &&
                !selectedPersona)
            }
          />

          <button
            type="button"
            onClick={sendMessage}
            disabled={
              loading ||
              !question.trim() ||
              (mode === "individual" &&
                !selectedPersona)
            }
          >
            {loading ? "..." : "Send ↑"}
          </button>

        </div>

        <div className="chat-input-hint">
          Press Enter to send • Shift + Enter for a new line
        </div>

      </div>

    </div>
  );
}

export default Interview;