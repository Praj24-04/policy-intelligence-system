import { useEffect, useState } from "react";
import { fetchPolicies, comparePolicies } from "../services/api";
import PolicyCard from "../components/PolicyCard";
import SectorBadge from "../components/SectorBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import { GitCompare, CheckCircle2, XCircle, Lightbulb, RotateCcw } from "lucide-react";

export default function Compare() {
  const [policies,     setPolicies]     = useState([]);
  const [sel1,         setSel1]         = useState(null);
  const [sel2,         setSel2]         = useState(null);
  const [result,       setResult]       = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [step,         setStep]         = useState(1);
  const [sectorFilter, setSectorFilter] = useState("");

  useEffect(() => {
    fetchPolicies(sectorFilter ? { sector: sectorFilter } : {}).then(d => {
      setPolicies(d || []);
    });
  }, [sectorFilter]);

  const handleSelect = (policy) => {
    if (step === 1) { setSel1(policy); setStep(2); }
    else if (step === 2 && policy.id !== sel1.id) {
      setSel2(policy);
      setLoading(true);
      comparePolicies(sel1.id, policy.id).then(r => {
        setResult(r);
        setLoading(false);
        setStep(3);
      });
    }
  };

  const reset = () => { setSel1(null); setSel2(null); setResult(null); setStep(1); };

  return (
    <div style={{ padding: "28px 32px" }}>
      <div className="fade-up" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <div style={{ width: 3, height: 22, background: "#34d399", borderRadius: 2 }} />
              <h1 style={{ fontFamily: "Syne", fontSize: 22, fontWeight: 800, color: "var(--text-main)" }}>
                Policy Comparator
              </h1>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: 13, paddingLeft: 13 }}>
              {step === 1
                ? "Step 1 — Select first policy"
                : step === 2
                ? `Step 2 — Select second policy to compare with "${sel1?.title?.slice(0, 40)}..."`
                : "Comparison complete"}
            </p>
          </div>
          {step > 1 && (
            <button onClick={reset} style={{
              display: "flex", alignItems: "center", gap: 6,
              background: "var(--bg-card)", border: "1px solid var(--border)",
              color: "var(--text-muted)", borderRadius: 8, padding: "8px 14px",
              fontSize: 12, cursor: "pointer",
            }}>
              <RotateCcw size={12} /> Reset
            </button>
          )}
        </div>
      </div>

      {/* Step Indicator */}
      <div className="fade-up fade-up-1" style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        {["Select Policy A", "Select Policy B", "View Insights"].map((label, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "5px 14px", borderRadius: 20,
              background: step > i ? "rgba(34,211,238,0.1)" : "var(--bg-card)",
              border: `1px solid ${step > i ? "rgba(34,211,238,0.3)" : "var(--border)"}`,
              color: step > i ? "var(--cyan)" : "var(--text-dim)",
              fontSize: 12,
            }}>
              <span style={{ fontFamily: "JetBrains Mono", fontSize: 10 }}>0{i + 1}</span>
              {label}
            </div>
            {i < 2 && <div style={{ width: 20, height: 1, background: "var(--border)" }} />}
          </div>
        ))}
      </div>

      {/* Result Panel */}
      {step === 3 && result && !loading && (
        <div className="fade-up" style={{ marginBottom: 24 }}>

          {/* Policy Cards Side by Side */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 16 }}>
            {[result.policy_1, result.policy_2].map((p, i) => (
              <div key={i} className="card" style={{
                padding: "18px 22px",
                borderColor: i === 0 ? "#818cf8" : "var(--cyan)"
              }}>
                <div style={{ fontSize: 10, fontFamily: "JetBrains Mono", color: i === 0 ? "#818cf8" : "var(--cyan)", marginBottom: 8 }}>
                  POLICY {i === 0 ? "A" : "B"}
                </div>
                <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 8 }}>
                  {p.title}
                </div>
                <SectorBadge sector={p.sector} />
                <div style={{ marginTop: 10, display: "flex", gap: 12, fontSize: 12, color: "var(--text-muted)" }}>
                  <span>{p.country}</span>
                  <span>{p.year}</span>
                  <span>{p.region}</span>
                </div>
                {p.tags?.length > 0 && (
                  <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 4 }}>
                    {p.tags.slice(0, 4).map(t => (
                      <span key={t} style={{
                        fontSize: 10, padding: "2px 7px", borderRadius: 4,
                        background: "var(--bg-hover)", color: "var(--text-muted)",
                        border: "1px solid var(--border)", fontFamily: "JetBrains Mono"
                      }}>
                        {t}
                      </span>
                    ))}
                  </div>
                )}

                {/* Unique tags for this policy */}
                {i === 0 && result.unique_to_policy_1?.length > 0 && (
                  <div style={{ marginTop: 10 }}>
                    <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 4 }}>
                      UNIQUE FOCUS AREAS
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                      {result.unique_to_policy_1.slice(0, 3).map(t => (
                        <span key={t} style={{
                          fontSize: 10, padding: "2px 7px", borderRadius: 4,
                          background: "rgba(129,140,248,0.12)",
                          color: "#818cf8",
                          border: "1px solid rgba(129,140,248,0.3)",
                          fontFamily: "JetBrains Mono"
                        }}>
                          ★ {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {i === 1 && result.unique_to_policy_2?.length > 0 && (
                  <div style={{ marginTop: 10 }}>
                    <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 4 }}>
                      UNIQUE FOCUS AREAS
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                      {result.unique_to_policy_2.slice(0, 3).map(t => (
                        <span key={t} style={{
                          fontSize: 10, padding: "2px 7px", borderRadius: 4,
                          background: "rgba(34,211,238,0.1)",
                          color: "var(--cyan)",
                          border: "1px solid rgba(34,211,238,0.25)",
                          fontFamily: "JetBrains Mono"
                        }}>
                          ★ {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Insights Panel */}
          <div className="card" style={{ padding: "22px 26px", borderColor: "rgba(245,158,11,0.25)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Lightbulb size={15} color="#f59e0b" />
              <span style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)" }}>
                AI-Generated Insights
              </span>
            </div>

            {/* Summary Row */}
            <div style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}>
                {result.same_sector
                  ? <><CheckCircle2 size={13} color="#10b981" /><span style={{ color: "#10b981" }}>Same sector</span></>
                  : <><XCircle size={13} color="#f43f5e" /><span style={{ color: "#f43f5e" }}>Different sectors</span></>
                }
              </div>

              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                Shared focus:{" "}
                <span style={{ color: result.shared_tags?.length ? "var(--cyan)" : "var(--text-dim)" }}>
                  {result.shared_tags?.length > 0 ? result.shared_tags.join(", ") : "None"}
                </span>
              </div>
            </div>

            {/* Insight Cards */}
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {result.insights.map((ins, i) => (
                <div key={i} style={{
                  display: "flex", gap: 10, alignItems: "flex-start",
                  padding: "10px 14px", borderRadius: 8,
                  background: "var(--bg-hover)", border: "1px solid var(--border)",
                }}>
                  <div style={{
                    width: 6, height: 6, borderRadius: "50%",
                    background: i % 2 === 0 ? "#f59e0b" : "var(--cyan)",
                    flexShrink: 0, marginTop: 5
                  }} />
                  <span style={{ fontSize: 13, color: "var(--text-main)", lineHeight: 1.6 }}>
                    {ins}
                  </span>
                </div>
              ))}
            </div>

            {/* Source Links */}
            <div style={{ display: "flex", gap: 12, marginTop: 16, paddingTop: 14, borderTop: "1px solid var(--border)" }}>
              {[result.policy_1, result.policy_2].map((p, i) => (
                p.source_url ? (
                  <a key={i} href={p.source_url} target="_blank" rel="noreferrer"
                    style={{
                      fontSize: 11, color: i === 0 ? "#818cf8" : "var(--cyan)",
                      textDecoration: "none", fontFamily: "JetBrains Mono",
                      padding: "4px 10px", borderRadius: 6,
                      border: `1px solid ${i === 0 ? "rgba(129,140,248,0.2)" : "rgba(34,211,238,0.2)"}`,
                      background: i === 0 ? "rgba(129,140,248,0.06)" : "rgba(34,211,238,0.06)",
                    }}>
                    ↗ Policy {i === 0 ? "A" : "B"} Source
                  </a>
                ) : null
              ))}
            </div>
          </div>
        </div>
      )}

      {loading && <LoadingSpinner label="Running comparison analysis..." />}

      {/* Sector Filter + Policy Grid */}
      {step < 3 && (
        <>
          <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
            {["", "AI Governance", "Cybersecurity", "Data Privacy", "Healthcare AI", "Financial Regulation"].map(s => (
              <button key={s} onClick={() => setSectorFilter(s)}
                style={{
                  padding: "6px 14px", borderRadius: 20, fontSize: 12, cursor: "pointer",
                  background: sectorFilter === s ? "rgba(34,211,238,0.15)" : "var(--bg-card)",
                  border: `1px solid ${sectorFilter === s ? "var(--cyan)" : "var(--border)"}`,
                  color: sectorFilter === s ? "var(--cyan)" : "var(--text-muted)",
                }}>
                {s || "All Sectors"}
              </button>
            ))}
          </div>

          <div style={{ maxHeight: 600, overflowY: "auto", paddingRight: 4 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 12 }}>
              {policies.map((p, i) => (
                <PolicyCard
                  key={p.id} policy={p} delay={(i % 5) + 1}
                  selectable selected={sel1?.id === p.id}
                  onSelect={handleSelect}
                />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}