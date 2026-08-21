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

  // Current sidebar page
  const [activePage, setActivePage] = useState("generate");

  // Selected persona for individual interview
  const [selectedPersona, setSelectedPersona] = useState(null);

  // Sidebar collapsed / expanded
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Generate personas
  const generate = async () => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:5000/generate",
        {
          product,
          description,
          gender,
          age,
          objective,
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
        alert(err.message);
      }
    }
  };

  // Open individual persona interview
  const openInterview = (persona) => {
    setSelectedPersona(persona);
    setActivePage("interview");
  };

  // Open interview page
  const openInterviewPage = () => {
    if (result) {
      setActivePage("interview");
    }
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
          <h2>
            🧠
            <span className="sidebar-logo-text">
              Persona AI
            </span>
          </h2>

          <p>Synthetic User Research</p>
        </div>

        {/* SIDEBAR TOGGLE */}
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
          <span aria-hidden="true">
            {sidebarCollapsed ? "☰" : "←"}
          </span>
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
            onClick={() => setActivePage("generate")}
          >
            <span className="nav-icon">✨</span>
            <span className="nav-label">Generate</span>
          </button>

          <button
            type="button"
            className={
              activePage === "personas"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActivePage("personas")}
            disabled={!result}
          >
            <span className="nav-icon">👥</span>
            <span className="nav-label">Personas</span>
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
            <span className="nav-label">Interview</span>
          </button>

          <button
            type="button"
            className={
              activePage === "results"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActivePage("results")}
            disabled={!result}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Results</span>
          </button>

        </nav>

        {/* SIDEBAR FOOTER */}
        <div className="sidebar-footer">
          <p>AI-powered UX Research</p>
        </div>
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

            <div className="page-header">
              <h1>🧠 Synthetic Persona Generator</h1>

              <p className="subtitle">
                Generate AI-powered synthetic users for smarter
                market research
              </p>
            </div>

            <div className="generator-card">

              {/* SECTION HEADER */}
              <div className="form-section-title">
                <div className="section-icon">📋</div>

                <div>
                  <h2>Research Setup</h2>
                  <p>
                    Define your product and target audience
                  </p>
                </div>
              </div>

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
                    placeholder="Describe the product, its features, price range, benefits, etc."
                    value={description}
                    onChange={(e) =>
                      setDescription(e.target.value)
                    }
                  />

                  <span className="form-help">
                    The more context you provide, the more
                    relevant the personas will be
                  </span>
                </div>

                {/* GENDER */}
                <div className="form-field">
                  <label className="form-label">
                    👤 Target Gender
                  </label>

                  <div className="gender-options">

                    <label>
                      <input
                        type="radio"
                        value="Male"
                        checked={gender === "Male"}
                        onChange={(e) =>
                          setGender(e.target.value)
                        }
                      />
                      Male
                    </label>

                    <label>
                      <input
                        type="radio"
                        value="Female"
                        checked={gender === "Female"}
                        onChange={(e) =>
                          setGender(e.target.value)
                        }
                      />
                      Female
                    </label>

                    <label>
                      <input
                        type="radio"
                        value="Both"
                        checked={gender === "Both"}
                        onChange={(e) =>
                          setGender(e.target.value)
                        }
                      />
                      Both
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
                      let value = Number(e.target.value);

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

                {/* RESEARCH OBJECTIVE */}
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
                    What would you like the AI personas to help
                    you discover?
                  </span>
                </div>

              </div>

              {/* GENERATE BUTTON */}
              <button
                type="button"
                className="generate-btn"
                onClick={generate}
              >
                ✨ Generate AI Personas
              </button>

            </div>
          </div>
        )}

        {/* =====================================================
            PERSONAS PAGE
        ====================================================== */}

        {activePage === "personas" && result && (
          <div className="page">

            <div className="page-header">
              <h1>👥 Generated Personas</h1>

              <p className="subtitle">
                AI-generated synthetic users for your research
              </p>
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

            <div className="page-header">
              <h1>🎤 Persona Interview</h1>

              <p className="subtitle">
                Interact with your AI-generated synthetic users
              </p>
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

            <div className="page-header">
              <h1>📊 Research Results</h1>

              <p className="subtitle">
                Summary of persona preferences
              </p>
            </div>

            <div className="stats">

              {/* PREFERRED */}
              <div className="stat-box">
                <h3>👍 Preferred</h3>
                <p>{result.preferred}</p>
              </div>

              {/* NOT PREFERRED */}
              <div className="stat-box">
                <h3>👎 Not Preferred</h3>
                <p>{result.notPreferred}</p>
              </div>

              {/* PREFERENCE RATE */}
              <div className="stat-box">
                <h3>📊 Preference Rate</h3>

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

              {/* TOTAL PERSONAS */}
              <div className="stat-box">
                <h3>👥 Total Personas</h3>
                <p>{result.personas.length}</p>
              </div>

            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;