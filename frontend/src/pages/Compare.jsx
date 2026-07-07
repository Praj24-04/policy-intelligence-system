import { useEffect, useState, useRef } from "react";
import { fetchPolicies, comparePolicies, getToken, BASE } from "../services/api";
import SectorBadge from "../components/SectorBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import { GitCompare, CheckCircle2, XCircle, Lightbulb, RotateCcw, FileDown, Search } from "lucide-react";

export default function Compare() {
  const [policies,     setPolicies]     = useState([]);
  const [sel1,         setSel1]         = useState(null);
  const [sel2,         setSel2]         = useState(null);
  const [result,       setResult]       = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [step,         setStep]         = useState(1);
  const [sectorFilter, setSectorFilter] = useState("");
  const [search,       setSearch]       = useState("");

  const reportRef = useRef(null);

  const filtered = policies.filter(p => {
    if (!search) return true;
    const query = search.toLowerCase();
    return (
      (p.title && p.title.toLowerCase().includes(query)) ||
      (p.country && p.country.toLowerCase().includes(query)) ||
      (p.sector && p.sector.toLowerCase().includes(query))
    );
  });

  useEffect(() => {
    fetchPolicies(sectorFilter ? { sector: sectorFilter } : {}).then(d => {
      setPolicies(d || []);
    });
  }, [sectorFilter]);

  const handleSelect = (policy) => {
    if (step === 1) {
      setSel1(policy);
      setStep(2);
    } else if (step === 2 && policy.id !== sel1.id) {
      setSel2(policy);
      setLoading(true);
      comparePolicies(sel1.id, policy.id).then(r => {
        setResult(r);
        setLoading(false);
        setStep(3);
      });
    }
  };

  const reset = () => {
    setSel1(null);
    setSel2(null);
    setResult(null);
    setStep(1);
  };

  const handleDownloadPDF = () => {
    if (!sel1 || !sel2) return;
    const downloadUrl = `${BASE}/compare/download?id1=${sel1.id}&id2=${sel2.id}`;
    window.open(downloadUrl, '_blank');
  };

  // Sector filter list mapping
  const filterMapping = [
    { label: "All Sectors", value: "" },
    { label: "AI Governance", value: "AI Governance" },
    { label: "Cybersecurity", value: "Cybersecurity" },
    { label: "Data Privacy", value: "Data Privacy" },
    { label: "Financial Regulation", value: "Financial Regulation" },
    { label: "Healthcare AI", value: "Healthcare AI" },
    { label: "ESG", value: "ESG Policies" },
    { label: "IoT", value: "IoT and Robotics" },
    { label: "POSH", value: "POSH Policies" }
  ];

  // Helper section divider component
  const SectionDivider = ({ label }) => (
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
      <div style={{ width: "20px", height: "1px", backgroundColor: "var(--border)" }} />
      <span style={{
        fontSize: "12px",
        fontFamily: "JetBrains Mono",
        color: "var(--text-muted)",
        letterSpacing: "0.12em",
        fontWeight: 500,
        textTransform: "uppercase"
      }}>
        {label}
      </span>
      <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border)" }} />
    </div>
  );

  return (
    <div style={{
      flex: 1,
      overflowY: "auto",
      background: "var(--bg-deep)",
      minHeight: "100vh"
    }}>
      <style>{`
        .policy-select-card:hover {
          border-color: var(--border-lit) !important;
          box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }
        .action-btn-hover:hover {
          background-color: var(--bg-hover) !important;
          border-color: var(--border-lit) !important;
        }
        .reset-btn-hover:hover {
          color: var(--text-main) !important;
        }
      `}</style>

      <div style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "32px 40px",
        width: "100%"
      }}>
        {/* PAGE HEADER (Always visible) */}
        <div style={{ marginBottom: "24px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "6px" }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--cyan)", backgroundColor: "var(--cyan)" }}></span>
            <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)", letterSpacing: "0.05em" }}>
              PREP / COMPARE
            </span>
          </div>
          <h1 style={{ 
            fontFamily: "'DM Sans', sans-serif", 
            fontSize: "52px", 
            fontWeight: 700, 
            color: "var(--text-main)",
            margin: "0 0 16px 0",
            letterSpacing: "-1.5px",
            lineHeight: "1.1"
          }}>
            Compare <span className="half-highlight-custom">policies.</span>
          </h1>
          <p style={{ fontFamily: "DM Sans", fontSize: "14px", color: "var(--text-muted)", margin: 0 }}>
            Select two policies to generate a structured intelligence comparison report.
          </p>
        </div>

        {/* STEP INDICATOR (steps 1 and 2 only) */}
        {step < 3 && (
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "24px" }}>
            {[
              { num: "01", label: "Select Policy A", stepNum: 1 },
              { num: "02", label: "Select Policy B", stepNum: 2 },
              { num: "03", label: "View Report", stepNum: 3 }
            ].map((s, idx) => {
              const isActive = step === s.stepNum;
              const isCompleted = step > s.stepNum;

              let bg = "var(--bg-card)";
              let border = "1px solid var(--border)";
              let color = "var(--text-dim)";
              let weight = "normal";

              if (isActive) {
                border = "1px solid var(--text-main)";
                color = "var(--text-main)";
                weight = "600";
              } else if (isCompleted) {
                border = "1px solid var(--cyan)";
                bg = "var(--accent-light)";
                color = "var(--stat-label)";
              }

              return (
                <div key={idx} style={{ display: "flex", alignItems: "center" }}>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "5px 14px",
                    borderRadius: "20px",
                    background: bg,
                    backgroundColor: bg,
                    border: border,
                    color: color,
                    fontSize: "12px",
                    fontFamily: "DM Sans",
                    fontWeight: weight
                  }}>
                    {isCompleted ? (
                      <span style={{ fontSize: "10px", fontWeight: "bold" }}>✓</span>
                    ) : (
                      <span style={{ fontFamily: "JetBrains Mono", fontSize: "9px" }}>{s.num}</span>
                    )}
                    <span>{s.label}</span>
                  </div>
                  {idx < 2 && (
                    <div style={{ width: "24px", height: "1px", borderTop: "1px solid var(--border)", margin: "0 8px" }} />
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* SECTOR FILTER + POLICY GRID (steps 1 & 2) */}
        {step < 3 && (
          <>
            {/* Search Input */}
            <div style={{ position: "relative", marginBottom: "16px", width: "100%" }}>
              <span style={{ 
                position: "absolute", 
                left: 16, 
                top: "50%", 
                transform: "translateY(-50%)",
                pointerEvents: "none",
                display: "flex",
                alignItems: "center",
                color: "var(--text-dim)"
              }}>
                <Search size={16} />
              </span>
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search policies by title, sector, or country..."
                className="search-input-custom"
                style={{
                  width: "100%",
                  height: 48,
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "0 16px 0 44px",
                  outline: "none",
                  fontSize: "14px",
                  fontFamily: "'DM Sans', sans-serif",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.02)"
                }}
              />
            </div>

            {/* Filter pills row */}
            <div style={{ display: "flex", gap: "8px", marginBottom: "16px", flexWrap: "wrap", alignItems: "center" }}>
              {filterMapping.map(f => {
                const isActive = sectorFilter === f.value;
                return (
                  <button
                    key={f.label}
                    onClick={() => setSectorFilter(f.value)}
                    style={{
                      padding: "6px 14px",
                      borderRadius: "20px",
                      fontSize: "12px",
                      fontFamily: "DM Sans",
                      cursor: "pointer",
                      transition: "all 0.15s ease",
                      outline: "none",
                      border: isActive ? "1px solid var(--cyan)" : "none",
                      background: isActive ? "var(--accent-light)" : "transparent",
                      backgroundColor: isActive ? "var(--accent-light)" : "transparent",
                      color: isActive ? "var(--stat-label)" : "var(--text-dim)"
                    }}
                  >
                    {f.label}
                  </button>
                );
              })}
 
              {/* Policy count */}
              <div style={{ marginLeft: "auto", fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                Showing {filtered.length} policies
              </div>
            </div>

            {/* SELECTION SUMMARY BAR (appears after step 1) */}
            {step > 1 && sel1 && (
              <div style={{
                padding: "10px 16px",
                background: "var(--bg-hover)",
                backgroundColor: "var(--bg-hover)",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                marginBottom: "12px",
                display: "flex",
                alignItems: "center",
                gap: "16px"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>POLICY A:</span>
                  <span style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-main)" }}>{sel1.title}</span>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#2563eb", backgroundColor: "#2563eb" }}></span>
                </div>
                <div style={{ width: "1px", height: "16px", background: "var(--border)", backgroundColor: "var(--border)" }} />
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>POLICY B:</span>
                  {sel2 ? (
                    <>
                      <span style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-main)" }}>{sel2.title}</span>
                      <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--cyan)", backgroundColor: "var(--cyan)" }}></span>
                    </>
                  ) : (
                    <span style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-dim)", fontStyle: "italic" }}>
                      Select from grid below
                    </span>
                  )}
                </div>
                <button
                  onClick={reset}
                  className="reset-btn-hover"
                  style={{
                    marginLeft: "auto",
                    background: "none",
                    border: "none",
                    fontSize: "10px",
                    fontFamily: "JetBrains Mono",
                    color: "var(--text-dim)",
                    cursor: "pointer",
                    outline: "none",
                    padding: 0
                  }}
                >
                  ↺ RESET
                </button>
              </div>
            )}

            {/* Policy selection grid */}
            <div style={{ maxHeight: "520px", overflowY: "auto", paddingRight: "4px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px" }}>
                {filtered.map((p) => {
                  const isSelectedA = sel1?.id === p.id;
                  const isSelectedB = sel2?.id === p.id;

                  return (
                    <div
                      key={p.id}
                      onClick={() => handleSelect(p)}
                      className="policy-select-card"
                      style={{
                        position: "relative",
                        background: "var(--bg-card)",
                        border: isSelectedA 
                          ? "2px solid #2563eb" 
                          : isSelectedB 
                          ? "2px solid #5c9e2e" 
                          : "1px solid var(--border)",
                        backgroundColor: isSelectedA
                          ? "rgba(37,99,235,0.05)"
                          : isSelectedB
                          ? "rgba(163,230,53,0.05)"
                          : "var(--bg-card)",
                        borderRadius: "8px",
                        padding: "14px 16px",
                        cursor: "pointer",
                        transition: "all 0.2s ease",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between",
                        minHeight: "110px"
                      }}
                    >
                      {/* Selection Badge A/B top-left corner */}
                      {isSelectedA && (
                        <div style={{
                          position: "absolute",
                          top: "-6px",
                          left: "-6px",
                          width: "14px",
                          height: "14px",
                          borderRadius: "50%",
                          background: "#2563eb",
                          backgroundColor: "#2563eb",
                          color: "#ffffff",
                          fontSize: "8px",
                          fontWeight: "bold",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center"
                        }}>
                          A
                        </div>
                      )}
                      {isSelectedB && (
                        <div style={{
                          position: "absolute",
                          top: "-6px",
                          left: "-6px",
                          width: "14px",
                          height: "14px",
                          borderRadius: "50%",
                          background: "#5c9e2e",
                          backgroundColor: "#5c9e2e",
                          color: "#ffffff",
                          fontSize: "8px",
                          fontWeight: "bold",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center"
                        }}>
                          B
                        </div>
                      )}

                      {/* Top Row */}
                      <div style={{ display: "flex", gap: "10px", alignItems: "flex-start", marginBottom: "12px" }}>
                        {/* Avatar */}
                        <div style={{
                          width: "28px",
                          height: "28px",
                          borderRadius: "50%",
                          background: "var(--bg-hover)",
                          backgroundColor: "var(--bg-hover)",
                          color: "var(--text-main)",
                          fontSize: "12px",
                          fontWeight: "600",
                          fontFamily: "DM Sans",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          flexShrink: 0
                        }}>
                          {p.title ? p.title.charAt(0).toUpperCase() : "P"}
                        </div>
                        
                        {/* Title */}
                        <div style={{ flex: 1 }}>
                          <div style={{
                            fontSize: "13px",
                            fontWeight: "500",
                            color: "var(--text-main)",
                            fontFamily: "DM Sans",
                            lineHeight: "1.35",
                            display: "-webkit-box",
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: "vertical",
                            overflow: "hidden"
                          }}>
                            {p.title}
                          </div>
                        </div>

                        {/* Sector badge top-right */}
                        <div style={{
                          fontSize: "9px",
                          fontFamily: "JetBrains Mono",
                          display: "flex",
                          alignItems: "center",
                          gap: "4px",
                          color: "var(--stat-label)",
                          background: "var(--accent-light)",
                          backgroundColor: "var(--accent-light)",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          whiteSpace: "nowrap"
                        }}>
                          <span style={{ width: "4px", height: "4px", borderRadius: "50%", background: "var(--cyan)", backgroundColor: "var(--cyan)" }}></span>
                          {p.sector ? p.sector.slice(0, 10) : "General"}
                        </div>
                      </div>

                      {/* Bottom Row */}
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)", textTransform: "uppercase" }}>
                          {p.country || "GLOBAL"}
                        </span>
                        <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                          {p.year || "N/A"}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {/* LOADING STATE */}
        {loading && (
          <div style={{ textAlign: "center", padding: "60px 0" }}>
            <LoadingSpinner />
            <div style={{ fontFamily: "DM Sans", fontSize: "13px", color: "var(--text-muted)", marginTop: "14px" }}>
              Generating comparison report...
            </div>
            <div style={{ fontFamily: "JetBrains Mono", fontSize: "11px", color: "var(--text-dim)", marginTop: "6px" }}>
              Analyzing {sel1?.title} against {sel2?.title}
            </div>
          </div>
        )}

        {/* COMPARISON REPORT (step 3 — full output) */}
        {step === 3 && result && !loading && (
          <div
            ref={reportRef}
            id="comparison-report"
            style={{
              maxWidth: "900px",
              margin: "0 auto",
              background: "var(--bg-card)"
            }}
          >
            {/* SECTION 0 — REPORT HEADER */}
            <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ fontSize: "9px", fontFamily: "JetBrains Mono", color: "var(--text-dim)", letterSpacing: "0.12em", fontWeight: "bold" }}>
                    POLICY COMPARISON REPORT
                  </div>
                  <div style={{ fontSize: "11px", fontFamily: "DM Sans", color: "var(--text-dim)", marginTop: "4px" }}>
                    {new Date().toLocaleDateString('en-US', {
                      year: 'numeric', month: 'long', day: 'numeric'
                    })}
                  </div>
                </div>
                
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={reset}
                    className="action-btn-hover"
                    style={{
                      border: "1px solid var(--border)",
                      background: "#ffffff",
                      backgroundColor: "#ffffff",
                      color: "var(--text-muted)",
                      fontSize: "12px",
                      fontFamily: "DM Sans",
                      padding: "8px 14px",
                      borderRadius: "6px",
                      cursor: "pointer",
                      outline: "none",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px"
                    }}
                  >
                    ↺ New Comparison
                  </button>
                  <button
                    onClick={handleDownloadPDF}
                    style={{
                      background: "#0a0a0a",
                      backgroundColor: "#0a0a0a",
                      color: "#ffffff",
                      fontSize: "12px",
                      fontFamily: "DM Sans",
                      fontWeight: 600,
                      padding: "8px 16px",
                      letterSpacing: "0.02em",
                      borderRadius: "6px",
                      cursor: "pointer",
                      outline: "none",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      border: "none"
                    }}
                  >
                    <FileDown size={12} /> Download PDF
                  </button>
                </div>
              </div>
              <div style={{ height: "1px", borderTop: "1px solid var(--border)", marginTop: "16px" }} />
            </div>

            {/* SECTION 1 — ORIENTATION (Policy Cards) */}
            <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
              <SectionDivider label="01 ORIENTATION" />
              
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                {[(result.policy1 || result.policy_1), (result.policy2 || result.policy_2)].map((p, idx) => {
                  if (!p) return null;
                  const isA = idx === 0;

                  return (
                    <div
                      key={idx}
                      style={{
                        padding: "22px 28px",
                        border: "1px solid var(--border)",
                        borderRadius: "8px",
                        boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
                        borderTop: `3px solid ${isA ? "#2563eb" : "#5c9e2e"}`
                      }}
                    >
                      <div style={{
                        fontSize: "11px",
                        fontFamily: "JetBrains Mono",
                        color: isA ? "#2563eb" : "#5c9e2e",
                        marginBottom: "8px",
                        fontWeight: "600",
                        letterSpacing: "0.14em"
                      }}>
                        POLICY {isA ? "A" : "B"}
                      </div>
                      <h3 style={{
                        fontFamily: "DM Sans",
                        fontSize: "16px",
                        fontWeight: 600,
                        color: "var(--text-main)",
                        margin: "0 0 6px 0",
                        lineHeight: 1.3
                      }}>
                        {p.title}
                      </h3>
                      
                      <div style={{ marginBottom: "12px" }}>
                        <SectorBadge sector={p.sector} />
                      </div>

                      <div style={{ display: "flex", flexDirection: "column" }}>
                        {[
                          { label: "Jurisdiction", val: p.country },
                          { label: "Year Enacted", val: p.year },
                          { label: "Region", val: p.region },
                          { label: "Status", val: p.status || "Active" },
                          { label: "Version", val: p.version || "1.0" }
                        ].map((row, rIdx) => (
                          <div
                            key={rIdx}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              padding: "6px 0",
                              borderBottom: rIdx < 4 ? "1px solid #eeeeee" : "none"
                            }}
                          >
                            <span style={{
                              fontSize: "12px",
                              fontFamily: "JetBrains Mono",
                              color: "var(--text-muted)",
                              fontWeight: 400,
                              textTransform: "uppercase"
                            }}>
                              {row.label}
                            </span>
                            <span style={{
                              fontSize: "14px",
                              fontFamily: "DM Sans",
                              fontWeight: 500,
                              color: "var(--text-main)"
                            }}>
                              {row.val || "N/A"}
                            </span>
                          </div>
                        ))}
                      </div>

                      {p.source_url && (
                        <div style={{ marginTop: "12px" }}>
                          <a
                            href={p.source_url}
                            target="_blank"
                            rel="noreferrer"
                            style={{
                              fontSize: "10px",
                              fontFamily: "JetBrains Mono",
                              color: "#5c9e2e",
                              textDecoration: "none"
                            }}
                          >
                            View Source ↗
                          </a>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* SECTION 2 — VERDICT */}
            <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
              <SectionDivider label="02 SIMILARITY VERDICT" />

              <div style={{
                padding: "22px 28px",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
                display: "flex",
                gap: "24px"
              }}>
                {/* Left Side (35%) */}
                <div style={{ width: "35%", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ fontSize: "48px", fontFamily: "DM Sans", fontWeight: 700, color: "var(--text-main)", lineHeight: 1 }}>
                      {Math.round((result.overall_metrics?.composite_score || 0) * 100)}%
                    </div>
                    <div style={{ fontSize: "15px", fontFamily: "DM Sans", fontWeight: 600, color: "#5c9e2e", marginTop: "6px" }}>
                      {result.overall_metrics?.similarity_label || "Moderately Aligned"}
                    </div>
                  </div>
                  
                  {/* Score bar */}
                  <div style={{ marginTop: "16px" }}>
                    <div style={{ width: "100%", height: "4px", background: "#f0f0f0", borderRadius: "2px", overflow: "hidden" }}>
                      <div style={{
                        width: `${Math.round((result.overall_metrics?.composite_score || 0) * 100)}%`,
                        height: "100%",
                        background: (result.overall_metrics?.composite_score || 0) > 0.8 
                          ? "#5c9e2e" 
                          : (result.overall_metrics?.composite_score || 0) > 0.6 
                          ? "#d97706" 
                          : (result.overall_metrics?.composite_score || 0) > 0.4 
                          ? "#2563eb" 
                          : "#dc2626",
                        borderRadius: "2px",
                        transition: "width 0.8s ease"
                      }} />
                    </div>
                  </div>
                </div>

                {/* Divider */}
                <div style={{ width: "1px", background: "var(--border)", backgroundColor: "var(--border)" }} />

                {/* Right Side (65%) */}
                <div style={{ width: "65%" }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "12px" }}>
                    {[
                      { 
                        label: "Theme & Concept Match", 
                        val: result.overall_metrics?.semantic_similarity,
                        tooltip: "Measures the overlap of overall themes, statutory concepts, and core regulatory intentions between the two documents."
                      },
                      { 
                        label: "Detailed Provision Match", 
                        val: result.overall_metrics?.cross_encoder_normalized,
                        tooltip: "A clause-by-clause comparison that evaluates how closely the specific rules and requirements correspond to one another."
                      },
                      { 
                        label: "Regulatory Scope Overlap", 
                        val: result.overall_metrics?.jaccard_coefficient,
                        tooltip: "Indicates the proportion of shared operational domains, technology scopes, and target sectors covered by both frameworks."
                      }
                    ].map((row, rIdx) => (
                      <div 
                        key={rIdx} 
                        title={row.tooltip}
                        style={{ 
                          display: "flex", 
                          alignItems: "center", 
                          gap: "12px", 
                          cursor: "help",
                          padding: "2px 0"
                        }}
                      >
                        <span style={{ 
                          fontSize: "12px", 
                          fontFamily: "JetBrains Mono", 
                          color: "var(--text-muted)", 
                          width: "205px",
                          borderBottom: "1px dotted var(--text-muted)",
                          display: "inline-block"
                        }}>
                          {row.label}
                        </span>
                        <div style={{ flex: 1, height: "4px", background: "var(--bg-hover)", borderRadius: "2px", overflow: "hidden" }}>
                          <div style={{
                            width: `${Math.round((row.val || 0) * 100)}%`,
                            height: "100%",
                            background: "#5c9e2e",
                            backgroundColor: "#5c9e2e"
                          }} />
                        </div>
                        <span style={{
                          fontSize: "13px",
                          fontFamily: "JetBrains Mono",
                          fontWeight: 500,
                          color: "var(--text-main)",
                          width: "40px",
                          textAlign: "right"
                        }}>
                          {Math.round((row.val || 0) * 100)}%
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Summary Box */}
                  <div style={{
                    background: "var(--bg-hover)",
                    backgroundColor: "var(--bg-hover)",
                    border: "1px solid var(--border)",
                    borderRadius: "6px",
                    padding: "12px 14px"
                  }}>
                    {(() => {
                      const composite = result.overall_metrics?.composite_score || 0;
                      let verdictText = "";
                      if (composite > 0.8) verdictText = "These policies are nearly identical in approach and coverage. Compliance with one substantially satisfies the other.";
                      else if (composite > 0.65) verdictText = "Strong alignment exists on core principles. Key differences lie in enforcement mechanisms and jurisdictional scope.";
                      else if (composite > 0.5) verdictText = "Moderate overlap with meaningful divergence. Shared values but distinct implementation approaches reflect different regulatory contexts.";
                      else if (composite > 0.35) verdictText = "Limited alignment. These policies address related domains but through fundamentally different frameworks and priorities.";
                      else verdictText = "Distinct approaches. These policies represent contrasting regulatory philosophies and are best understood as complementary rather than comparable.";
                      
                      return (
                        <p style={{
                          fontSize: "14px",
                          fontFamily: "DM Sans",
                          color: "var(--text-muted)",
                          margin: 0,
                          lineHeight: 1.7
                        }}>
                          {verdictText}
                        </p>
                      );
                    })()}
                  </div>
                </div>
              </div>
            </div>

            {/* Page Break Hint */}
            <div className="pdf-page-break" style={{ display: "none" }} />

            {/* SECTION 3 — SHARED COVERAGE */}
            {result.shared_tags?.length > 0 && (
              <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
                <SectionDivider label="03 SHARED COVERAGE" />
                
                <div style={{
                  padding: "22px 28px",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                    <span style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                      Both policies address these areas
                    </span>
                    <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                      {result.shared_tags.length} shared themes
                    </span>
                  </div>

                  <div style={{ height: "2px", background: "var(--border)", backgroundColor: "var(--border)", marginBottom: "14px" }} />

                  {/* Pills */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                    {result.shared_tags.map((t, tIdx) => (
                      <div
                        key={tIdx}
                        style={{
                          background: "#f0f7e8",
                          backgroundColor: "#f0f7e8",
                          border: "1px solid rgba(92,158,46,0.25)",
                          borderRadius: "4px",
                          padding: "5px 12px",
                          display: "flex",
                          alignItems: "center",
                          gap: "6px"
                        }}
                      >
                        <span style={{ color: "#5c9e2e", fontSize: "10px", fontWeight: "bold" }}>✓</span>
                        <span style={{
                          fontSize: "12px",
                          fontWeight: 500,
                          letterSpacing: "0.06em",
                          fontFamily: "JetBrains Mono",
                          color: "#3d6b1e",
                          textTransform: "uppercase"
                        }}>
                          {t}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Insight box */}
                  <div style={{
                    background: "var(--bg-hover)",
                    backgroundColor: "var(--bg-hover)",
                    border: "1px solid var(--border)",
                    borderLeft: "3px solid #5c9e2e",
                    borderRadius: "6px",
                    padding: "10px 14px",
                    marginTop: "14px"
                  }}>
                    <p style={{
                      fontSize: "14px",
                      fontFamily: "DM Sans",
                      color: "var(--text-muted)",
                      margin: 0,
                      lineHeight: 1.7
                    }}>
                      Implementing these {result.shared_tags.length} areas satisfies overlapping obligations across both jurisdictions — reducing compliance duplication.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* SECTION 4 — COVERAGE GAPS */}
            <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
              <SectionDivider label="04 COVERAGE GAPS" />

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                {/* Left Column — Policy A */}
                <div style={{
                  border: "1px solid var(--border)",
                  borderTop: "3px solid #2563eb",
                  borderRadius: "0 0 8px 8px",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
                  padding: "18px 20px"
                }}>
                  <div style={{
                    fontSize: "11px",
                    fontFamily: "JetBrains Mono",
                    color: "#2563eb",
                    marginBottom: "4px",
                    fontWeight: "600",
                    letterSpacing: "0.14em"
                  }}>
                    UNIQUE TO POLICY A
                  </div>
                  <h4 style={{
                    fontSize: "14px",
                    fontFamily: "DM Sans",
                    fontWeight: 600,
                    color: "var(--text-main)",
                    margin: "0 0 14px 0"
                  }}>
                    {(result.policy_1?.title || result.policy1?.title || "Policy A").slice(0, 30)}...
                  </h4>

                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {result.only_policy1_tags?.length > 0 ? (
                      result.only_policy1_tags.map((t, idx) => (
                        <div key={idx} style={{ display: "flex", alignItems: "center", gap: "8px", borderLeft: "3px solid #bfdbfe", paddingLeft: "10px" }}>
                          <span style={{
                            fontSize: "13px",
                            fontFamily: "DM Sans",
                            fontWeight: 500,
                            color: "#1f2937",
                            textTransform: "capitalize"
                          }}>
                            {t}
                          </span>
                        </div>
                      ))
                    ) : (
                      <span style={{ fontSize: "12px", fontFamily: "DM Sans", fontStyle: "italic", color: "var(--text-dim)" }}>
                        No unique provisions identified.
                      </span>
                    )}
                  </div>
                </div>

                {/* Right Column — Policy B */}
                <div style={{
                  border: "1px solid var(--border)",
                  borderTop: "3px solid #5c9e2e",
                  borderRadius: "0 0 8px 8px",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
                  padding: "18px 20px"
                }}>
                  <div style={{
                    fontSize: "11px",
                    fontFamily: "JetBrains Mono",
                    color: "#5c9e2e",
                    marginBottom: "4px",
                    fontWeight: "600",
                    letterSpacing: "0.14em"
                  }}>
                    UNIQUE TO POLICY B
                  </div>
                  <h4 style={{
                    fontSize: "14px",
                    fontFamily: "DM Sans",
                    fontWeight: 600,
                    color: "var(--text-main)",
                    margin: "0 0 14px 0"
                  }}>
                    {(result.policy_2?.title || result.policy2?.title || "Policy B").slice(0, 30)}...
                  </h4>

                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {result.only_policy2_tags?.length > 0 ? (
                      result.only_policy2_tags.map((t, idx) => (
                        <div key={idx} style={{ display: "flex", alignItems: "center", gap: "8px", borderLeft: "3px solid #bbf7d0", paddingLeft: "10px" }}>
                          <span style={{
                            fontSize: "13px",
                            fontFamily: "DM Sans",
                            fontWeight: 500,
                            color: "#1f2937",
                            textTransform: "capitalize"
                          }}>
                            {t}
                          </span>
                        </div>
                      ))
                    ) : (
                      <span style={{ fontSize: "12px", fontFamily: "DM Sans", fontStyle: "italic", color: "var(--text-dim)" }}>
                        No unique provisions identified.
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Gaps dynamic insight box */}
              {((result.only_policy1_tags?.length || 0) > 0 || (result.only_policy2_tags?.length || 0) > 0) && (
                <div style={{
                  background: "var(--bg-hover)",
                  backgroundColor: "var(--bg-hover)",
                  border: "1px solid var(--border)",
                  borderLeft: "3px solid #d97706",
                  borderRadius: "6px",
                  padding: "12px 14px",
                  marginTop: "14px"
                }}>
                  <p style={{
                    fontSize: "14px",
                    fontFamily: "DM Sans",
                    color: "var(--text-muted)",
                    margin: 0,
                    lineHeight: 1.7
                  }}>
                    These gaps represent areas where one jurisdiction has chosen to regulate specifically. Organizations operating across both must address {(result.only_policy1_tags?.length || 0) + (result.only_policy2_tags?.length || 0)} additional distinct requirements.
                  </p>
                </div>
              )}
            </div>

            {/* Page Break Hint */}
            <div className="pdf-page-break" style={{ display: "none" }} />

            {/* SECTION 5 — DIMENSIONAL ANALYSIS */}
            {result.dimensional_breakdown && (
              <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
                <SectionDivider label="05 REGULATORY DIMENSIONS" />
                
                <div style={{
                  padding: "22px 28px",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
                }}>
                  <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)", marginBottom: "20px" }}>
                    How each policy scores across 6 regulatory dimensions
                  </div>

                  {/* Legend row */}
                  <div style={{ display: "flex", gap: "20px", marginBottom: "16px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{ width: "8px", height: "8px", background: "#2563eb", backgroundColor: "#2563eb", display: "inline-block" }}></span>
                      <span style={{ fontSize: "11px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>Policy A</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{ width: "8px", height: "8px", background: "#5c9e2e", backgroundColor: "#5c9e2e", display: "inline-block" }}></span>
                      <span style={{ fontSize: "11px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>Policy B</span>
                    </div>
                  </div>

                  {/* Dimensions list */}
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    {Object.entries(result.dimensional_breakdown).map(([dimName, info], idx) => (
                      <div
                        key={dimName}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "16px",
                          marginBottom: "16px",
                          paddingBottom: "16px",
                          borderBottom: idx < 5 ? "1px solid #f5f5f5" : "none"
                        }}
                      >
                        <span style={{
                          width: "130px",
                          flexShrink: 0,
                          fontSize: "13px",
                          fontFamily: "DM Sans",
                          fontWeight: 600,
                          color: "#1f2937",
                          textTransform: "capitalize"
                        }}>
                          {dimName}
                        </span>

                        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "6px" }}>
                          {/* Bar A */}
                          <div style={{ width: "100%", height: "8px", background: "#f5f5f5", borderRadius: "4px", overflow: "hidden" }}>
                            <div style={{
                              width: `${Math.round((info.strength_policy1 || 0) * 100)}%`,
                              height: "100%",
                              background: "#2563eb",
                              backgroundColor: "#2563eb",
                              opacity: 0.85,
                              borderRadius: "4px"
                            }} />
                          </div>
                          {/* Bar B */}
                          <div style={{ width: "100%", height: "8px", background: "#f5f5f5", borderRadius: "4px", overflow: "hidden" }}>
                            <div style={{
                              width: `${Math.round((info.strength_policy2 || 0) * 100)}%`,
                              height: "100%",
                              background: "#5c9e2e",
                              backgroundColor: "#5c9e2e",
                              opacity: 0.85,
                              borderRadius: "4px"
                            }} />
                          </div>
                        </div>

                        {/* Dominant label */}
                        <div style={{
                          width: "60px",
                          textAlign: "right",
                          fontSize: "11px",
                          fontFamily: "JetBrains Mono",
                          fontWeight: 500,
                          color: info.dominant === "policy1" ? "#2563eb" : info.dominant === "policy2" ? "#5c9e2e" : "#9ca3af"
                        }}>
                          {info.dominant === "policy1" ? "A stronger" : info.dominant === "policy2" ? "B stronger" : "Equal"}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* SECTION 6 — PHILOSOPHY & APPROACH */}
            <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
              <SectionDivider label="06 REGULATORY PHILOSOPHY" />

              <div style={{
                padding: "22px 28px",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
              }}>
                <div style={{ display: "flex", gap: "24px" }}>
                  {/* Left philosophy column */}
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: "11px",
                      fontFamily: "JetBrains Mono",
                      color: "var(--text-muted)",
                      marginBottom: "4px",
                      fontWeight: 500,
                      letterSpacing: "0.1em"
                    }}>
                      POLICY A APPROACH
                    </div>
                    <div style={{ fontSize: "22px", fontFamily: "DM Sans", fontWeight: 700, color: "var(--text-main)", marginBottom: "10px" }}>
                      {(result.policy_1?.approach || result.policy1?.approach || "Standard")}
                    </div>
                    
                    <p style={{
                      fontSize: "14px",
                      fontFamily: "DM Sans",
                      color: "var(--text-muted)",
                      margin: 0,
                      lineHeight: 1.7
                    }}>
                      This policy prioritizes {(() => {
                        const app = (result.policy_1?.approach || result.policy1?.approach || "").toLowerCase();
                        if (app.includes("compliance")) return "strict adherence through defined obligations and penalty structures";
                        if (app.includes("risk")) return "proportionate response based on assessed harm potential";
                        if (app.includes("principles")) return "broad values over specific rules, allowing adaptive implementation";
                        if (app.includes("innovation")) return "enabling new technologies while managing emerging risks";
                        if (app.includes("safety")) return "precautionary approach with mandatory human oversight requirements";
                        if (app.includes("voluntary") || app.includes("soft")) return "industry self-regulation guided by recommended frameworks";
                        return "a standardized set of requirements for operational compliance";
                      })()}.
                    </p>
                  </div>

                  {/* Vertical Divider */}
                  <div style={{ width: "1px", background: "var(--border)", backgroundColor: "var(--border)" }} />

                  {/* Right philosophy column */}
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: "11px",
                      fontFamily: "JetBrains Mono",
                      color: "var(--text-muted)",
                      marginBottom: "4px",
                      fontWeight: 500,
                      letterSpacing: "0.1em"
                    }}>
                      POLICY B APPROACH
                    </div>
                    <div style={{ fontSize: "22px", fontFamily: "DM Sans", fontWeight: 700, color: "var(--text-main)", marginBottom: "10px" }}>
                      {(result.policy_2?.approach || result.policy2?.approach || "Standard")}
                    </div>
                    
                    <p style={{
                      fontSize: "14px",
                      fontFamily: "DM Sans",
                      color: "var(--text-muted)",
                      margin: 0,
                      lineHeight: 1.7
                    }}>
                      This policy prioritizes {(() => {
                        const app = (result.policy_2?.approach || result.policy2?.approach || "").toLowerCase();
                        if (app.includes("compliance")) return "strict adherence through defined obligations and penalty structures";
                        if (app.includes("risk")) return "proportionate response based on assessed harm potential";
                        if (app.includes("principles")) return "broad values over specific rules, allowing adaptive implementation";
                        if (app.includes("innovation")) return "enabling new technologies while managing emerging risks";
                        if (app.includes("safety")) return "precautionary approach with mandatory human oversight requirements";
                        if (app.includes("voluntary") || app.includes("soft")) return "industry self-regulation guided by recommended frameworks";
                        return "a standardized set of requirements for operational compliance";
                      })()}.
                    </p>
                  </div>
                </div>

                {/* Philosophical alignment insight box */}
                <div style={{
                  background: "var(--bg-hover)",
                  backgroundColor: "var(--bg-hover)",
                  border: "1px solid var(--border)",
                  borderLeft: `3px solid ${(result.policy_1?.approach || result.policy1?.approach) !== (result.policy_2?.approach || result.policy2?.approach) ? "#d97706" : "#5c9e2e"}`,
                  borderRadius: "6px",
                  padding: "12px 14px",
                  marginTop: "14px"
                }}>
                  {(() => {
                    const app1 = result.policy_1?.approach || result.policy1?.approach || "Standard";
                    const app2 = result.policy_2?.approach || result.policy2?.approach || "Standard";
                    
                    if (app1 !== app2) {
                      return (
                        <p style={{
                          fontSize: "14px",
                          fontFamily: "DM Sans",
                          color: "var(--text-muted)",
                          margin: 0,
                          lineHeight: 1.7
                        }}>
                          These policies represent different regulatory philosophies. {app1} frameworks typically offer more legal certainty but less flexibility. {app2} frameworks allow faster adaptation but may create compliance ambiguity.
                        </p>
                      );
                    } else {
                      return (
                        <p style={{
                          fontSize: "14px",
                          fontFamily: "DM Sans",
                          color: "var(--text-muted)",
                          margin: 0,
                          lineHeight: 1.7
                        }}>
                          Both policies share a {app1} philosophy, suggesting alignment in regulatory intent despite differences in specific provisions.
                        </p>
                      );
                    }
                  })()}
                </div>
              </div>
            </div>

            {/* Page Break Hint */}
            <div className="pdf-page-break" style={{ display: "none" }} />

            {/* SECTION 7 — AI INSIGHTS */}
            <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
              <SectionDivider label="07 INTELLIGENCE INSIGHTS" />

              <div style={{
                padding: "22px 28px",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <Lightbulb size={14} color="#d97706" />
                    <span style={{ fontSize: "13px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                      Generated by ML analysis
                    </span>
                  </div>
                  <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                    {result.insights?.length || 0} insights
                  </span>
                </div>

                <div style={{ display: "flex", flexDirection: "column" }}>
                  {result.insights?.length > 0 ? (
                    result.insights.map((insight, idx) => (
                      <div
                        key={idx}
                        style={{
                          display: "flex",
                          gap: "14px",
                          alignItems: "flex-start",
                          paddingBottom: "12px",
                          borderBottom: idx < result.insights.length - 1 ? "1px solid #eeeeee" : "none",
                          marginBottom: idx < result.insights.length - 1 ? "12px" : "0"
                        }}
                      >
                        <span style={{
                          fontSize: "12px",
                          fontFamily: "JetBrains Mono",
                          fontWeight: "600",
                          color: "#5c9e2e",
                          width: "28px",
                          flexShrink: 0,
                          marginTop: "2px"
                        }}>
                          0{idx + 1}
                        </span>
                        <p style={{
                          fontSize: "14px",
                          fontFamily: "DM Sans",
                          color: "#1f2937",
                          margin: 0,
                          lineHeight: 1.75,
                          fontWeight: 400
                        }}>
                          {insight}
                        </p>
                      </div>
                    ))
                  ) : (
                    <span style={{ fontSize: "12px", fontFamily: "DM Sans", fontStyle: "italic", color: "var(--text-dim)" }}>
                      No ML analysis insights generated.
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* SECTION 8 — ADOPTION RECOMMENDATION */}
            <div className="pdf-section" style={{ pageBreakInside: "avoid", marginBottom: "28px" }}>
              <SectionDivider label="08 WHAT TO DO WITH THIS" />

              <div style={{
                padding: "22px 28px",
                border: "1px solid var(--border)",
                background: "var(--bg-hover)",
                backgroundColor: "var(--bg-hover)",
                borderRadius: "8px",
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
              }}>
                {/* Block 1: FOR COUNTRIES BUILDING FRAMEWORKS */}
                <div>
                  <h5 style={{
                    fontSize: "12px",
                    fontFamily: "JetBrains Mono",
                    color: "var(--text-muted)",
                    letterSpacing: "0.1em",
                    margin: "0 0 10px 0",
                    fontWeight: "600"
                  }}>
                    FOR COUNTRIES BUILDING FRAMEWORKS
                  </h5>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    {result.ml_metrics?.same_sector && (result.overall_metrics?.composite_score || 0) > 0.6 ? (
                      <>
                        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                          <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                          <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                            Both policies offer viable templates — choose based on your enforcement capacity
                          </span>
                        </div>
                        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                          <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                          <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                            Adopt shared provisions as your baseline ({result.shared_tags?.length || 0} areas of consensus)
                          </span>
                        </div>
                        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                          <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                          <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                            Select unique provisions from whichever jurisdiction matches your development stage
                          </span>
                        </div>
                      </>
                    ) : (
                      <>
                        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                          <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                          <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                            These policies address {result.policy_1?.sector || "Policy A sector"} and {result.policy_2?.sector || "Policy B sector"} separately — implement both frameworks for complete coverage
                          </span>
                        </div>
                        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                          <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                          <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                            Start with {(() => {
                              const y1 = result.policy_1?.year || 0;
                              const y2 = result.policy_2?.year || 0;
                              return y1 >= y2 ? (result.policy_1?.title || "Policy A") : (result.policy_2?.title || "Policy B");
                            })()} as your primary reference (more recent)
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Divider */}
                <div style={{ height: "1px", background: "#d8d8d8", backgroundColor: "#d8d8d8", margin: "14px 0" }} />

                {/* Block 2: FOR COMPLIANCE PROFESSIONALS */}
                <div>
                  <h5 style={{
                    fontSize: "12px",
                    fontFamily: "JetBrains Mono",
                    color: "var(--text-muted)",
                    letterSpacing: "0.1em",
                    margin: "0 0 10px 0",
                    fontWeight: "600"
                  }}>
                    FOR COMPLIANCE PROFESSIONALS
                  </h5>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                      <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                      <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                        Map shared themes to establish a unified compliance matrix for rapid audit scoping
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                      <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                      <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                        Conduct a targeted gap analysis against unique provisions before expanding services
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                      <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                      <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                        Update incident response procedures to satisfy overlapping regulatory constraints
                      </span>
                    </div>
                  </div>
                </div>

                {/* Divider */}
                <div style={{ height: "1px", background: "#d8d8d8", backgroundColor: "#d8d8d8", margin: "14px 0" }} />

                {/* Block 3: FOR POLICY RESEARCHERS */}
                <div>
                  <h5 style={{
                    fontSize: "12px",
                    fontFamily: "JetBrains Mono",
                    color: "var(--text-muted)",
                    letterSpacing: "0.1em",
                    margin: "0 0 10px 0",
                    fontWeight: "600"
                  }}>
                    FOR POLICY RESEARCHERS
                  </h5>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                      <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                      <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                        Examine divergence in unique provisions to trace jurisdictional priorities and scope constraints
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                      <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                      <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                        Track how cross-border differences impact compliance overhead for global tech platforms
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                      <span style={{ color: "#5c9e2e", fontFamily: "DM Sans", fontSize: "14px", fontWeight: 700, flexShrink: 0, marginTop: "1px" }}>→</span>
                      <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", lineHeight: 1.65 }}>
                        Evaluate the efficiency of these models to inform future global harmonizing standard reviews
                      </span>
                    </div>
                  </div>
                </div>

              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}