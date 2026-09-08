import "./PersonaCard.css";

function PersonaCard({ persona }) {
  const isYes =
    persona.buyDecision === "Yes" ||
    persona.buyDecision === true;

  /*
   * =====================================================
   * ADOPTION SCORE
   * =====================================================
   *
   * The score combines:
   * - Persona's 1–5 product rating
   * - Whether the persona said Yes/No
   *
   * Yes + rating:
   *   1/5 → 70%
   *   2/5 → 70%
   *   3/5 → 70%
   *   4/5 → 80%
   *   5/5 → 100%
   *
   * No + rating:
   *   1/5 → 10%
   *   2/5 → 20%
   *   3/5 → 30%
   *   4/5 → 40%
   *   5/5 → 45%
   *
   * This is an adoption score, not a statistically
   * calibrated probability.
   */

  let adoptionScore;

  if (isYes) {
    adoptionScore = Math.max(70, persona.rating * 20);
  } else {
    adoptionScore = Math.min(45, persona.rating * 10);
  }

  /*
   * Adoption label
   */

  let adoptionLabel;

  if (adoptionScore >= 80) {
    adoptionLabel = "Highly likely to adopt";
  } else if (adoptionScore >= 60) {
    adoptionLabel = "Likely to adopt";
  } else if (adoptionScore >= 40) {
    adoptionLabel = "Moderately likely";
  } else {
    adoptionLabel = "Unlikely to adopt";
  }

  return (
    <div className="card">

      {/* =================================================
          PERSONA NAME
      ================================================= */}

      <h2>{persona.name}</h2>


      {/* =================================================
          PERSONA DETAILS
      ================================================= */}

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
          <strong>Rating:</strong>{" "}
          <span className="rating">
            ⭐ {persona.rating}/5
          </span>
        </p>

        <p className="decision">
          <strong>Decision:</strong>{" "}

          <span
            className={
              isYes
                ? "decision-yes"
                : "decision-no"
            }
          >
            {isYes ? "Yes" : "No"}
          </span>
        </p>

      </div>


      {/* =================================================
          ADOPTION SCORE
      ================================================= */}

      <div className="adoption-score">

        <div className="adoption-header">

          <span className="adoption-title">
            Adoption Score
          </span>

          <strong className="adoption-percentage">
            {adoptionScore}%
          </strong>

        </div>


        {/* Progress bar */}

        <div className="adoption-bar">

          <div
            className="adoption-fill"
            style={{
              width: `${adoptionScore}%`,
            }}
          />

        </div>


        {/* Score label */}

        <div
          className={
            isYes
              ? "adoption-label adoption-positive"
              : "adoption-label adoption-negative"
          }
        >
          {adoptionLabel}
        </div>

      </div>


      {/* =================================================
          REASON
      ================================================= */}

      <p className="persona-reason">

        <strong>Reason:</strong>

        <br />

        {persona.reason}

      </p>

    </div>
  );
}

export default PersonaCard;