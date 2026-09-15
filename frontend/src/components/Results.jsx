import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./Results.css";

const API_URL = "http://127.0.0.1:5000";

function Results({
  personas = [],
  preferred,
  notPreferred,
  product = "",
  description = "",
  gender = "Both",
  age = "",
  objective = "",
}) {
  const [insights, setInsights] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [insightError, setInsightError] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);

  const totalPersonas = personas.length;

  const yesCount =
    typeof preferred === "number"
      ? preferred
      : personas.filter(
          (persona) =>
            persona.buyDecision === "Yes" ||
            persona.buyDecision === true
        ).length;

  const noCount =
    typeof notPreferred === "number"
      ? notPreferred
      : Math.max(0, totalPersonas - yesCount);

  const calculateAdoptionScore = (persona) => {
    const rating = Number(persona.rating) || 0;
    const ratingScore = (rating / 5) * 60;
    const decisionScore =
      persona.buyDecision === "Yes" || persona.buyDecision === true
        ? 40
        : 0;

    return Math.round(Math.min(100, ratingScore + decisionScore));
  };

  const scoredPersonas = useMemo(
    () =>
      personas.map((persona) => ({
        ...persona,
        adoptionScore: calculateAdoptionScore(persona),
      })),
    [personas]
  );

  const adoptionScore =
    totalPersonas > 0
      ? Math.round(
          scoredPersonas.reduce(
            (sum, persona) => sum + persona.adoptionScore,
            0
          ) / totalPersonas
        )
      : 0;

  const ratings = personas
    .map((persona) => Number(persona.rating))
    .filter((rating) => Number.isFinite(rating) && rating >= 1 && rating <= 5);

  const averageRating =
    ratings.length > 0
      ? (ratings.reduce((sum, rating) => sum + rating, 0) / ratings.length).toFixed(1)
      : "0.0";

  const wouldUsePercentage =
    totalPersonas > 0 ? Math.round((yesCount / totalPersonas) * 100) : 0;

  const highAdoption = scoredPersonas.filter((p) => p.adoptionScore >= 75).length;
  const moderateAdoption = scoredPersonas.filter(
    (p) => p.adoptionScore >= 50 && p.adoptionScore < 75
  ).length;
  const lowAdoption = scoredPersonas.filter((p) => p.adoptionScore < 50).length;

  const positiveCount = scoredPersonas.filter((p) => p.adoptionScore >= 70).length;
  const neutralCount = scoredPersonas.filter(
    (p) => p.adoptionScore >= 40 && p.adoptionScore < 70
  ).length;
  const negativeCount = scoredPersonas.filter((p) => p.adoptionScore < 40).length;

  const validationStatus =
    adoptionScore >= 75
      ? "Strong Validation"
      : adoptionScore >= 50
      ? "Moderate Validation"
      : "Needs Improvement";

  const validationClass =
    adoptionScore >= 75 ? "strong" : adoptionScore >= 50 ? "moderate" : "weak";

  const sortedPersonas = [...scoredPersonas].sort(
    (a, b) => b.adoptionScore - a.adoptionScore
  );

  const cacheKey = useMemo(() => {
    const ids = personas.map((p, index) => p.id || `${p.name}-${index}`).join("|");
    return `persona-ai-insights-${ids}`;
  }, [personas]);

  const loadInsights = async (forceRefresh = false) => {
    if (!personas.length) return;

    if (!forceRefresh) {
      try {
        const cached = sessionStorage.getItem(cacheKey);
        if (cached) {
          setInsights(JSON.parse(cached));
          return;
        }
      } catch (error) {
        console.warn("Unable to read cached insights:", error);
      }
    }

    try {
      setLoadingInsights(true);
      setInsightError("");

      const response = await axios.post(`${API_URL}/insights`, { personas });
      const data = response.data || {};

      setInsights(data);

      try {
        sessionStorage.setItem(cacheKey, JSON.stringify(data));
      } catch (error) {
        console.warn("Unable to cache insights:", error);
      }
    } catch (error) {
      console.error("Research insights error:", error);
      setInsightError(
        error.response?.data?.error ||
          "Unable to generate AI insights. The quantitative results are still available."
      );
    } finally {
      setLoadingInsights(false);
    }
  };

  useEffect(() => {
    setInsights(null);
    setInsightError("");
    loadInsights(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cacheKey]);

  const asText = (value) => {
    if (value === null || value === undefined) return "";
    if (typeof value === "string" || typeof value === "number") return String(value);
    return (
      value.description ||
      value.reasoning ||
      value.interpretation ||
      value.title ||
      value.topic ||
      value.theme ||
      value.segment ||
      value.evidence ||
      JSON.stringify(value)
    );
  };

  const renderList = (items, emptyText = "No supported findings available.") => {
    if (!Array.isArray(items) || items.length === 0) {
      return <p className="muted-text">{emptyText}</p>;
    }

    return (
      <div className="insight-list">
        {items.map((item, index) => (
          <div className="insight-list-item" key={index}>
            <span className="bullet-dot">•</span>
            <p>{asText(item)}</p>
          </div>
        ))}
      </div>
    );
  };

  const downloadReport = async () => {
    if (!personas.length || isDownloading) return;

    try {
      setIsDownloading(true);

      const response = await axios.post(
        `${API_URL}/generate-report`,
        {
          product,
          description,
          gender,
          age,
          objective,
          personas,
          insights,
        },
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      const safeProduct = (product || "research")
        .trim()
        .replace(/[^a-z0-9]+/gi, "_")
        .replace(/^_+|_+$/g, "");

      link.href = url;
      link.download = `${safeProduct || "research"}_report.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Report generation error:", error);
      alert("Unable to generate the research report. Make sure Flask is running.");
    } finally {
      setIsDownloading(false);
    }
  };

  if (!totalPersonas) {
    return (
      <div className="results-dashboard">
        <div className="results-empty">
          <div className="results-empty-icon">📊</div>
          <h1>Research Results</h1>
          <p>Generate personas first to see your research results.</p>
        </div>
      </div>
    );
  }

  const productScore = insights?.productScore || {};
  const interviewStats = insights?.interviewStats || {};
  const sentiment = insights?.sentiment || {};

  const aiPositive = Number(sentiment.positive);
  const aiNeutral = Number(sentiment.neutral);
  const aiNegative = Number(sentiment.negative);
  const hasAISentiment = [aiPositive, aiNeutral, aiNegative].every(Number.isFinite);

  return (
    <div className="results-dashboard">
      <header className="results-header">
        <div className="results-title-row">
          <div className="results-title-icon">📊</div>
          <div>
            <span className="results-eyebrow">COMBINED RESEARCH</span>
            <h1>Research Results</h1>
            <p>
              Survey results, persona interviews, group interviews and AI insights in one summary.
            </p>
          </div>
        </div>
        <div className="results-persona-pill">👥 {totalPersonas} Personas</div>
      </header>

      <section className="report-download-card">
        <div className="report-download-content">
          <div className="report-download-icon">📄</div>
          <div>
            <span className="section-kicker">RESEARCH REPORT</span>
            <h2>Download complete research summary</h2>
            <p>
              Includes quantitative results, persona opinions, interview summaries and AI-generated insights.
            </p>
          </div>
        </div>
        <button
          type="button"
          className="download-report-btn"
          onClick={downloadReport}
          disabled={isDownloading}
        >
          {isDownloading ? "⏳ Generating..." : "📄 Download PDF"}
        </button>
      </section>

      <section className="results-stats-grid">
        <div className="result-stat-card">
          <span className="result-stat-icon">👥</span>
          <span className="result-stat-label">Total Personas</span>
          <strong>{totalPersonas}</strong>
          <small>Current research sample</small>
        </div>

        <div className="result-stat-card highlight">
          <span className="result-stat-icon">🚀</span>
          <span className="result-stat-label">Adoption Score</span>
          <strong>{adoptionScore}/100</strong>
          <small>{validationStatus}</small>
        </div>

        <div className="result-stat-card">
          <span className="result-stat-icon">⭐</span>
          <span className="result-stat-label">Average Rating</span>
          <strong>{averageRating}/5</strong>
          <small>Persona survey rating</small>
        </div>

        <div className="result-stat-card">
          <span className="result-stat-icon">👍</span>
          <span className="result-stat-label">Would Use / Buy</span>
          <strong>{wouldUsePercentage}%</strong>
          <small>{yesCount} yes • {noCount} no</small>
        </div>
      </section>

      <section className="results-card validation-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">QUANTITATIVE EVIDENCE</span>
            <h2>Product validation</h2>
            <p>Survey ratings and purchase/use decisions provide the quantitative baseline.</p>
          </div>
          <span className={`validation-badge ${validationClass}`}>{validationStatus}</span>
        </div>

        <div className="validation-content">
          <div className="large-score">{adoptionScore}<span>/100</span></div>
          <div className="validation-bar-wrap">
            <div className="validation-bar">
              <div className={`validation-fill ${validationClass}`} style={{ width: `${adoptionScore}%` }} />
            </div>
            <div className="validation-labels">
              <span>Low</span><span>Moderate</span><span>Strong</span>
            </div>
          </div>
        </div>
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">RESEARCH COVERAGE</span>
            <h2>What evidence was analyzed?</h2>
            <p>Results combine the survey with both interview modes.</p>
          </div>
        </div>

        <div className="coverage-grid">
          <div className="coverage-card">
            <div className="coverage-icon">📋</div>
            <div>
              <strong>Persona Survey</strong>
              <span>{totalPersonas} personas • ratings • decisions • reasons</span>
            </div>
            <b>Included</b>
          </div>

          <div className="coverage-card">
            <div className="coverage-icon">🎤</div>
            <div>
              <strong>Individual Interviews</strong>
              <span>{Number(interviewStats.individualPersonas) || 0} personas • {Number(interviewStats.individualResponses) || 0} responses</span>
            </div>
            <b>{interviewStats.hasIndividualInterviews ? "Included" : "Not recorded"}</b>
          </div>

          <div className="coverage-card">
            <div className="coverage-icon">👥</div>
            <div>
              <strong>All-Persona Interviews</strong>
              <span>{Number(interviewStats.allPersonaQuestions) || 0} questions • {Number(interviewStats.allPersonaResponses) || 0} responses</span>
            </div>
            <b>{interviewStats.hasAllPersonaInterviews ? "Included" : "Not recorded"}</b>
          </div>
        </div>
      </section>

      <section className="results-card ai-summary-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">AI RESEARCH SYNTHESIS</span>
            <h2>Overall research insight</h2>
            <p>Generated from survey, individual interviews and all-persona responses.</p>
          </div>
          <button
            type="button"
            className="refresh-insights-btn"
            onClick={() => loadInsights(true)}
            disabled={loadingInsights}
          >
            {loadingInsights ? "⏳ Analyzing..." : "↻ Refresh Analysis"}
          </button>
        </div>

        {loadingInsights && (
          <div className="insights-loading-inline">
            <div className="loading-spinner">AI</div>
            <div>
              <strong>Analyzing the research...</strong>
              <p>Comparing survey responses, individual interviews and all-persona discussions.</p>
            </div>
          </div>
        )}

        {insightError && !loadingInsights && (
          <div className="insight-error-inline">
            <strong>AI insight analysis unavailable</strong>
            <p>{insightError}</p>
          </div>
        )}

        {!loadingInsights && insights && (
          <>
            <div className="ai-summary-main">
              <div className="ai-summary-icon">💡</div>
              <p>{insights.summary || insights.mainFinding || "No AI summary was returned."}</p>
            </div>

            {insights.mainFinding && insights.mainFinding !== insights.summary && (
              <div className="main-finding-box">
                <span>Main Finding</span>
                <p>{insights.mainFinding}</p>
              </div>
            )}
          </>
        )}
      </section>

      <section className="two-column-results">
        <div className="results-card">
          <div className="section-heading compact">
            <div>
              <span className="section-kicker">POSITIVE SIGNALS</span>
              <h2>What is working?</h2>
            </div>
          </div>
          {renderList(insights?.positiveSignals)}
        </div>

        <div className="results-card">
          <div className="section-heading compact">
            <div>
              <span className="section-kicker">CONCERNS</span>
              <h2>What needs attention?</h2>
            </div>
          </div>
          {renderList(insights?.concerns)}
        </div>
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">SENTIMENT</span>
            <h2>Overall research sentiment</h2>
            <p>AI sentiment is shown when interview/survey analysis is available.</p>
          </div>
        </div>

        <div className="sentiment-grid">
          {hasAISentiment ? (
            <>
              <div className="sentiment-card positive">
                <span>😊</span><strong>{aiPositive}%</strong><small>Positive</small>
              </div>
              <div className="sentiment-card neutral">
                <span>😐</span><strong>{aiNeutral}%</strong><small>Neutral</small>
              </div>
              <div className="sentiment-card negative">
                <span>⚠️</span><strong>{aiNegative}%</strong><small>Negative</small>
              </div>
            </>
          ) : (
            <>
              <div className="sentiment-card positive"><span>😊</span><strong>{totalPersonas ? Math.round((positiveCount / totalPersonas) * 100) : 0}%</strong><small>Survey-positive</small></div>
              <div className="sentiment-card neutral"><span>😐</span><strong>{totalPersonas ? Math.round((neutralCount / totalPersonas) * 100) : 0}%</strong><small>Survey-neutral</small></div>
              <div className="sentiment-card negative"><span>⚠️</span><strong>{totalPersonas ? Math.round((negativeCount / totalPersonas) * 100) : 0}%</strong><small>Survey-negative</small></div>
            </>
          )}
        </div>
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">KEY THEMES</span>
            <h2>Recurring themes across the research</h2>
            <p>AI identifies repeated topics from the available research evidence.</p>
          </div>
        </div>

        {Array.isArray(insights?.themes) && insights.themes.length > 0 ? (
          <div className="ai-theme-grid">
            {insights.themes.map((theme, index) => (
              <div className="ai-theme-card" key={index}>
                <div className="ai-theme-number">{index + 1}</div>
                <div>
                  <div className="ai-theme-title-row">
                    <h3>{theme.theme || `Theme ${index + 1}`}</h3>
                    {theme.agreement !== undefined && <span>{theme.agreement}% agreement</span>}
                  </div>
                  {theme.sentiment && <small>{theme.sentiment}</small>}
                  <p>{theme.description || asText(theme)}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted-text">No recurring AI themes are available yet. Run or refresh the analysis after interviews are recorded.</p>
        )}
      </section>

      <section className="two-column-results">
        <div className="results-card">
          <div className="section-heading compact">
            <div>
              <span className="section-kicker">AGREEMENT</span>
              <h2>Where personas agree</h2>
            </div>
          </div>
          {Array.isArray(insights?.agreementPatterns) && insights.agreementPatterns.length > 0 ? (
            <div className="pattern-list">
              {insights.agreementPatterns.map((item, index) => (
                <div className="pattern-card" key={index}>
                  <strong>{item.topic || "Shared opinion"}</strong>
                  {item.percentage !== undefined && <span>{item.percentage}%</span>}
                  <p>{item.description || asText(item)}</p>
                </div>
              ))}
            </div>
          ) : <p className="muted-text">No agreement pattern available.</p>}
        </div>

        <div className="results-card">
          <div className="section-heading compact">
            <div>
              <span className="section-kicker">DISAGREEMENT</span>
              <h2>Where opinions differ</h2>
            </div>
          </div>
          {renderList(insights?.disagreementPatterns, "No meaningful disagreement pattern available.")}
        </div>
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">INTERVIEW DISCOVERIES</span>
            <h2>What interviews added</h2>
            <p>Important findings that emerged from direct persona conversations.</p>
          </div>
        </div>
        {renderList(insights?.interviewDiscoveries, "No interview discoveries are available yet.")}
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">SURVEY VS INTERVIEW</span>
            <h2>How interview evidence compares with the survey</h2>
          </div>
        </div>

        {Array.isArray(insights?.surveyVsInterview) && insights.surveyVsInterview.length > 0 ? (
          <div className="comparison-list">
            {insights.surveyVsInterview.map((item, index) => (
              <div className="comparison-card" key={index}>
                <div className="comparison-header">
                  <strong>{item.topic || `Comparison ${index + 1}`}</strong>
                  {item.direction && <span>{item.direction}</span>}
                </div>
                <div className="comparison-columns">
                  <div><small>Survey</small><p>{item.surveySignal || "—"}</p></div>
                  <div><small>Interview</small><p>{item.interviewSignal || "—"}</p></div>
                </div>
                <div className="comparison-interpretation">
                  {item.interpretation || "No additional interpretation provided."}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted-text">No survey-versus-interview comparison is available yet.</p>
        )}
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">BEHAVIORAL TRENDS</span>
            <h2>How personas behave and decide</h2>
          </div>
        </div>
        {renderList(insights?.behavioralTrends, "No supported behavioral trend is available.")}
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">PERSONA SEGMENTS</span>
            <h2>Differences between user groups</h2>
          </div>
        </div>

        {Array.isArray(insights?.segmentInsights) && insights.segmentInsights.length > 0 ? (
          <div className="segment-grid">
            {insights.segmentInsights.map((segment, index) => (
              <div className="segment-card" key={index}>
                <span>{segment.segment || `Segment ${index + 1}`}</span>
                <strong>{segment.wouldUsePercentage ?? 0}%</strong>
                <small>{segment.personaCount ?? 0} personas • Avg. rating {segment.averageRating ?? 0}/5</small>
                <p>{segment.reasoning || asText(segment)}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted-text">No meaningful segment differences were returned.</p>
        )}
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">INDIVIDUAL PERSONA INSIGHTS</span>
            <h2>What each interviewed persona revealed</h2>
          </div>
        </div>

        {Array.isArray(insights?.individualPersonaInsights) && insights.individualPersonaInsights.length > 0 ? (
          <div className="individual-insight-grid">
            {insights.individualPersonaInsights.map((item, index) => (
              <div className="individual-insight-card" key={index}>
                <div className="individual-insight-header">
                  <strong>{item.personaName || item.name || `Persona ${index + 1}`}</strong>
                  {item.decision && <span>{item.decision}</span>}
                </div>
                <p>{item.insight || item.summary || item.description || asText(item)}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted-text">No individual persona insight is available yet.</p>
        )}
      </section>

      <section className="results-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">PERSONA ADOPTION</span>
            <h2>Individual adoption scores</h2>
            <p>Score = 60% rating + 40% would-use decision.</p>
          </div>
        </div>

        <div className="persona-score-list">
          {sortedPersonas.map((persona, index) => (
            <div className="persona-score-row" key={persona.id || `${persona.name}-${index}`}>
              <div className="persona-rank">#{index + 1}</div>
              <div className="persona-score-avatar">👤</div>
              <div className="persona-score-info">
                <div className="persona-score-name">
                  <strong>{persona.name}</strong>
                  <span>{persona.age} years{persona.occupation ? ` • ${persona.occupation}` : ""}</span>
                </div>
                <div className="persona-score-bar">
                  <div className="score-track">
                    <div className="score-fill" style={{ width: `${persona.adoptionScore}%` }} />
                  </div>
                </div>
              </div>
              <div className="persona-score-value">
                <strong>{persona.adoptionScore}</strong><span>/100</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {sortedPersonas.length > 0 && (
        <section className="results-card">
          <div className="section-heading">
            <div>
              <span className="section-kicker">KEY PERSONA VOICES</span>
              <h2>What your users are saying</h2>
              <p>Survey reasons are shown alongside the AI interview analysis above.</p>
            </div>
          </div>

          <div className="quotes-grid">
            {sortedPersonas.slice(0, 6).map((persona, index) => (
              <div className="quote-card" key={persona.id || `${persona.name}-${index}`}>
                <div className="quote-mark">“</div>
                <p>{persona.reason || "No survey reason provided."}</p>
                <div className="quote-person">
                  <div className="quote-avatar">👤</div>
                  <div>
                    <strong>{persona.name}</strong>
                    <span>Adoption Score: {persona.adoptionScore}/100</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="results-summary">
        <div className="summary-icon">💡</div>
        <div>
          <span>FINAL RESEARCH CONCLUSION</span>
          <h2>
            {insights?.summary ||
              (adoptionScore >= 75
                ? "Strong product potential"
                : adoptionScore >= 50
                ? "Promising, but improvements may be needed"
                : "The product needs further validation")}
          </h2>
          <p>
            The quantitative survey shows <strong>{yesCount} of {totalPersonas}</strong> personas would use or purchase the product, with an average rating of <strong>{averageRating}/5</strong> and an adoption score of <strong>{adoptionScore}/100</strong>. The AI synthesis above incorporates recorded individual and all-persona interviews when available.
          </p>
        </div>
      </section>
    </div>
  );
}

export default Results;
