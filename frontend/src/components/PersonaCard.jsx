import "./PersonaCard.css";

function PersonaCard({ persona }) {
  const isYes =
    persona.buyDecision === "Yes" ||
    persona.buyDecision === true;

  return (
    <div className="card">

      {/* Persona Name */}
      <h2>{persona.name}</h2>

      {/* Persona Details */}
      <div className="persona-details">

        <p>
          <strong>Age:</strong> {persona.age}
        </p>

        <p>
          <strong>Occupation:</strong> {persona.occupation}
        </p>

        <p>
          <strong>Personality:</strong> {persona.personality}
        </p>

        <p>
          <strong>Rating:</strong> ⭐ {persona.rating}/5
        </p>

        <p className="decision">
          <strong>Decision:</strong>{" "}
          <span
            className={isYes ? "decision-yes" : "decision-no"}
          >
            {isYes ? "Yes" : "No"}
          </span>
        </p>

      </div>

      {/* Reason */}
      <p className="persona-reason">
        <strong>Reason:</strong>
        <br />
        {persona.reason}
      </p>

    </div>
  );
}

export default PersonaCard;