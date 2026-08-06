import { useState } from "react";
import axios from "axios";
import PersonaCard from "./components/PersonaCard";
import "./App.css";

function App() {
  const [product, setProduct] = useState("");
  const [description, setDescription] = useState("");
  const [gender, setGender] = useState("Both");
  const [age, setAge] = useState("");
  const [objective, setObjective] = useState("");
  const [count, setCount] = useState(20);

  const [result, setResult] = useState(null);

  const generate = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/generate", {
        product,
        description,
        gender,
        age,
        objective,
        count,
      });

      console.log("Response:", res.data);
      setResult(res.data);
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

  return (
    <div className="container">
      <h1>🧠 Synthetic Persona Generator</h1>

      <p className="subtitle">
        Generate AI-powered synthetic personas for market research
      </p>

      {/* Product Name */}
      <label className="form-label">📦 Product Name</label>
      <input
        type="text"
        placeholder="Enter product name"
        value={product}
        onChange={(e) => setProduct(e.target.value)}
      />

      {/* Description */}
      <label className="form-label">📝 Product Description</label>
      <textarea
        placeholder="Describe your product"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      {/* Target Gender */}
      <div className="gender-group">
        <label className="form-label">👤 Target Gender</label>

        <div className="gender-options">
          <label>
            <input
              type="radio"
              value="Male"
              checked={gender === "Male"}
              onChange={(e) => setGender(e.target.value)}
            />
            Male
          </label>

          <label>
            <input
              type="radio"
              value="Female"
              checked={gender === "Female"}
              onChange={(e) => setGender(e.target.value)}
            />
            Female
          </label>

          <label>
            <input
              type="radio"
              value="Both"
              checked={gender === "Both"}
              onChange={(e) => setGender(e.target.value)}
            />
            Both
          </label>
        </div>
      </div>

      {/* Age */}
      <label className="form-label">🎯 Target Audience Age</label>
      <input
        type="text"
        placeholder="Example: 18-30"
        value={age}
        onChange={(e) => setAge(e.target.value)}
      />

      {/* Number of Personas */}
      <label className="form-label">👥 Number of Personas</label>
      <input
        type="number"
        placeholder="1 - 20"
        value={count}
        min="1"
        max="20"
        onChange={(e) => {
          let value = Number(e.target.value);

          if (value > 20) value = 20;
          if (value < 1 && e.target.value !== "") value = 1;

          setCount(value);
        }}
      />

      {/* Research Objective */}
      <label className="form-label">📊 Research Objective</label>
      <input
        type="text"
        placeholder="What do you want to discover?"
        value={objective}
        onChange={(e) => setObjective(e.target.value)}
      />

      <button className="generate-btn" onClick={generate}>
        ✨ Generate Personas
      </button>

      {result && (
        <>
          <div className="stats">
            <div className="stat-box">
              <h3>👍 Preferred</h3>
              <p>{result.preferred}</p>
            </div>

            <div className="stat-box">
              <h3>👎 Not Preferred</h3>
              <p>{result.notPreferred}</p>
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
              <p>{result.personas.length}</p>
            </div>
          </div>

          <div className="grid">
            {result.personas.map((persona, index) => (
              <PersonaCard
                key={index}
                persona={persona}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;