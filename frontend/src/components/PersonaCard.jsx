import "./PersonaCard.css";
function PersonaCard({ persona }) {
  return (
    <div className="card">
      <h2>{persona.name}</h2>

      <p><strong>Age:</strong> {persona.age}</p>

      <p><strong>Occupation:</strong> {persona.occupation}</p>

      <p><strong>Personality:</strong> {persona.personality}</p>

      <p><strong>Rating:</strong> ⭐ {persona.rating}/5</p>

      <p>
        <strong>Decision:</strong>{" "}
        <span style={{ color: persona.buyDecision === "Yes" ? "green" : "red" }}>
          {persona.buyDecision}
        </span>
      </p>

      <p>{persona.reason}</p>
    </div>
  );
}

export default PersonaCard;