import { useState } from "react";
import axios from "axios";
import PersonaCard from "./components/PersonaCard";
import Interview from "./components/Interview";
import "./App.css";

function App() {
  const [product, setProduct] = useState("");
  const [description, setDescription] = useState("");
  const [gender, setGender] = useState("Both");
  const [age, setAge] = useState("");
  const [objective, setObjective] = useState("");
  const [count, setCount] = useState(20);

  const [result, setResult] = useState(null);
  const [activePage, setActivePage] = useState("generate");
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

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
          count,
        }
      );

      console.log("Response:", res.data);

      setResult(res.data);
      setSelectedPersona(null);
      setActivePage("personas");
    } catch (err) {
      console.error("Full Error:", err);

      if (err.response) {
        console.error("Backend Response:", err.response.data);

        alert(
          err.response.data.error ||
            JSON.stringify(err.response.data)
        );
      } else {
        alert(
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
  // SIDEBAR
  // =========================================================

  const goToPage = (page) => {
    if (page === "personas" && !result) return;
    if (page === "interview" && !result) return;
    if (page === "results" && !result) return;

    setActivePage(page);
  };

  return (
    <div className="app-layout">

      {/* =====================================================
          SIDEBAR
      ====================================================== */}

      <aside
        className={`sidebar ${
          sidebarCollapsed ? "collapsed" : ""
        }`}
      >
        {/* LOGO */}
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

        {/* TOGGLE */}
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

        {/* NAVIGATION */}
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
              <span className="nav-label">
                Generate
              </span>
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
              <span className="nav-label">
                Personas
              </span>
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
              <span className="nav-label">
                Interview
              </span>
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
              <span className="nav-label">
                Results
              </span>
            )}
          </button>

        </nav>

        {/* FOOTER */}
        {!sidebarCollapsed && (
          <div className="sidebar-footer">
            <span>AI-powered UX Research</span>
          </div>
        )}
      </aside>

      {/* =====================================================
          MAIN CONTENT
      ====================================================== */}

      <main className="main-content">

        {/* =====================================================
            GENERATE PAGE
        ====================================================== */}

        {activePage === "generate" && (
          <div className="page">

            {/* PAGE HEADER */}

            <header className="page-header">

              <div className="title-icon">
                🧠
              </div>

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

            {/* ABOUT PROJECT */}

            <section className="project-info">

              <div className="project-info-icon">
                💡
              </div>

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

            {/* GENERATOR CARD */}

            <section className="generator-card">

              {/* SECTION HEADER */}

              <div className="form-section-title">

                <div className="section-icon">
                  📋
                </div>

                <div>
                  <h2>Research Setup</h2>

                  <p>
                    Define your product, target audience and
                    research goals
                  </p>
                </div>

              </div>

              {/* FORM */}

              <div className="form-grid">

                {/* PRODUCT NAME */}

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

                {/* AGE */}

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

                {/* DESCRIPTION */}

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

                {/* GENDER */}

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

                {/* PERSONA COUNT */}

                <div className="form-field">

                  <label className="form-label">
                    👥 Number of Personas
                  </label>

                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={count}
                    onChange={(e) => {
                      let value = Number(
                        e.target.value
                      );

                      if (value > 20) {
                        value = 20;
                      }

                      if (
                        value < 1 &&
                        e.target.value !== ""
                      ) {
                        value = 1;
                      }

                      setCount(value);
                    }}
                  />

                  <span className="form-help">
                    Generate between 1 and 20 synthetic users
                  </span>

                </div>

                {/* OBJECTIVE */}

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

              {/* GENERATE BUTTON */}

              <button
                type="button"
                className="generate-btn"
                onClick={generate}
                disabled={isGenerating}
              >
                {isGenerating
                  ? "⏳ Generating Synthetic Users..."
                  : "✨ Generate AI Personas"}
              </button>

            </section>

          </div>
        )}

        {/* =====================================================
            PERSONAS PAGE
        ====================================================== */}

        {activePage === "personas" && result && (
          <div className="page">

            <div className="page-header simple-header">

              <div className="title-icon">
                👥
              </div>

              <div>
                <h1>Generated Personas</h1>

                <p className="subtitle">
                  AI-generated synthetic users for your
                  product research
                </p>
              </div>

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

        {/* =====================================================
            INTERVIEW PAGE
        ====================================================== */}

        {activePage === "interview" && result && (
          <div className="page">

            <div className="page-header simple-header">

              <div className="title-icon">
                🎤
              </div>

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
            />

          </div>
        )}

        {/* =====================================================
            RESULTS PAGE
        ====================================================== */}

        {activePage === "results" && result && (
          <div className="page">

            <div className="page-header simple-header">

              <div className="title-icon">
                📊
              </div>

              <div>
                <h1>Research Results</h1>

                <p className="subtitle">
                  Summary of synthetic persona preferences
                </p>
              </div>

            </div>

            <div className="stats">

              <div className="stat-box">
                <span className="stat-icon">
                  👍
                </span>

                <div>
                  <h3>Preferred</h3>
                  <p>{result.preferred}</p>
                </div>
              </div>

              <div className="stat-box">
                <span className="stat-icon">
                  👎
                </span>

                <div>
                  <h3>Not Preferred</h3>
                  <p>{result.notPreferred}</p>
                </div>
              </div>

              <div className="stat-box">
                <span className="stat-icon">
                  📊
                </span>

                <div>
                  <h3>Preference Rate</h3>

                  <p>
                    {result.personas.length > 0
                      ? Math.round(
                          (result.preferred * 100) /
                            result.personas.length
                        )
                      : 0}
                    %
                  </p>
                </div>
              </div>

              <div className="stat-box">
                <span className="stat-icon">
                  👥
                </span>

                <div>
                  <h3>Total Personas</h3>
                  <p>{result.personas.length}</p>
                </div>
              </div>

            </div>

          </div>
        )}

      </main>
    </div>
  );
}

export default App;