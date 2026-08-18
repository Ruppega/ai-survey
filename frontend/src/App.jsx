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

  // Sidebar page
  const [activePage, setActivePage] = useState("generate");

  // Selected persona for interview
  const [selectedPersona, setSelectedPersona] = useState(null);

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

      // Automatically show personas after generation
      setActivePage("personas");

    } catch (err) {
      console.error("Full Error:", err);

      if (err.response) {
        console.error(
          "Backend Response:",
          err.response.data
        );

        alert(
          err.response.data.error ||
          JSON.stringify(err.response.data)
        );
      } else {
        alert(err.message);
      }
    }
  };

  const openInterview = (persona) => {
    setSelectedPersona(persona);
    setActivePage("interview");
  };

  return (
    <div className="app-layout">

      {/* ================================================= */}
      {/* SIDEBAR */}
      {/* ================================================= */}

      <aside className="sidebar">

        <div className="sidebar-logo">
          <h2>🧠 Persona AI</h2>
          <p>Synthetic User Research</p>
        </div>

        <nav className="sidebar-nav">

          <button
            className={
              activePage === "generate"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActivePage("generate")}
          >
            <span>✨</span>
            Generate
          </button>

          <button
            className={
              activePage === "personas"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActivePage("personas")}
            disabled={!result}
          >
            <span>👥</span>
            Personas
          </button>

          <button
            className={
              activePage === "interview"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActivePage("interview")}
            disabled={!result}
          >
            <span>🎤</span>
            Interview
          </button>

          <button
            className={
              activePage === "results"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActivePage("results")}
            disabled={!result}
          >
            <span>📊</span>
            Results
          </button>

        </nav>

        <div className="sidebar-footer">
          <p>AI-powered UX Research</p>
        </div>

      </aside>


      {/* ================================================= */}
      {/* MAIN CONTENT */}
      {/* ================================================= */}

      <main className="main-content">

        {/* ================================================= */}
        {/* GENERATE PAGE */}
        {/* ================================================= */}

        {activePage === "generate" && (

          <div className="page">

            <h1>🧠 Synthetic Persona Generator</h1>

            <p className="subtitle">
              Generate AI-powered synthetic personas
              for market research
            </p>


            {/* Product Name */}

            <label className="form-label">
              📦 Product Name
            </label>

            <input
              type="text"
              placeholder="Enter product name"
              value={product}
              onChange={(e) =>
                setProduct(e.target.value)
              }
            />


            {/* Description */}

            <label className="form-label">
              📝 Product Description
            </label>

            <textarea
              placeholder="Describe your product"
              value={description}
              onChange={(e) =>
                setDescription(e.target.value)
              }
            />


            {/* Gender */}

            <div className="gender-group">

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


            {/* Age */}

            <label className="form-label">
              🎯 Target Audience Age
            </label>

            <input
              type="text"
              placeholder="Example: 18-30"
              value={age}
              onChange={(e) =>
                setAge(e.target.value)
              }
            />


            {/* Number of Personas */}

            <label className="form-label">
              👥 Number of Personas
            </label>

            <input
              type="number"
              placeholder="1 - 20"
              value={count}
              min="1"
              max="20"
              onChange={(e) => {

                let value = Number(e.target.value);

                if (value > 20) value = 20;

                if (
                  value < 1 &&
                  e.target.value !== ""
                ) {
                  value = 1;
                }

                setCount(value);

              }}
            />


            {/* Research Objective */}

            <label className="form-label">
              📊 Research Objective
            </label>

            <input
              type="text"
              placeholder="What do you want to discover?"
              value={objective}
              onChange={(e) =>
                setObjective(e.target.value)
              }
            />


            {/* Generate */}

            <button
              className="generate-btn"
              onClick={generate}
            >
              ✨ Generate Personas
            </button>

          </div>

        )}


        {/* ================================================= */}
        {/* PERSONAS PAGE */}
        {/* ================================================= */}

        {activePage === "personas" && result && (

          <div className="page">

            <h1>👥 Generated Personas</h1>

            <p className="subtitle">
              AI-generated synthetic users for your research
            </p>


            <div className="grid">

              {result.personas.map(
                (persona, index) => (

                  <div
                    key={persona.id || index}
                    className="persona-wrapper"
                  >

                    <PersonaCard
                      persona={persona}
                    />

                    <button
                      className="interview-btn"
                      onClick={() =>
                        openInterview(persona)
                      }
                    >
                      🎤 Interview Persona
                    </button>

                  </div>

                )
              )}

            </div>

          </div>

        )}


        {/* ================================================= */}
        {/* INTERVIEW PAGE */}
        {/* ================================================= */}

        {activePage === "interview" && (

          <div className="page">

            {selectedPersona ? (

              <Interview
                persona={selectedPersona}
              />

            ) : (

              <div className="empty-state">

                <h2>🎤 Interview Mode</h2>

                <p>
                  Select a persona from the Personas page
                  to start an interview.
                </p>

                <button
                  onClick={() =>
                    setActivePage("personas")
                  }
                >
                  👥 View Personas
                </button>

              </div>

            )}

          </div>

        )}


        {/* ================================================= */}
        {/* RESULTS PAGE */}
        {/* ================================================= */}

        {activePage === "results" && result && (

          <div className="page">

            <h1>📊 Research Results</h1>

            <p className="subtitle">
              Summary of persona preferences
            </p>


            <div className="stats">

              <div className="stat-box">

                <h3>👍 Preferred</h3>

                <p>
                  {result.preferred}
                </p>

              </div>


              <div className="stat-box">

                <h3>👎 Not Preferred</h3>

                <p>
                  {result.notPreferred}
                </p>

              </div>


              <div className="stat-box">

                <h3>📊 Preference Rate</h3>

                <p>

                  {Math.round(
                    (result.preferred * 100) /
                    result.personas.length
                  )}

                  %

                </p>

              </div>


              <div className="stat-box">

                <h3>👥 Total Personas</h3>

                <p>
                  {result.personas.length}
                </p>

              </div>

            </div>

          </div>

        )}

      </main>

    </div>
  );
}

export default App;