import { useState } from "react";
import axios from "axios";

import PersonaCard from "./components/PersonaCard";
import Interview from "./components/Interview";
import Results from "./components/Results";
import Insights from "./components/Insights";
import AskResearch from "./components/AskResearch";

import "./App.css";

function App() {
  const [product, setProduct] = useState("");
  const [description, setDescription] = useState("");
  const [gender, setGender] = useState("Both");
  const [age, setAge] = useState("");
  const [objective, setObjective] = useState("");

  // 100-persona support
  const [count, setCount] = useState(20);

  const [result, setResult] = useState(null);
  const [activePage, setActivePage] = useState("generate");
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Interview conversations stay in App state so page navigation
  // does not clear the conversation.
  const [interviewMessages, setInterviewMessages] = useState({});

  // =========================================================
  // GENERATE PERSONAS
  // =========================================================

  const generate = async () => {
    if (!product.trim()) {
      alert("Please enter a product name.");
      return;
    }

    if (!age.trim()) {
      alert("Please enter the target audience age.");
      return;
    }

    if (!description.trim()) {
      alert("Please describe the product.");
      return;
    }

    if (!objective.trim()) {
      alert("Please enter the research objective.");
      return;
    }

    if (isGenerating) return;

    const requestedCount = Math.min(
      100,
      Math.max(1, Number(count) || 1)
    );

    setIsGenerating(true);

    try {
      const res = await axios.post(
        "http://127.0.0.1:5000/generate",
        {
          product: product.trim(),
          description: description.trim(),
          gender,
          age: age.trim(),
          objective: objective.trim(),
          count: requestedCount,
        },
        {
          timeout: 180000,
        }
      );

      console.log("Generated research response:", res.data);

      if (
        !res.data ||
        !Array.isArray(res.data.personas) ||
        res.data.personas.length === 0
      ) {
        throw new Error("Backend returned no personas.");
      }

      // The backend returns the requested number, up to 100.
      setResult(res.data);

      // New research session = fresh interview conversations.
      setInterviewMessages({});

      setSelectedPersona(null);

      // Open the persona page after generation.
      setActivePage("personas");
    } catch (err) {
      console.error("Full Error:", err);

      if (err.response) {
        console.error("Backend Response:", err.response.data);

        alert(
          err.response.data?.error ||
            JSON.stringify(err.response.data)
        );
      } else if (err.code === "ECONNABORTED") {
        alert(
          "Persona generation took too long. Please check Flask and try again."
        );
      } else {
        alert(
          err.message ||
            "Unable to connect to the backend. Make sure Flask is running."
        );
      }
    } finally {
      setIsGenerating(false);
    }
  };

  // =========================================================
  // INTERVIEW
  // =========================================================

  const openInterview = (persona) => {
    setSelectedPersona(persona);
    setActivePage("interview");
  };

  const openInterviewPage = () => {
    if (result) {
      setActivePage("interview");
    }
  };

  // =========================================================
  // SIDEBAR NAVIGATION
  // =========================================================

  const goToPage = (page) => {
    if (page === "personas" && !result) return;
    if (page === "interview" && !result) return;
    if (page === "results" && !result) return;
    if (page === "insights" && !result) return;
    if (page === "ask-research" && !result) return;

    setActivePage(page);
  };

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="app-layout">

      {/* SIDEBAR — intentionally unchanged */}
      <aside
        className={`sidebar ${
          sidebarCollapsed ? "collapsed" : ""
        }`}
      >
        <div className="sidebar-logo">
          <div className="logo-row">
            <div className="logo-brain">🧠</div>

            {!sidebarCollapsed && (
              <div>
                <h2>Persona AI</h2>
                <p>Synthetic User Research</p>
              </div>
            )}
          </div>
        </div>

        <button
          type="button"
          className="sidebar-toggle"
          onClick={() =>
            setSidebarCollapsed((prev) => !prev)
          }
          title={
            sidebarCollapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
          aria-label={
            sidebarCollapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
        >
          {sidebarCollapsed ? "☰" : "←"}
        </button>

        <nav className="sidebar-nav">

          <button
            type="button"
            className={
              activePage === "generate"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => goToPage("generate")}
          >
            <span className="nav-icon">✨</span>
            {!sidebarCollapsed && (
              <span className="nav-label">Generate</span>
            )}
          </button>

          <button
            type="button"
            className={
              activePage === "personas"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => goToPage("personas")}
            disabled={!result}
          >
            <span className="nav-icon">👥</span>
            {!sidebarCollapsed && (
              <span className="nav-label">Personas</span>
            )}
          </button>

          <button
            type="button"
            className={
              activePage === "interview"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={openInterviewPage}
            disabled={!result}
          >
            <span className="nav-icon">🎤</span>
            {!sidebarCollapsed && (
              <span className="nav-label">Interview</span>
            )}
          </button>

          <button
            type="button"
            className={
              activePage === "results"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => goToPage("results")}
            disabled={!result}
          >
            <span className="nav-icon">📊</span>
            {!sidebarCollapsed && (
              <span className="nav-label">Results</span>
            )}
          </button>

          <button
            type="button"
            className={
              activePage === "insights"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => goToPage("insights")}
            disabled={!result}
          >
            <span className="nav-icon">💡</span>
            {!sidebarCollapsed && (
              <span className="nav-label">Insights</span>
            )}
          </button>

          <button
            type="button"
            className={
              activePage === "ask-research"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => goToPage("ask-research")}
            disabled={!result}
          >
            <span className="nav-icon">🔎</span>
            {!sidebarCollapsed && (
              <span className="nav-label">Ask Research</span>
            )}
          </button>

        </nav>

        {!sidebarCollapsed && (
          <div className="sidebar-footer">
            <span>AI-powered UX Research</span>
          </div>
        )}
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">

        {/* GENERATE PAGE */}
        {activePage === "generate" && (
          <div className="page">

            <header className="page-header">
              <div className="title-icon">🧠</div>

              <div className="title-content">
                <h1>
                  Generation of AI Powered Synthetic
                  Users for Product Research
                </h1>

                <p className="subtitle">
                  Generate realistic AI-powered synthetic users
                  to understand customer preferences, behavior,
                  and product decisions.
                </p>
              </div>
            </header>

            <section className="project-info">
              <div className="project-info-icon">💡</div>

              <div>
                <h3>About the Project</h3>

                <p>
                  This platform uses Generative AI to create
                  realistic synthetic users based on your target
                  audience, product information, and research
                  objective. These AI personas can be analyzed,
                  interviewed, and used to simulate product
                  research before conducting real-world studies.
                </p>
              </div>
            </section>

            <section className="generator-card">

              <div className="form-section-title">
                <div className="section-icon">📋</div>

                <div>
                  <h2>Research Setup</h2>
                  <p>
                    Define your product, target audience and
                    research goals
                  </p>
                </div>
              </div>

              <div className="form-grid">

                <div className="form-field">
                  <label className="form-label">
                    📦 Product Name
                  </label>

                  <input
                    type="text"
                    placeholder="e.g. Boat Airdopes 311 Pro"
                    value={product}
                    onChange={(e) =>
                      setProduct(e.target.value)
                    }
                  />

                  <span className="form-help">
                    Enter the product you want to research
                  </span>
                </div>

                <div className="form-field">
                  <label className="form-label">
                    🎯 Target Audience Age
                  </label>

                  <input
                    type="text"
                    placeholder="e.g. 18-30"
                    value={age}
                    onChange={(e) =>
                      setAge(e.target.value)
                    }
                  />

                  <span className="form-help">
                    Specify the age range of your target users
                  </span>
                </div>

                <div className="form-field full">
                  <label className="form-label">
                    📝 Product Description
                  </label>

                  <textarea
                    placeholder="Describe the product, features, price range, benefits, target market, etc."
                    value={description}
                    onChange={(e) =>
                      setDescription(e.target.value)
                    }
                  />

                  <span className="form-help">
                    More product context helps the AI create
                    more relevant synthetic users
                  </span>
                </div>

                <div className="form-field">
                  <label className="form-label">
                    👤 Target Gender
                  </label>

                  <div className="gender-options">

                    <label className="radio-option">
                      <input
                        type="radio"
                        value="Male"
                        checked={gender === "Male"}
                        onChange={(e) =>
                          setGender(e.target.value)
                        }
                      />
                      <span>Male</span>
                    </label>

                    <label className="radio-option">
                      <input
                        type="radio"
                        value="Female"
                        checked={gender === "Female"}
                        onChange={(e) =>
                          setGender(e.target.value)
                        }
                      />
                      <span>Female</span>
                    </label>

                    <label className="radio-option">
                      <input
                        type="radio"
                        value="Both"
                        checked={gender === "Both"}
                        onChange={(e) =>
                          setGender(e.target.value)
                        }
                      />
                      <span>Both</span>
                    </label>

                  </div>
                </div>

                <div className="form-field">
                  <label className="form-label">
                    👥 Number of Personas
                  </label>

                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={count}
                    onChange={(e) => {
                      const raw = e.target.value;

                      if (raw === "") {
                        setCount("");
                        return;
                      }

                      let value = Number(raw);

                      if (value > 100) value = 100;
                      if (value < 1) value = 1;

                      setCount(value);
                    }}
                  />

                  <span className="form-help">
                    Generate between 1 and 100 synthetic users
                  </span>
                </div>

                <div className="form-field full">
                  <label className="form-label">
                    📊 Research Objective
                  </label>

                  <input
                    type="text"
                    placeholder="e.g. Discover what influences users to purchase wireless earbuds"
                    value={objective}
                    onChange={(e) =>
                      setObjective(e.target.value)
                    }
                  />

                  <span className="form-help">
                    Define what you want to discover from
                    your synthetic users
                  </span>
                </div>

              </div>

              <button
                type="button"
                className="generate-btn"
                onClick={generate}
                disabled={isGenerating}
              >
                {isGenerating
                  ? `⏳ Generating ${Number(count) || 1} Synthetic Users...`
                  : "✨ Generate AI Personas"}
              </button>

            </section>
          </div>
        )}

        {/* PERSONAS PAGE */}
        {activePage === "personas" && result && (
          <div className="page">

            <div className="page-header simple-header">
              <div className="title-icon">👥</div>

              <div>
                <h1>Generated Personas</h1>

                <p className="subtitle">
                  {result.personas.length} AI-generated
                  synthetic users for your product research
                </p>
              </div>
            </div>

            <div className="persona-count-banner">
              <strong>{result.personas.length}</strong>
              <span>
                synthetic personas generated for this research
                session
              </span>
            </div>

            <div className="grid">
              {result.personas.map((persona, index) => (
                <div
                  key={persona.id || index}
                  className="persona-wrapper"
                >
                  <PersonaCard persona={persona} />

                  <button
                    type="button"
                    className="interview-btn"
                    onClick={() =>
                      openInterview(persona)
                    }
                  >
                    🎤 Interview Persona
                  </button>
                </div>
              ))}
            </div>

          </div>
        )}

        {/* INTERVIEW PAGE */}
        {activePage === "interview" && result && (
          <div className="page">

            <div className="page-header simple-header">
              <div className="title-icon">🎤</div>

              <div>
                <h1>Persona Interview</h1>

                <p className="subtitle">
                  Interact with your AI-generated synthetic
                  users
                </p>
              </div>
            </div>

            <Interview
              personas={result.personas}
              selectedPersona={selectedPersona}
              onSelectPersona={setSelectedPersona}
              interviewMessages={interviewMessages}
              setInterviewMessages={setInterviewMessages}
            />

          </div>
        )}

        {/* RESULTS PAGE */}
        {activePage === "results" && result && (
          <div className="page">

            <Results
              personas={result.personas}
              preferred={result.preferred}
              notPreferred={result.notPreferred}
              product={product}
              description={description}
              gender={gender}
              age={age}
              objective={objective}
            />

          </div>
        )}

        {/* INSIGHTS PAGE */}
        {activePage === "insights" && result && (
          <div className="page">

            <Insights
              personas={result.personas}
            />

          </div>
        )}

        {/* ASK YOUR RESEARCH PAGE */}
        {activePage === "ask-research" && result && (
          <div className="page">

            <AskResearch
              personas={result.personas}
            />

          </div>
        )}

      </main>
    </div>
  );
}

export default App;
