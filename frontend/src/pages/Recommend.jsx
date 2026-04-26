import { useEffect, useState } from "react";
import { fetchPolicies, fetchRecommendations, submitFeedback } from "../services/api";
import SectorBadge from "../components/SectorBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import { Sparkles, Globe2, CheckCircle2 } from "lucide-react";

const MaturityColor = {
  nascent:    { bg: "rgba(244,63,94,0.1)",  border: "rgba(244,63,94,0.2)",  text: "#f43f5e" },
  emerging:   { bg: "rgba(245,158,11,0.1)", border: "rgba(245,158,11,0.2)", text: "#f59e0b" },
  developing: { bg: "rgba(99,102,241,0.1)", border: "rgba(99,102,241,0.2)", text: "#a5b4fc" },
  advanced:   { bg: "rgba(16,185,129,0.1)", border: "rgba(16,185,129,0.2)", text: "#10b981" },
};

export default function Recommend() {
  const [policies,      setPolicies]      = useState([]);
  const [selected,      setSelected]      = useState(null);
  const [result,        setResult]        = useState(null);
  const [loading,       setLoading]       = useState(false);
  const [sector,        setSector]        = useState("");
  const [feedbackGiven, setFeedbackGiven] = useState({});

  useEffect(() => {
    fetchPolicies({}).then(d => setPolicies(d || []));
  }, []);

  const handleSelect = (policy) => {
    setSelected(policy);
    setResult(null);
    setFeedbackGiven({});
    setLoading(true);
    fetchRecommendations(policy.id, 6).then(r => {
      setResult(r);
      setLoading(false);
    });
  };

  const handleFeedback = async (country, helpful) => {
    if (!result?.source_policy?.id) return;
    await submitFeedback(result.source_policy.id, country, helpful);
    setFeedbackGiven(prev => ({
      ...prev,
      [country]: helpful ? "positive" : "negative"
    }));
  };

  const filtered = sector
    ? policies.filter(p => p.sector === sector)
    : policies;

  return (
    <div style={{ padding: "28px 32px" }}>

      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div style={{ width: 3, height: 22, background: "#a78bfa", borderRadius: 2 }} />
          <h1 style={{ fontFamily: "Syne", fontSize: 22, fontWeight: 800, color: "var(--text-main)" }}>
            Policy Recommender
          </h1>
          <div style={{
            display: "flex", alignItems: "center", gap: 6, marginLeft: 8,
            padding: "3px 10px", borderRadius: 20,
            background: "rgba(167,139,250,0.1)",
            border: "1px solid rgba(167,139,250,0.2)"
          }}>
            <Sparkles size={11} color="#a78bfa" />
            <span style={{ fontSize: 11, color: "#a78bfa", fontFamily: "JetBrains Mono" }}>
              ML POWERED
            </span>
          </div>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, paddingLeft: 13 }}>
          Select a policy to discover which countries would benefit most from adopting it
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20, alignItems: "start" }}>

        {/* Left Panel */}
        <div>
          <div className="card fade-up fade-up-1" style={{ padding: "14px 16px", marginBottom: 12 }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono", marginBottom: 10 }}>
              FILTER BY SECTOR
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {["", "AI Governance", "Cybersecurity", "Data Privacy", "Healthcare AI", "Financial Regulation"].map(s => (
                <button key={s} onClick={() => setSector(s)} style={{
                  padding: "7px 12px", borderRadius: 8,
                  textAlign: "left", fontSize: 12, cursor: "pointer",
                  background: sector === s ? "rgba(167,139,250,0.1)" : "transparent",
                  border: `1px solid ${sector === s ? "rgba(167,139,250,0.3)" : "transparent"}`,
                  color: sector === s ? "#a78bfa" : "var(--text-muted)",
                }}>
                  {s || "All Sectors"} ({s ? policies.filter(p => p.sector === s).length : policies.length})
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 520, overflowY: "auto", paddingRight: 2 }}>
            {filtered.map((p, i) => (
              <div key={p.id}
                className={`card fade-up fade-up-${(i % 4) + 1}`}
                onClick={() => handleSelect(p)}
                style={{
                  padding: "12px 14px", cursor: "pointer",
                  borderColor: selected?.id === p.id ? "#a78bfa" : undefined,
                  background: selected?.id === p.id ? "rgba(167,139,250,0.07)" : undefined,
                }}>
                <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 12, color: "var(--text-main)", marginBottom: 6, lineHeight: 1.3 }}>
                  {p.title}
                </div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <SectorBadge sector={p.sector} />
                  <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
                    {p.country?.slice(0, 12)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel */}
        <div>
          {!selected && !loading && (
            <div className="card fade-up" style={{ padding: 48, textAlign: "center" }}>
              <Globe2 size={36} color="var(--text-dim)" style={{ margin: "0 auto 16px", display: "block" }} />
              <div style={{ fontFamily: "Syne", fontSize: 16, color: "var(--text-muted)", marginBottom: 8 }}>
                Select a policy to generate recommendations
              </div>
              <div style={{ fontSize: 13, color: "var(--text-dim)" }}>
                The ML engine will analyze the policy and identify countries with the highest adoption need
              </div>
            </div>
          )}

          {loading && <LoadingSpinner label="Running ML recommendation engine..." />}

          {result && !loading && (
            <div className="fade-up">

              {/* Source Policy Banner */}
              <div className="card" style={{
                padding: "16px 20px", marginBottom: 16,
                borderColor: "rgba(167,139,250,0.3)",
                background: "rgba(167,139,250,0.05)"
              }}>
                <div style={{ fontSize: 11, color: "#a78bfa", fontFamily: "JetBrains Mono", marginBottom: 6 }}>
                  ANALYZING POLICY
                </div>
                <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 15, color: "var(--text-main)", marginBottom: 8 }}>
                  {result.source_policy.title}
                </div>
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <SectorBadge sector={result.source_policy.sector} />
                  <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    Origin: {result.source_policy.country}
                  </span>
                  <span style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono" }}>
                    Cluster #{result.source_policy.cluster} · {result.total_countries_analyzed} countries analyzed
                  </span>
                </div>
              </div>

              {/* ML Method Badge */}
              <div style={{
                fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono",
                marginBottom: 14, padding: "6px 12px",
                background: "var(--bg-card)", border: "1px solid var(--border)",
                borderRadius: 8, display: "inline-block"
              }}>
                ⚙ {result.ml_method}
              </div>

              {/* Recommendation Cards */}
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {result.recommendations.map((rec, i) => {
                  const mc = MaturityColor[rec.regulatory_maturity] || MaturityColor.developing;
                  return (
                    <div key={rec.country}
                      className={`card fade-up fade-up-${i + 1}`}
                      style={{ padding: "18px 22px" }}>

                      {/* Country Header */}
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                            <span style={{ fontFamily: "Syne", fontWeight: 800, fontSize: 16, color: "var(--text-main)" }}>
                              #{i + 1} {rec.country}
                            </span>
                            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>· {rec.region}</span>
                            {rec.already_has_sector ? (
                              <span style={{ fontSize: 10, padding: "1px 7px", borderRadius: 4, background: "rgba(100,116,139,0.1)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>
                                Has sector
                              </span>
                            ) : (
                              <span style={{ fontSize: 10, padding: "1px 7px", borderRadius: 4, background: "rgba(244,63,94,0.08)", color: "#f43f5e", border: "1px solid rgba(244,63,94,0.2)" }}>
                                Missing sector
                              </span>
                            )}
                          </div>
                          <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 4, background: mc.bg, color: mc.text, border: `1px solid ${mc.border}`, fontFamily: "JetBrains Mono" }}>
                            {rec.regulatory_maturity} maturity
                          </span>
                        </div>

                        {/* Need Score */}
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 2 }}>
                            NEED SCORE
                          </div>
                          <div style={{
                            fontFamily: "Syne", fontWeight: 800, fontSize: 28,
                            color: rec.need_score > 0.6 ? "#f43f5e" : rec.need_score > 0.4 ? "#f59e0b" : "#10b981"
                          }}>
                            {Math.round(rec.need_score * 100)}%
                          </div>
                        </div>
                      </div>

                      {/* Score Bar */}
                      <div style={{ height: 3, background: "var(--border)", borderRadius: 2, marginBottom: 12 }}>
                        <div style={{
                          height: "100%", borderRadius: 2,
                          width: `${rec.need_score * 100}%`,
                          background: rec.need_score > 0.6 ? "#f43f5e" : rec.need_score > 0.4 ? "#f59e0b" : "#10b981",
                          transition: "width 0.8s ease"
                        }} />
                      </div>

                      {/* Reasoning */}
                      <div style={{ background: "var(--bg-hover)", border: "1px solid var(--border)", borderRadius: 8, padding: "10px 14px", marginBottom: 12 }}>
                        <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 6 }}>
                          WHY THIS COUNTRY
                        </div>
                        <p style={{ fontSize: 12, color: "var(--text-main)", lineHeight: 1.65 }}>
                          {rec.reasoning}
                        </p>
                      </div>

                      {/* Expected Benefits */}
                      <div style={{ marginBottom: 14 }}>
                        <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 8 }}>
                          EXPECTED BENEFITS
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                          {rec.expected_benefits.map((b, j) => (
                            <div key={j} style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
                              <CheckCircle2 size={12} color="#10b981" style={{ flexShrink: 0, marginTop: 2 }} />
                              <span style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>{b}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* ── Feedback Buttons ── INSIDE the map, after benefits */}
                      <div style={{
                        display: "flex", alignItems: "center", gap: 8,
                        paddingTop: 12, borderTop: "1px solid var(--border)"
                      }}>
                        <span style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginRight: 4 }}>
                          WAS THIS RELEVANT?
                        </span>
                        <button onClick={() => handleFeedback(rec.country, true)} style={{
                          padding: "4px 14px", borderRadius: 6, cursor: "pointer", fontSize: 12,
                          background: feedbackGiven[rec.country] === "positive" ? "rgba(16,185,129,0.2)" : "rgba(16,185,129,0.08)",
                          border: `1px solid ${feedbackGiven[rec.country] === "positive" ? "rgba(16,185,129,0.5)" : "rgba(16,185,129,0.2)"}`,
                          color: "#10b981",
                          fontWeight: feedbackGiven[rec.country] === "positive" ? 700 : 400,
                          transition: "all 0.2s",
                        }}>
                          👍 {feedbackGiven[rec.country] === "positive" ? "Marked Helpful" : "Helpful"}
                        </button>
                        <button onClick={() => handleFeedback(rec.country, false)} style={{
                          padding: "4px 14px", borderRadius: 6, cursor: "pointer", fontSize: 12,
                          background: feedbackGiven[rec.country] === "negative" ? "rgba(244,63,94,0.2)" : "rgba(244,63,94,0.08)",
                          border: `1px solid ${feedbackGiven[rec.country] === "negative" ? "rgba(244,63,94,0.5)" : "rgba(244,63,94,0.2)"}`,
                          color: "#f43f5e",
                          fontWeight: feedbackGiven[rec.country] === "negative" ? 700 : 400,
                          transition: "all 0.2s",
                        }}>
                          👎 {feedbackGiven[rec.country] === "negative" ? "Marked Irrelevant" : "Not Relevant"}
                        </button>
                      </div>

                    </div>
                  );
                })}
              </div>

              {/* Similar Policies */}
              {result.similar_policies?.length > 0 && (
                <div className="card" style={{ padding: "16px 20px", marginTop: 16 }}>
                  <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 12 }}>
                    THEMATICALLY SIMILAR POLICIES (COSINE SIMILARITY)
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {result.similar_policies.map((p, i) => (
                      <div key={i} style={{
                        display: "flex", justifyContent: "space-between", alignItems: "center",
                        padding: "8px 12px", borderRadius: 8,
                        background: "var(--bg-hover)", border: "1px solid var(--border)"
                      }}>
                        <div>
                          <div style={{ fontSize: 12, color: "var(--text-main)", fontWeight: 500 }}>{p.title}</div>
                          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{p.country} · {p.sector}</div>
                        </div>
                        <div style={{ fontFamily: "JetBrains Mono", fontSize: 13, color: "var(--cyan)" }}>
                          {Math.round(p.similarity * 100)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
}