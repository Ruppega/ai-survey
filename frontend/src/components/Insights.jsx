import React, { useEffect, useRef, useState } from "react";
import "./Insights.css";

const API_URL = "http://127.0.0.1:5000";

function Insights({ personas }) {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =========================================================
  // GENERATE INSIGHTS
  // =========================================================

  const generateInsights = async () => {
    if (!personas || personas.length === 0) {
      setInsights(null);
      setError("No personas are available for insight analysis.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/insights`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          personas: personas,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Failed to generate insights."
        );
      }

      setInsights(data);

    } catch (err) {
      console.error("Insight generation error:", err);

      setError(
        err.message || "Something went wrong while generating insights."
      );

    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // AUTOMATICALLY GENERATE WHEN PERSONAS CHANGE
  // =========================================================

  useEffect(() => {
    if (!personas || personas.length === 0) {
      setInsights(null);
      setError("No personas are available for insight analysis.");
      return;
    }

    generateInsights();
  }, [personas]);

  // =========================================================
  // NO PERSONAS
  // =========================================================

  if (!personas || personas.length === 0) {
    return (
      <div className="insights-page">
        <div className="insights-header">
          <div>
            <h1>Research Insights</h1>

            <p>
              Generate personas first to analyze research insights.
            </p>
          </div>
        </div>

        <div className="insights-error">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="insights-page">

        <div className="insights-header">
          <div>
            <h1>Research Insights</h1>

            <p>
              AI-generated analysis of your current persona research.
            </p>
          </div>
        </div>

        <div className="insights-loading">

          <h2>Analyzing Persona Research...</h2>

          <p>
            Gemini is analyzing persona preferences,
            ratings, reasons, and interview responses.
          </p>

        </div>

      </div>
    );
  }

  // =========================================================
  // ERROR
  // =========================================================

  if (error) {
    return (
      <div className="insights-page">

        <div className="insights-header">

          <div>
            <h1>Research Insights</h1>

            <p>
              AI-generated insights from your current persona
              research and interviews.
            </p>
          </div>

        </div>

        <div className="insights-error">

          <h2>Unable to Generate Insights</h2>

          <p>{error}</p>

          <button
            className="refresh-insights-btn"
            onClick={generateInsights}
          >
            Try Again
          </button>

        </div>

      </div>
    );
  }

  // =========================================================
  // WAITING FOR DATA
  // =========================================================

  if (!insights) {
    return null;
  }

  const productScore = insights.productScore || {};
  const sentiment = insights.sentiment || {};

  return (
    <div className="insights-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="insights-header">

        <div>

          <h1>Research Insights</h1>

          <p>
            AI-generated insights from your current persona
            research and interviews.
          </p>

        </div>

        <button
          className="refresh-insights-btn"
          onClick={generateInsights}
          disabled={loading}
        >
          {loading
            ? "Analyzing..."
            : "Regenerate Insights"}
        </button>

      </div>


      {/* =====================================================
          PRODUCT SCORE
      ===================================================== */}

      <section className="insight-section">

        <h2>Would Use This Product?</h2>

        <div className="score-grid">

          {/* WOULD USE */}

          <div className="score-card">

            <span className="score-value">
              {productScore.wouldUsePercentage ?? 0}%
            </span>

            <span className="score-label">
              Would Use
            </span>

          </div>


          {/* PREFERRED */}

          <div className="score-card">

            <span className="score-value">
              {productScore.preferred ?? 0}
            </span>

            <span className="score-label">
              Preferred
            </span>

          </div>


          {/* NOT PREFERRED */}

          <div className="score-card">

            <span className="score-value">
              {productScore.notPreferred ?? 0}
            </span>

            <span className="score-label">
              Not Preferred
            </span>

          </div>


          {/* AVERAGE RATING */}

          <div className="score-card">

            <span className="score-value">
              {productScore.averageRating ?? 0}/5
            </span>

            <span className="score-label">
              Average Rating
            </span>

          </div>

        </div>

      </section>


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <section className="insight-section">

        <h2>Overall Summary</h2>

        <div className="summary-card">

          <p>
            {insights.summary ||
              "No summary was generated."}
          </p>

        </div>

      </section>


      {/* =====================================================
          SENTIMENT
      ===================================================== */}

      <section className="insight-section">

        <h2>Sentiment Breakdown</h2>

        <div className="sentiment-grid">

          {/* POSITIVE */}

          <div className="sentiment-card">

            <span>
              Positive
            </span>

            <strong>
              {sentiment.positive ?? 0}%
            </strong>

          </div>


          {/* NEUTRAL */}

          <div className="sentiment-card">

            <span>
              Neutral
            </span>

            <strong>
              {sentiment.neutral ?? 0}%
            </strong>

          </div>


          {/* NEGATIVE */}

          <div className="sentiment-card">

            <span>
              Negative
            </span>

            <strong>
              {sentiment.negative ?? 0}%
            </strong>

          </div>

        </div>

      </section>


      {/* =====================================================
          RECURRING THEMES
      ===================================================== */}

      <section className="insight-section">

        <h2>Recurring Themes</h2>

        <div className="themes-list">

          {Array.isArray(insights.themes) &&
          insights.themes.length > 0 ? (

            insights.themes.map(
              (theme, index) => (

                <div
                  className="theme-card"
                  key={index}
                >

                  <div className="theme-card-header">

                    <h3>
                      {theme.theme}
                    </h3>

                    <span className="theme-sentiment">
                      {theme.sentiment}
                    </span>

                  </div>

                  <p>
                    {theme.description}
                  </p>

                </div>

              )
            )

          ) : (

            <p>
              No recurring themes were identified.
            </p>

          )}

        </div>

      </section>


      {/* =====================================================
          AGREEMENT PATTERNS
      ===================================================== */}

      <section className="insight-section">

        <h2>Agreement Patterns</h2>

        <div className="insight-list">

          {Array.isArray(insights.agreementPatterns) &&
          insights.agreementPatterns.length > 0 ? (

            insights.agreementPatterns.map(
              (pattern, index) => (

                <div
                  className="list-item"
                  key={index}
                >

                  <span className="list-number">
                    {index + 1}
                  </span>

                  <p>
                    {pattern}
                  </p>

                </div>

              )
            )

          ) : (

            <p>
              No agreement patterns were identified.
            </p>

          )}

        </div>

      </section>


      {/* =====================================================
          BEHAVIORAL TRENDS
      ===================================================== */}

      <section className="insight-section">

        <h2>Behavioral Trends</h2>

        <div className="insight-list">

          {Array.isArray(insights.behavioralTrends) &&
          insights.behavioralTrends.length > 0 ? (

            insights.behavioralTrends.map(
              (trend, index) => (

                <div
                  className="list-item"
                  key={index}
                >

                  <span className="list-number">
                    {index + 1}
                  </span>

                  <p>
                    {trend}
                  </p>

                </div>

              )
            )

          ) : (

            <p>
              No behavioral trends were identified.
            </p>

          )}

        </div>

      </section>


      {/* =====================================================
          SEGMENT INSIGHTS
      ===================================================== */}

      <section className="insight-section">

        <h2>Persona Segment Insights</h2>

        <div className="segment-grid">

          {Array.isArray(insights.segmentInsights) &&
          insights.segmentInsights.length > 0 ? (

            insights.segmentInsights.map(
              (segment, index) => (

                <div
                  className="segment-card"
                  key={index}
                >

                  <h3>
                    {segment.segment}
                  </h3>

                  <div className="segment-score">
                    {segment.wouldUsePercentage ?? 0}%
                  </div>

                  <p>
                    {segment.reasoning}
                  </p>

                </div>

              )
            )

          ) : (

            <p>
              No segment insights were generated.
            </p>

          )}

        </div>

      </section>

    </div>
  );
}

export default Insights;