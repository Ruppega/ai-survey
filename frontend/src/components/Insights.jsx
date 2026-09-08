import React, { useEffect, useState } from "react";
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
          personas,
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
        err.message ||
          "Something went wrong while generating insights."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // AUTOMATIC GENERATION
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
  // HELPERS
  // =========================================================

  const safeNumber = (value, fallback = 0) => {
    const number = Number(value);
    return Number.isFinite(number) ? number : fallback;
  };

  const formatPercentage = (value) => {
    return `${safeNumber(value)}%`;
  };

  const getDirectionClass = (direction) => {
    if (!direction) return "adds-detail";

    const value = String(direction).toLowerCase();

    if (value.includes("supports")) {
      return "supports";
    }

    if (value.includes("challenges")) {
      return "challenges";
    }

    return "adds-detail";
  };

  const getSentimentClass = (sentimentValue) => {
    if (!sentimentValue) return "neutral";

    const value = String(sentimentValue).toLowerCase();

    if (value.includes("positive")) {
      return "positive";
    }

    if (value.includes("negative")) {
      return "negative";
    }

    return "neutral";
  };

  // =========================================================
  // NO PERSONAS
  // =========================================================

  if (!personas || personas.length === 0) {
    return (
      <div className="insights-page">

        <div className="insights-header">
          <div className="header-content">
            <span className="eyebrow">
              AI RESEARCH ANALYSIS
            </span>

            <h1>Research Insights</h1>

            <p>
              Generate personas first to analyze survey
              and interview research.
            </p>
          </div>
        </div>

        <div className="insights-error">
          <div className="error-icon">!</div>

          <h2>No Research Data</h2>

          <p>
            Generate personas before generating research insights.
          </p>
        </div>

      </div>
    );
  }

  // =========================================================
  // LOADING
  // =========================================================

  if (loading && !insights) {
    return (
      <div className="insights-page">

        <div className="insights-header">
          <div className="header-content">
            <span className="eyebrow">
              AI RESEARCH ANALYSIS
            </span>

            <h1>Research Insights</h1>

            <p>
              Analyzing survey responses and interview
              conversations.
            </p>
          </div>
        </div>

        <div className="insights-loading">

          <div className="loading-orb">
            AI
          </div>

          <h2>
            Analyzing Persona Research...
          </h2>

          <p>
            Comparing survey responses, individual interviews,
            group interviews, and behavioral patterns.
          </p>

          <div className="loading-steps">
            <span>Survey Data</span>
            <span>Individual Interviews</span>
            <span>Group Interviews</span>
            <span>Behavior Patterns</span>
          </div>

        </div>

      </div>
    );
  }

  // =========================================================
  // ERROR
  // =========================================================

  if (error && !insights) {
    return (
      <div className="insights-page">

        <div className="insights-header">
          <div className="header-content">

            <span className="eyebrow">
              AI RESEARCH ANALYSIS
            </span>

            <h1>Research Insights</h1>

            <p>
              AI-generated analysis from your persona research.
            </p>

          </div>
        </div>

        <div className="insights-error">

          <div className="error-icon">
            !
          </div>

          <h2>
            Unable to Generate Insights
          </h2>

          <p>
            {error}
          </p>

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

  if (!insights) {
    return null;
  }

  // =========================================================
  // DATA
  // =========================================================

  const productScore =
    insights.productScore || {};

  const sentiment =
    insights.sentiment || {};

  const interviewStats =
    insights.interviewStats || {};

  const totalPersonas =
    safeNumber(productScore.totalPersonas) ||
    personas.length;

  const individualQuestions =
    safeNumber(
      interviewStats.individualResponses
    );

  const individualPersonas =
    safeNumber(
      interviewStats.individualPersonas
    );

  const allPersonaQuestions =
    safeNumber(
      interviewStats.allPersonaQuestions
    );

  const allPersonaResponses =
    safeNumber(
      interviewStats.allPersonaResponses
    );

  const personasInAllInterviews =
    safeNumber(
      interviewStats.allPersonaPersonas
    );

  const totalQuestionsConsidered =
    individualQuestions +
    allPersonaQuestions;

  // =========================================================
  // MAIN UI
  // =========================================================

  return (
    <div className="insights-page">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <header className="insights-header">

        <div className="header-content">

          <span className="eyebrow">
            AI RESEARCH ANALYSIS
          </span>

          <h1>
            Research Insights
          </h1>

          <p>
            AI-generated analysis combining survey responses,
            individual interviews, and all-persona interviews.
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

      </header>


      {/* =====================================================
          DATA SOURCES
      ====================================================== */}

      <section className="data-source-strip">

        {/* SURVEY */}

        <div className="source-item active">

          <div className="source-icon">
            S
          </div>

          <div className="source-info">

            <strong>
              Survey Research
            </strong>

            <span>
              {totalPersonas} personas
            </span>

          </div>

        </div>


        <div className="source-connector" />


        {/* INDIVIDUAL */}

        <div
          className={`source-item ${
            individualQuestions > 0
              ? "active"
              : ""
          }`}
        >

          <div className="source-icon">
            I
          </div>

          <div className="source-info">

            <strong>
              Individual Interviews
            </strong>

            <span>
              {individualQuestions} questions
            </span>

          </div>

        </div>


        <div className="source-connector" />


        {/* GROUP */}

        <div
          className={`source-item ${
            allPersonaQuestions > 0
              ? "active"
              : ""
          }`}
        >

          <div className="source-icon">
            G
          </div>

          <div className="source-info">

            <strong>
              All-Persona Interviews
            </strong>

            <span>
              {allPersonaQuestions} questions
            </span>

          </div>

        </div>

      </section>


      {/* =====================================================
          PRODUCT RECEPTION
      ====================================================== */}

      <section className="insight-section">

        <div className="section-heading">

          <div>

            <span className="section-kicker">
              PRODUCT RECEPTION
            </span>

            <h2>
              Would Users Choose This Product?
            </h2>

          </div>

          <span className="section-badge">
            {totalPersonas} personas analyzed
          </span>

        </div>


        <div className="score-dashboard">

          {/* MAIN SCORE */}

          <div className="main-score-card">

            <div
              className="score-ring"
              style={{
                "--score":
                  `${safeNumber(
                    productScore.wouldUsePercentage
                  ) * 3.6}deg`,
              }}
            >

              <div className="score-ring-inner">

                <strong>
                  {productScore.wouldUsePercentage ?? 0}%
                </strong>

                <span>
                  Would Use
                </span>

              </div>

            </div>

            <h3>
              Product Acceptance
            </h3>

            <p>
              Percentage of personas who indicated that
              they would use or purchase the product.
            </p>

          </div>


          {/* SUPPORTING SCORES */}

          <div className="supporting-score-grid">

            <div className="score-card">

              <span className="score-card-icon">
                ✓
              </span>

              <strong>
                {productScore.preferred ?? 0}
              </strong>

              <span>
                Preferred
              </span>

            </div>


            <div className="score-card">

              <span className="score-card-icon">
                ×
              </span>

              <strong>
                {productScore.notPreferred ?? 0}
              </strong>

              <span>
                Not Preferred
              </span>

            </div>


            <div className="score-card">

              <span className="score-card-icon">
                ★
              </span>

              <strong>
                {productScore.averageRating ?? 0}/5
              </strong>

              <span>
                Average Rating
              </span>

            </div>


            <div className="score-card">

              <span className="score-card-icon">
                P
              </span>

              <strong>
                {totalPersonas}
              </strong>

              <span>
                Personas
              </span>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          KEY TAKEAWAY
      ====================================================== */}

      <section className="insight-section">

        <div className="takeaway-card">

          <div className="takeaway-icon">
            ✦
          </div>

          <div className="takeaway-content">

            <span className="section-kicker">
              KEY TAKEAWAY
            </span>

            <h2>
              What does the research tell us?
            </h2>

            <p>
              {insights.summary ||
                "No overall summary was generated."}
            </p>

          </div>

        </div>

      </section>


      {/* =====================================================
          INTERVIEW QUESTIONS
      ====================================================== */}

      <section className="insight-section interview-questions-section">

        <div className="section-heading interview-heading">

          <div>

            <span className="section-kicker">
              INTERVIEW ANALYSIS
            </span>

            <h2>
              How Many Questions Were Considered?
            </h2>

            <p className="section-description">
              Interview questions included from individual
              persona conversations and all-persona discussions.
            </p>

          </div>

          <div className="questions-total-badge">

            <strong>
              {totalQuestionsConsidered}
            </strong>

            <span>
              Total Questions
            </span>

          </div>

        </div>


        <div className="questions-considered-grid">

          {/* INDIVIDUAL */}

          <div className="question-count-card">

            <div className="question-count-icon">
              I
            </div>

            <div className="question-count-content">

              <span>
                Individual Questions
              </span>

              <strong>
                {individualQuestions}
              </strong>

              <p>
                Questions considered from individual
                persona interviews across{" "}
                {individualPersonas} persona
                {individualPersonas === 1
                  ? ""
                  : "s"}.
              </p>

            </div>

          </div>


          {/* ALL PERSONA */}

          <div className="question-count-card">

            <div className="question-count-icon">
              G
            </div>

            <div className="question-count-content">

              <span>
                All-Persona Questions
              </span>

              <strong>
                {allPersonaQuestions}
              </strong>

              <p>
                Group questions considered across{" "}
                {personasInAllInterviews} persona
                {personasInAllInterviews === 1
                  ? ""
                  : "s"} with{" "}
                {allPersonaResponses} response
                {allPersonaResponses === 1
                  ? ""
                  : "s"}.
              </p>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          SURVEY VS INTERVIEW
      ====================================================== */}

      {Array.isArray(
        insights.surveyVsInterview
      ) &&
        insights.surveyVsInterview.length > 0 && (

        <section className="insight-section">

          <div className="section-heading">

            <div>

              <span className="section-kicker">
                RESEARCH COMPARISON
              </span>

              <h2>
                Survey vs Interview Findings
              </h2>

            </div>

            <span className="section-badge">
              Cross-source analysis
            </span>

          </div>


          <div className="comparison-list">

            {insights.surveyVsInterview.map(
              (item, index) => {

                const directionClass =
                  getDirectionClass(
                    item.direction
                  );

                return (

                  <div
                    className="comparison-card"
                    key={index}
                  >

                    <div className="comparison-number">
                      {index + 1}
                    </div>

                    <div className="comparison-content">

                      <h3>
                        {item.topic}
                      </h3>

                      <div className="comparison-columns">

                        <div className="comparison-column">

                          <span className="comparison-label">
                            Survey Signal
                          </span>

                          <p>
                            {item.surveySignal}
                          </p>

                        </div>


                        <div className="comparison-column">

                          <span className="comparison-label">
                            Interview Signal
                          </span>

                          <p>
                            {item.interviewSignal}
                          </p>

                        </div>

                      </div>


                      <div className="comparison-interpretation">

                        <span
                          className={`direction-badge ${directionClass}`}
                        >
                          {item.direction ||
                            "Adds Detail"}
                        </span>

                        <p>
                          {item.interpretation}
                        </p>

                      </div>

                    </div>

                  </div>

                );
              }
            )}

          </div>

        </section>

      )}


      {/* =====================================================
          SENTIMENT
      ====================================================== */}

      <section className="insight-section">

        <div className="section-heading">

          <div>

            <span className="section-kicker">
              INTERVIEW SENTIMENT
            </span>

            <h2>
              How Do Personas Feel?
            </h2>

          </div>

        </div>


        <div className="sentiment-dashboard">

          <div className="sentiment-bar">

            <div
              className="sentiment-positive"
              style={{
                width:
                  `${safeNumber(
                    sentiment.positive
                  )}%`,
              }}
            />

            <div
              className="sentiment-neutral"
              style={{
                width:
                  `${safeNumber(
                    sentiment.neutral
                  )}%`,
              }}
            />

            <div
              className="sentiment-negative"
              style={{
                width:
                  `${safeNumber(
                    sentiment.negative
                  )}%`,
              }}
            />

          </div>


          <div className="sentiment-legend">

            <div className="sentiment-item">

              <span className="legend-dot positive" />

              <span>
                Positive
              </span>

              <strong>
                {formatPercentage(
                  sentiment.positive
                )}
              </strong>

            </div>


            <div className="sentiment-item">

              <span className="legend-dot neutral" />

              <span>
                Neutral
              </span>

              <strong>
                {formatPercentage(
                  sentiment.neutral
                )}
              </strong>

            </div>


            <div className="sentiment-item">

              <span className="legend-dot negative" />

              <span>
                Negative
              </span>

              <strong>
                {formatPercentage(
                  sentiment.negative
                )}
              </strong>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          INTERVIEW DISCOVERIES
      ====================================================== */}

      {Array.isArray(
        insights.interviewDiscoveries
      ) &&
        insights.interviewDiscoveries.length > 0 && (

        <section className="insight-section">

          <div className="section-heading">

            <div>

              <span className="section-kicker">
                INTERVIEW DISCOVERIES
              </span>

              <h2>
                What Did Interviews Reveal?
              </h2>

            </div>

          </div>


          <div className="discovery-grid">

            {insights.interviewDiscoveries.map(
              (discovery, index) => (

                <div
                  className="discovery-card"
                  key={index}
                >

                  <div className="discovery-top">

                    <span className="discovery-type">
                      {discovery.type ||
                        "Finding"}
                    </span>

                    <span className="discovery-number">
                      {String(index + 1).padStart(
                        2,
                        "0"
                      )}
                    </span>

                  </div>

                  <h3>
                    {discovery.title}
                  </h3>

                  <p>
                    {discovery.description}
                  </p>

                  {discovery.evidence && (

                    <div className="evidence-box">

                      <span>
                        Evidence
                      </span>

                      <p>
                        {discovery.evidence}
                      </p>

                    </div>

                  )}

                </div>

              )
            )}

          </div>

        </section>

      )}


      {/* =====================================================
          RECURRING THEMES
      ====================================================== */}

      <section className="insight-section">

        <div className="section-heading">

          <div>

            <span className="section-kicker">
              RECURRING THEMES
            </span>

            <h2>
              What Keeps Appearing Across Interviews?
            </h2>

          </div>

        </div>


        <div className="themes-list">

          {Array.isArray(insights.themes) &&
          insights.themes.length > 0 ? (

            insights.themes.map(
              (theme, index) => {

                const agreement =
                  safeNumber(
                    theme.agreement
                  );

                return (

                  <div
                    className="theme-card"
                    key={index}
                  >

                    <div className="theme-card-header">

                      <div className="theme-title-area">

                        <span className="theme-number">
                          {index + 1}
                        </span>

                        <h3>
                          {theme.theme}
                        </h3>

                      </div>

                      <span
                        className={`theme-sentiment ${getSentimentClass(
                          theme.sentiment
                        )}`}
                      >
                        {theme.sentiment ||
                          "Neutral"}
                      </span>

                    </div>


                    <p>
                      {theme.description}
                    </p>


                    <div className="theme-agreement">

                      <div className="agreement-header">

                        <span>
                          Persona Agreement
                        </span>

                        <strong>
                          {agreement}%
                        </strong>

                      </div>


                      <div className="mini-progress">

                        <div
                          style={{
                            width:
                              `${Math.min(
                                100,
                                agreement
                              )}%`,
                          }}
                        />

                      </div>

                    </div>

                  </div>

                );
              }
            )

          ) : (

            <div className="empty-insight">
              No recurring themes were identified.
            </div>

          )}

        </div>

      </section>


      {/* =====================================================
          AGREEMENT / DISAGREEMENT
      ====================================================== */}

      <section className="insight-section">

        <div className="two-column-insights">

          {/* AGREEMENT */}

          <div className="pattern-panel">

            <div className="pattern-header">

              <div className="pattern-icon agreement">
                ✓
              </div>

              <div>

                <span className="section-kicker">
                  CONSENSUS
                </span>

                <h2>
                  Agreement Patterns
                </h2>

              </div>

            </div>


            <div className="pattern-list">

              {Array.isArray(
                insights.agreementPatterns
              ) &&
              insights.agreementPatterns.length > 0 ? (

                insights.agreementPatterns.map(
                  (pattern, index) => {

                    const percentage =
                      safeNumber(
                        pattern.percentage
                      );

                    return (

                      <div
                        className="pattern-item"
                        key={index}
                      >

                        <div className="pattern-item-top">

                          <strong>
                            {pattern.topic}
                          </strong>

                          <span>
                            {percentage}%
                          </span>

                        </div>

                        <div className="mini-progress">

                          <div
                            style={{
                              width:
                                `${Math.min(
                                  100,
                                  percentage
                                )}%`,
                            }}
                          />

                        </div>

                        <p>
                          {pattern.description}
                        </p>

                      </div>

                    );
                  }
                )

              ) : (

                <p className="empty-text">
                  No strong agreement patterns
                  were identified.
                </p>

              )}

            </div>

          </div>


          {/* DISAGREEMENT */}

          <div className="pattern-panel">

            <div className="pattern-header">

              <div className="pattern-icon disagreement">
                !
              </div>

              <div>

                <span className="section-kicker">
                  DIVERSITY
                </span>

                <h2>
                  Disagreement Patterns
                </h2>

              </div>

            </div>


            <div className="pattern-list">

              {Array.isArray(
                insights.disagreementPatterns
              ) &&
              insights.disagreementPatterns.length > 0 ? (

                insights.disagreementPatterns.map(
                  (pattern, index) => (

                    <div
                      className="disagreement-item"
                      key={index}
                    >

                      <strong>
                        {pattern.topic}
                      </strong>

                      <p>
                        {pattern.description}
                      </p>

                    </div>

                  )
                )

              ) : (

                <p className="empty-text">
                  No major disagreement patterns
                  were identified.
                </p>

              )}

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          BEHAVIORAL TRENDS
      ====================================================== */}

      <section className="insight-section">

        <div className="section-heading">

          <div>

            <span className="section-kicker">
              BEHAVIOR ANALYSIS
            </span>

            <h2>
              Behavioral Trends
            </h2>

          </div>

        </div>


        <div className="behavior-grid">

          {Array.isArray(
            insights.behavioralTrends
          ) &&
          insights.behavioralTrends.length > 0 ? (

            insights.behavioralTrends.map(
              (trend, index) => (

                <div
                  className="behavior-card"
                  key={index}
                >

                  <span className="behavior-number">
                    {String(index + 1).padStart(
                      2,
                      "0"
                    )}
                  </span>

                  <p>
                    {trend}
                  </p>

                </div>

              )
            )

          ) : (

            <div className="empty-insight">
              No behavioral trends were identified.
            </div>

          )}

        </div>

      </section>


      {/* =====================================================
          INDIVIDUAL PERSONA FINDINGS
      ====================================================== */}

      {Array.isArray(
        insights.individualPersonaInsights
      ) &&
      insights.individualPersonaInsights.length > 0 && (

        <section className="insight-section">

          <div className="section-heading">

            <div>

              <span className="section-kicker">
                INDIVIDUAL PERSONA ANALYSIS
              </span>

              <h2>
                Persona-by-Persona Interview Findings
              </h2>

              <p className="section-description">
                Individual interview responses are compared
                with each persona's original survey decision.
              </p>

            </div>

          </div>


          <div className="individual-persona-grid">

            {insights.individualPersonaInsights.map(
              (personaInsight, index) => (

                <div
                  className="individual-persona-card"
                  key={index}
                >

                  <div className="persona-insight-header">

                    <div className="persona-avatar">
                      {String(
                        personaInsight.persona ||
                          "P"
                      )
                        .charAt(0)
                        .toUpperCase()}
                    </div>

                    <div>

                      <h3>
                        {personaInsight.persona}
                      </h3>

                      <span>
                        Survey Rating:{" "}
                        {personaInsight.surveyRating ??
                          "N/A"}
                        /5
                      </span>

                    </div>

                  </div>


                  <div className="persona-insight-status">

                    <span
                      className={`interview-sentiment ${getSentimentClass(
                        personaInsight.interviewSentiment
                      )}`}
                    >
                      {personaInsight.interviewSentiment ||
                        "Neutral"}
                    </span>

                    <span
                      className={
                        personaInsight.supportsSurvey
                          ? "survey-match"
                          : "survey-difference"
                      }
                    >
                      {personaInsight.supportsSurvey
                        ? "Supports Survey"
                        : "Different From Survey"}
                    </span>

                  </div>


                  <div className="persona-finding">

                    <span>
                      Key Finding
                    </span>

                    <p>
                      {personaInsight.keyFinding}
                    </p>

                  </div>

                </div>

              )
            )}

          </div>

        </section>

      )}


      {/* =====================================================
          SEGMENT INSIGHTS
      ====================================================== */}

      <section className="insight-section">

        <div className="section-heading">

          <div>

            <span className="section-kicker">
              USER SEGMENTS
            </span>

            <h2>
              Persona Segment Insights
            </h2>

          </div>

        </div>


        <div className="segment-grid">

          {Array.isArray(
            insights.segmentInsights
          ) &&
          insights.segmentInsights.length > 0 ? (

            insights.segmentInsights.map(
              (segment, index) => (

                <div
                  className="segment-card"
                  key={index}
                >

                  <div className="segment-card-header">

                    <span className="segment-index">
                      {index + 1}
                    </span>

                    <h3>
                      {segment.segment}
                    </h3>

                  </div>


                  <div className="segment-score">

                    <strong>
                      {segment.wouldUsePercentage ??
                        0}%
                    </strong>

                    <span>
                      would use
                    </span>

                  </div>


                  <div className="segment-rating">

                    <span>
                      Average Rating
                    </span>

                    <strong>
                      {segment.averageRating ??
                        0}/5
                    </strong>

                  </div>


                  <p>
                    {segment.reasoning}
                  </p>

                </div>

              )
            )

          ) : (

            <div className="empty-insight">
              No segment insights were generated.
            </div>

          )}

        </div>

      </section>


      {/* =====================================================
          FINAL CONCLUSION
      ====================================================== */}

      <section className="insight-section">

        <div className="final-conclusion">

          <div className="final-conclusion-icon">
            ✓
          </div>

          <div>

            <span className="section-kicker">
              RESEARCH CONCLUSION
            </span>

            <h2>
              Overall Research Direction
            </h2>

            <p>
              {insights.mainFinding ||
                insights.summary ||
                "The research analysis is complete."}
            </p>


            <div className="conclusion-stats">

              <div>

                <strong>
                  {productScore.wouldUsePercentage ??
                    0}%
                </strong>

                <span>
                  Would Use
                </span>

              </div>


              <div>

                <strong>
                  {productScore.averageRating ??
                    0}/5
                </strong>

                <span>
                  Average Rating
                </span>

              </div>


              <div>

                <strong>
                  {totalQuestionsConsidered}
                </strong>

                <span>
                  Questions Considered
                </span>

              </div>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Insights;