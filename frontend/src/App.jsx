import { useState } from "react";
import axios from "axios";
import PersonaCard from "./components/PersonaCard";
import "./App.css";

function App() {
  const [product, setProduct] = useState("");
  const [description, setDescription] = useState("");
  const [age, setAge] = useState("");
  const [objective, setObjective] = useState("");
  const [count, setCount] = useState(20);

  const [result, setResult] = useState(null);

  const generate = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/generate", {
        product,
        description,
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
      <h1>Synthetic Persona Generator</h1>

      <input
        type="text"
        placeholder="Product Name"
        value={product}
        onChange={(e) => setProduct(e.target.value)}
      />

      <textarea
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <input
        type="text"
        placeholder="Target Audience Age"
        value={age}
        onChange={(e) => setAge(e.target.value)}
      />

      {/* Number of Personas */}
      <input
        type="number"
        placeholder="Number of Personas (1-20)"
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

      <input
        type="text"
        placeholder="Research Objective"
        value={objective}
        onChange={(e) => setObjective(e.target.value)}
      />

      <button onClick={generate}>
        Generate Personas
      </button>

      {result && (
        <>
          <h2>
            {result.preferred} / {result.personas.length} Prefer
          </h2>

          <h3>
            {Math.round(
              (result.preferred * 100) / result.personas.length
            )}
            % Prefer
          </h3>

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