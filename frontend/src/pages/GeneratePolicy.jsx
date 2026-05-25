import { useState, useEffect } from "react";
import LoadingSpinner from "../components/LoadingSpinner";
import { Sparkles, FileDown, RotateCcw, AlertTriangle } from "lucide-react";

const FALLBACK_COUNTRIES = [
  "India", "United States", "European Union", "Brazil", "China", 
  "United Kingdom", "Singapore", "Australia", "Canada", "Japan", 
  "South Korea", "Germany", "France"
];

const FALLBACK_SECTORS = [
  "AI Governance", "Cybersecurity", "Data Privacy",
  "Healthcare AI", "Financial Regulation",
  "POSH Policies", "ESG Policies", "IoT and Robotics"
];

const LOADING_MESSAGES = [
  "Analyzing regulatory landscape...",
  "Querying reference policies...",
  "Identifying framework gaps...",
  "Drafting policy sections...",
  "Structuring document...",
  "Finalizing framework..."
];

export default function GeneratePolicy() {
  const [country, setCountry] = useState("");
  const [sector, setSector] = useState("");
  const [focusAreas, setFocusAreas] = useState("");
  const [countries, setCountries] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [contextPreview, setContextPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);


  // 1. Fetch available countries and sectors on mount
  useEffect(() => {
    async function loadMeta() {
      try {
        const [cRes, sRes] = await Promise.all([
          fetch("http://localhost:8000/api/generate/countries"),
          fetch("http://localhost:8000/api/generate/sectors")
        ]);
        if (cRes.ok) {
          const cData = await cRes.json();
          setCountries(cData);
        } else {
          setCountries(FALLBACK_COUNTRIES);
        }
        if (sRes.ok) {
          const sData = await sRes.json();
          setSectors(sData);
        } else {
          setSectors(FALLBACK_SECTORS);
        }
      } catch (err) {
        console.error("Failed to load backend metadata, using local presets.", err);
        setCountries(FALLBACK_COUNTRIES);
        setSectors(FALLBACK_SECTORS);
      }
    }
    loadMeta();
  }, []);

  // 2. Fetch context preview whenever country or sector changes
  useEffect(() => {
    if (!country || !sector) {
      setContextPreview(null);
      return;
    }

    async function loadPreview() {
      setPreviewLoading(true);
      try {
        const res = await fetch(
          `http://localhost:8000/api/generate/context-preview?country=${encodeURIComponent(country)}&sector=${encodeURIComponent(sector)}`
        );
        if (res.ok) {
          const data = await res.json();
          setContextPreview(data);
        } else {
          setContextPreview(null);
        }
      } catch (err) {
        console.error("Failed to fetch intelligence context preview.", err);
        setContextPreview(null);
      } finally {
        setPreviewLoading(false);
      }
    }

    loadPreview();
  }, [country, sector]);

  // 3. Cycle generating messages
  useEffect(() => {
    let interval;
    if (generating) {
      interval = setInterval(() => {
        setLoadingStep((s) => (s < LOADING_MESSAGES.length - 1 ? s + 1 : s));
      }, 2500);
    } else {
      setLoadingStep(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [generating]);

  const handleGenerate = async () => {
    if (!country || !sector) return;
    setGenerating(true);
    setResult(null);
    setError(null);

    const parsedFocus = focusAreas
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      const res = await fetch("http://localhost:8000/api/generate/policy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          country,
          sector,
          policy_scope: "national",
          focus_areas: parsedFocus
        })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Verification failed during LLM generation.");
      }
      setResult(data);
    } catch (err) {
      setError(err.message || "An unexpected network or pipeline error occurred.");
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    window.open(`http://localhost:8000/api/generate/download/${result.policy_id}`, "_blank");
  };

  const resetGenerator = () => {
    setResult(null);
    setCountry("");
    setSector("");
    setFocusAreas("");
    setContextPreview(null);
    setError(null);
  };

  return (
    <div style={{
      maxWidth: "900px",
      margin: "0 auto",
      padding: "32px 40px",
      fontFamily: "'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif",
      color: "#0a0a0a"
    }}>
      {/* Page Header */}
      <div style={{ marginBottom: "28px" }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          fontSize: "11px",
          fontFamily: "'JetBrains Mono', monospace",
          color: "var(--text-dim)",
          textTransform: "uppercase",
          letterSpacing: "1.5px",
          marginBottom: "14px"
        }}>
          <span style={{
            width: "6px",
            height: "6px",
            background: "#5c9e2e",
            display: "inline-block",
            borderRadius: "1px"
          }} /> Discover / Creation
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
          Draft new <span className="half-highlight-custom">policies.</span>
        </h1>
        <p style={{
          fontFamily: "'DM Sans', sans-serif",
          color: "var(--text-muted)",
          fontSize: "16px",
          margin: 0,
          maxWidth: "600px",
          lineHeight: 1.5
        }}>
          Generate a professionally structured policy framework template tailored to a country's regulatory context and identified gaps.
        </p>
      </div>

      {/* ERROR CARD */}
      {error && (
        <div style={{
          background: "#fef2f2",
          border: "1px solid #fca5a5",
          borderRadius: "8px",
          padding: "20px",
          marginBottom: "24px",
          display: "flex",
          flexDirection: "column",
          gap: "12px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#b91c1c" }}>
            <AlertTriangle size={18} />
            <span style={{ fontWeight: 600, fontSize: "15px" }}>Generation Pipeline Issue</span>
          </div>
          <p style={{ fontSize: "14.5px", color: "#7f1d1d", lineHeight: "1.5" }}>
            {error}
          </p>
          <button
            onClick={handleGenerate}
            style={{
              alignSelf: "flex-start",
              background: "#b91c1c",
              color: "#ffffff",
              border: "none",
              borderRadius: "6px",
              padding: "8px 16px",
              fontSize: "13.5px",
              fontWeight: 600,
              cursor: "pointer",
              transition: "background 0.2s"
            }}
            onMouseEnter={(e) => e.target.style.background = "#991b1b"}
            onMouseLeave={(e) => e.target.style.background = "#b91c1c"}
          >
            Retry Generation
          </button>
        </div>
      )}

      {/* VIEW PIPELINE: CONFIG OR LOADING OR RESULT */}
      {!generating && !result && (
        <>
          {/* STEP 1 - Configuration Card */}
          <div style={{
            background: "#ffffff",
            border: "1px solid #e8e8e8",
            borderRadius: "8px",
            padding: "24px 28px",
            marginBottom: "20px"
          }}>
            {/* Section label */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginBottom: "20px"
            }}>
              <span style={{ fontSize: "11.5px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "1.2px" }}>01 CONFIGURE</span>
              <div style={{ flex: 1, height: "1px", background: "#f0f0f0" }} />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              {/* Dropdowns Row */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                {/* Country Selection */}
                <div>
                  <label style={{
                    display: "block",
                    fontSize: "11px",
                    fontFamily: "'JetBrains Mono', monospace",
                    color: "#9ca3af",
                    letterSpacing: "0.08em",
                    marginBottom: "6px"
                  }}>SELECT COUNTRY</label>
                  <select
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    style={{
                      width: "100%",
                      height: "44px",
                      border: "1px solid #e8e8e8",
                      borderRadius: "6px",
                      padding: "0 12px",
                      fontSize: "15px",
                      fontFamily: "'DM Sans', sans-serif",
                      color: "#0a0a0a",
                      background: "#ffffff",
                      cursor: "pointer",
                      outline: "none",
                      transition: "border-color 0.15s, box-shadow 0.15s"
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = "#5c9e2e";
                      e.target.style.boxShadow = "0 0 0 3px rgba(92,158,46,0.08)";
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = "#e8e8e8";
                      e.target.style.boxShadow = "none";
                    }}
                  >
                    <option value="">Select jurisdiction...</option>
                    {countries.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* Sector Selection */}
                <div>
                  <label style={{
                    display: "block",
                    fontSize: "11px",
                    fontFamily: "'JetBrains Mono', monospace",
                    color: "#9ca3af",
                    letterSpacing: "0.08em",
                    marginBottom: "6px"
                  }}>SELECT SECTOR</label>
                  <select
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    style={{
                      width: "100%",
                      height: "44px",
                      border: "1px solid #e8e8e8",
                      borderRadius: "6px",
                      padding: "0 12px",
                      fontSize: "15px",
                      fontFamily: "'DM Sans', sans-serif",
                      color: "#0a0a0a",
                      background: "#ffffff",
                      cursor: "pointer",
                      outline: "none",
                      transition: "border-color 0.15s, box-shadow 0.15s"
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = "#5c9e2e";
                      e.target.style.boxShadow = "0 0 0 3px rgba(92,158,46,0.08)";
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = "#e8e8e8";
                      e.target.style.boxShadow = "none";
                    }}
                  >
                    <option value="">Select industry domain...</option>
                    {sectors.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Focus Areas Input */}
              <div>
                <label style={{
                  display: "block",
                  fontSize: "11px",
                  fontFamily: "'JetBrains Mono', monospace",
                  color: "#9ca3af",
                  letterSpacing: "0.08em",
                  marginBottom: "6px"
                }}>FOCUS AREAS (OPTIONAL)</label>
                <input
                  type="text"
                  placeholder="e.g. incident response, data localization, algorithmic auditing"
                  value={focusAreas}
                  onChange={(e) => setFocusAreas(e.target.value)}
                  style={{
                    width: "100%",
                    height: "44px",
                    border: "1px solid #e8e8e8",
                    borderRadius: "6px",
                    padding: "0 12px",
                    fontSize: "15px",
                    fontFamily: "'DM Sans', sans-serif",
                    color: "#0a0a0a",
                    background: "#ffffff",
                    outline: "none",
                    boxSizing: "border-box",
                    transition: "border-color 0.15s, box-shadow 0.15s"
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = "#5c9e2e";
                    e.target.style.boxShadow = "0 0 0 3px rgba(92,158,46,0.08)";
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = "#e8e8e8";
                    e.target.style.boxShadow = "none";
                  }}
                />
                <span style={{ display: "block", fontSize: "13px", color: "#9ca3af", marginTop: "6px" }}>
                  Provide comma-separated keywords. Leave blank to auto-detect optimal coverage parameters.
                </span>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={!country || !sector}
                style={{
                  marginTop: "8px",
                  width: "100%",
                  height: "48px",
                  background: (!country || !sector) ? "#e8e8e8" : "#0a0a0a",
                  color: (!country || !sector) ? "#9ca3af" : "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  fontSize: "15px",
                  fontFamily: "'DM Sans', sans-serif",
                  fontWeight: 600,
                  cursor: (!country || !sector) ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  transition: "opacity 0.2s, background 0.2s"
                }}
                onMouseEnter={(e) => {
                  if (country && sector) e.target.style.background = "#222222";
                }}
                onMouseLeave={(e) => {
                  if (country && sector) e.target.style.background = "#0a0a0a";
                }}
              >
                <Sparkles size={14} /> Generate Policy Framework
              </button>
            </div>
          </div>

          {/* STEP 2 - Context Preview Card */}
          {previewLoading && (
            <div style={{
              background: "#fafafa",
              border: "1px solid #e8e8e8",
              borderRadius: "8px",
              padding: "20px 24px",
              textAlign: "center"
            }}>
              <LoadingSpinner label="Compiling intelligence context..." />
            </div>
          )}

          {!previewLoading && contextPreview && (
            <div style={{
              background: "#fafafa",
              border: "1px solid #e8e8e8",
              borderRadius: "8px",
              padding: "20px 24px",
              animation: "fadeIn 0.3s ease-out"
            }}>
              {/* Header */}
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "16px"
              }}>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  fontSize: "11px",
                  fontFamily: "'JetBrains Mono', monospace",
                  color: "#9ca3af",
                  textTransform: "uppercase",
                  letterSpacing: "0.08em"
                }}>
                  <span style={{ color: "#5c9e2e", fontSize: "14px" }}>●</span> Intelligence Context
                </div>
                <span style={{ fontSize: "12px", fontFamily: "'JetBrains Mono', monospace", color: "#6b7280", background: "#ffffff", padding: "3px 8px", borderRadius: "4px", border: "1px solid #e8e8e8" }}>
                  Live Data Sync
                </span>
              </div>

              {/* Grid Columns */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "28px" }}>
                {/* Left Col - Country profile */}
                <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                  <div>
                    <span style={{ display: "block", fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.05em", marginBottom: "4px" }}>
                      REGULATORY MATURITY
                    </span>
                    <span style={{
                      fontSize: "13.5px",
                      fontFamily: "'JetBrains Mono', monospace",
                      fontWeight: 600,
                      color: "#0a0a0a",
                      textTransform: "uppercase",
                      background: "#ffffff",
                      border: "1px solid #e8e8e8",
                      borderRadius: "4px",
                      padding: "2px 8px"
                    }}>
                      {contextPreview.maturity}
                    </span>
                  </div>

                  <div>
                    <span style={{ display: "block", fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.05em", marginBottom: "6px" }}>
                      EXISTING COVERED SECTORS
                    </span>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                      {contextPreview.existing_sectors && contextPreview.existing_sectors.length > 0 ? (
                        contextPreview.existing_sectors.map((s) => (
                          <span key={s} style={{
                            fontSize: "13px",
                            color: "#374151",
                            background: "#ffffff",
                            border: "1px solid #e8e8e8",
                            borderRadius: "4px",
                            padding: "2px 6px"
                          }}>{s}</span>
                        ))
                      ) : (
                        <span style={{ fontSize: "13px", color: "#6b7280", fontStyle: "italic" }}>None listed</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <span style={{ display: "block", fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.05em", marginBottom: "4px" }}>
                      PRIORITY NEEDS
                    </span>
                    <span style={{ fontSize: "14px", color: "#374151", lineHeight: "1.5" }}>
                      {contextPreview.priority_needs ? contextPreview.priority_needs.join(", ") : "Cybersecurity controls and regional framework guidelines."}
                    </span>
                  </div>
                </div>

                {/* Right Col - DB findings */}
                <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                  <div>
                    <span style={{ display: "block", fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.05em", marginBottom: "4px" }}>
                      EXISTING {sector.toUpperCase()} POLICIES
                    </span>
                    <span style={{ fontSize: "14px", color: "#374151", fontWeight: 500 }}>
                      {contextPreview.existing_count > 0 ? (
                        <span style={{ color: "#5c9e2e" }}>✓ {contextPreview.existing_count} policies found in database</span>
                      ) : (
                        <span style={{ color: "#6b7280" }}>No existing policies — drafting framework from scratch</span>
                      )}
                    </span>
                  </div>

                  <div>
                    <span style={{ display: "block", fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.05em", marginBottom: "4px" }}>
                      SEMANTIC REFERENCES
                    </span>
                    <span style={{ fontSize: "14px", color: "#374151" }}>
                      Top 5 matching frameworks from other jurisdictions will serve as drafting blueprints.
                    </span>
                  </div>

                  <div>
                    <span style={{ display: "block", fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.05em", marginBottom: "6px" }}>
                      IDENTIFIED GAPS TO RESOLVE
                    </span>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                      {contextPreview.gaps && contextPreview.gaps.length > 0 ? (
                        contextPreview.gaps.slice(0, 4).map((gap) => (
                          <span
                            key={gap}
                            style={{
                              fontSize: "13px",
                              color: "#856404",
                              background: "#fff3cd",
                              border: "1px solid #ffeaa7",
                              borderRadius: "4px",
                              padding: "2px 8px"
                            }}
                          >
                            {gap}
                          </span>
                        ))
                      ) : (
                        <span style={{ fontSize: "13px", color: "#6b7280", fontStyle: "italic" }}>No outstanding gaps detected</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* STEP 3 - Generation Loading State */}
      {generating && (
        <div style={{
          background: "#ffffff",
          border: "1px solid #e8e8e8",
          borderRadius: "8px",
          padding: "48px 40px",
          textAlign: "center",
          animation: "fadeIn 0.3s ease-out"
        }}>
          <LoadingSpinner label="" />
          <h2 style={{
            fontSize: "18px",
            fontWeight: 600,
            marginTop: "20px",
            marginBottom: "8px",
            color: "#0a0a0a"
          }}>
            {LOADING_MESSAGES[loadingStep]}
          </h2>
          <p style={{
            fontSize: "12.5px",
            fontFamily: "'JetBrains Mono', monospace",
            color: "#9ca3af",
            textTransform: "uppercase",
            letterSpacing: "0.08em"
          }}>
            Drafting framework · Please wait 15-30s
          </p>
        </div>
      )}

      {/* STEP 4 - Generated Document Display */}
      {result && !generating && (
        <div style={{ animation: "fadeIn 0.4s ease-out" }}>
          {/* Document Header Bar */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px"
          }}>
            <div>
              <span style={{
                display: "block",
                fontSize: "10px",
                fontFamily: "'JetBrains Mono', monospace",
                color: "#9ca3af",
                letterSpacing: "0.08em",
                textTransform: "uppercase"
              }}>
                Generated Framework
              </span>
              <h2 style={{
                fontSize: "22px",
                fontWeight: 700,
                color: "#0a0a0a",
                marginTop: "4px",
                fontFamily: "'DM Sans', sans-serif"
              }}>
                {result.document.title}
              </h2>
            </div>

            <div style={{ display: "flex", gap: "10px", alignItems: "center", flexShrink: 0 }}>
              <button
                onClick={resetGenerator}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  background: "#ffffff",
                  border: "1px solid #e8e8e8",
                  borderRadius: "6px",
                  padding: "8px 14px",
                  fontSize: "12px",
                  fontWeight: 500,
                  color: "#374151",
                  cursor: "pointer",
                  transition: "background 0.2s"
                }}
                onMouseEnter={(e) => e.target.style.background = "#fafafa"}
                onMouseLeave={(e) => e.target.style.background = "#ffffff"}
              >
                <RotateCcw size={13} /> Generate New
              </button>

              <button
                onClick={handleDownload}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  background: "#0a0a0a",
                  color: "#ffffff",
                  border: "1px solid transparent",
                  borderRadius: "6px",
                  padding: "8px 16px",
                  fontSize: "12px",
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "background 0.2s"
                }}
                onMouseEnter={(e) => e.target.style.background = "#222222"}
                onMouseLeave={(e) => e.target.style.background = "#0a0a0a"}
              >
                <FileDown size={14} /> Download PDF
              </button>
            </div>
          </div>

          {/* Context Used Strip */}
          <div style={{
            background: "#fafafa",
            border: "1px solid #e8e8e8",
            borderRadius: "6px",
            padding: "10px 16px",
            marginBottom: "24px",
            fontSize: "11px",
            color: "#6b7280",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}>
            <span style={{ color: "#5c9e2e", fontSize: "14px", lineHeight: "1" }}>●</span>
            <span>
              Generated using {result.context_used.reference_policies.length} reference policies · {result.context_used.gaps_identified.length} gaps addressed · Tailored to {result.country} profile
            </span>
          </div>

          {/* Table of contents and preamble brief */}
          <div style={{
            background: "#ffffff",
            border: "1px solid #e8e8e8",
            borderRadius: "8px",
            padding: "24px 28px",
            marginBottom: "24px"
          }}>
            <span style={{ display: "block", fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.08em", marginBottom: "12px" }}>
              EXECUTIVE BRIEF & PREAMBLE
            </span>
            <p style={{
              fontSize: "15px",
              color: "#374151",
              lineHeight: "1.8",
              textAlign: "justify",
              marginBottom: "16px"
            }}>
              <b>Executive Summary:</b> {result.document.executive_summary}
            </p>
            <div style={{ height: "1px", background: "#f0f0f0", marginBottom: "16px" }} />
            <p style={{
              fontSize: "14.5px",
              color: "#6b7280",
              lineHeight: "1.8",
              textAlign: "justify",
              fontStyle: "italic"
            }}>
              <b>Legislative Preamble:</b> {result.document.preamble}
            </p>
          </div>

          {/* Document Sections */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {result.document.sections.map((section, idx) => (
              <div key={section.number} style={{ marginBottom: "8px" }}>
                {/* Section Header Wrapper */}
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  marginBottom: "10px"
                }}>
                  <span style={{
                    fontSize: "11px",
                    fontFamily: "'JetBrains Mono', monospace",
                    color: "#5c9e2e",
                    fontWeight: 600,
                    width: "28px"
                  }}>
                    {section.number.padStart(2, "0")}
                  </span>
                  <div style={{ width: "20px", height: "1px", background: "#e8e8e8" }} />
                  <span style={{
                    fontSize: "15px",
                    fontWeight: 600,
                    color: "#0a0a0a",
                    fontFamily: "'DM Sans', sans-serif"
                  }}>
                    {section.title}
                  </span>
                  <div style={{ flex: 1, height: "1px", background: "#e8e8e8" }} />
                </div>

                {/* Section Content card */}
                <div style={{
                  background: "#ffffff",
                  border: "1px solid #e8e8e8",
                  borderRadius: "8px",
                  padding: "24px 28px"
                }}>
                  <p style={{
                    fontSize: "15px",
                    color: "#374151",
                    lineHeight: "1.8",
                    textAlign: "justify",
                    margin: 0
                  }}>
                    {section.content}
                  </p>

                  {/* Subsections if they exist */}
                  {section.subsections && section.subsections.length > 0 && (
                    <div style={{
                      marginTop: "18px",
                      display: "flex",
                      flexDirection: "column",
                      gap: "14px",
                      borderTop: "1px solid #f3f4f6",
                      paddingTop: "18px"
                    }}>
                      {section.subsections.map((sub) => (
                        <div key={sub.number}>
                          <h4 style={{
                            fontSize: "14px",
                            fontWeight: 600,
                            color: "#0a0a0a",
                            marginTop: 0,
                            marginBottom: "6px",
                            borderLeft: "3px solid #5c9e2e",
                            paddingLeft: "10px"
                          }}>
                            {sub.number} {sub.title}
                          </h4>
                          <p style={{
                            fontSize: "14.2px",
                            color: "#4b5563",
                            lineHeight: "1.75",
                            textAlign: "justify",
                            margin: 0,
                            paddingLeft: "13px"
                          }}>
                            {sub.content}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* IMPLEMENTATION ROADMAP TIMELINE */}
          {result.document.implementation_timeline && result.document.implementation_timeline.length > 0 && (
            <div style={{ marginTop: "32px", marginBottom: "28px" }}>
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                marginBottom: "16px"
              }}>
                <span style={{ fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.08em" }}>IMPLEMENTATION TIMELINE</span>
                <div style={{ flex: 1, height: "1px", background: "#f0f0f0" }} />
              </div>

              <div style={{
                display: "grid",
                gridTemplateColumns: `repeat(${result.document.implementation_timeline.length}, 1fr)`,
                gap: "16px"
              }}>
                {result.document.implementation_timeline.map((phase, i) => (
                  <div
                    key={phase.phase}
                    style={{
                      background: "#ffffff",
                      border: "1px solid #e8e8e8",
                      borderRadius: "8px",
                      padding: "18px 22px"
                    }}
                  >
                    <div style={{
                      fontSize: "12px",
                      fontFamily: "'JetBrains Mono', monospace",
                      fontWeight: 600,
                      color: "#0a0a0a",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "4px"
                    }}>
                      <span>{phase.phase.toUpperCase()}</span>
                      <span style={{ color: "#5c9e2e", fontWeight: 400 }}>{phase.duration}</span>
                    </div>
                    <div style={{ height: "1px", background: "#f0f0f0", margin: "8px 0" }} />
                    <ul style={{
                      margin: 0,
                      paddingLeft: "14px",
                      fontSize: "13.5px",
                      color: "#4b5563",
                      lineHeight: "1.75",
                      listStyleType: "square"
                    }}>
                      {phase.actions.map((act, j) => (
                        <li key={j} style={{ marginBottom: "6px" }}>{act}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* REFERENCES & BASIS SECTION */}
          {result.document.references && result.document.references.length > 0 && (
            <div style={{ marginTop: "32px", marginBottom: "20px" }}>
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                marginBottom: "16px"
              }}>
                <span style={{ fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#9ca3af", letterSpacing: "0.08em" }}>REFERENCES & BASIS</span>
                <div style={{ flex: 1, height: "1px", background: "#f0f0f0" }} />
              </div>

              <div style={{
                background: "#ffffff",
                border: "1px solid #e8e8e8",
                borderRadius: "8px",
                padding: "14px 22px"
              }}>
                {result.document.references.map((ref, i) => (
                  <div
                    key={ref.id}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "14px",
                      padding: "12px 0",
                      borderBottom: i < result.document.references.length - 1 ? "1px solid #f3f4f6" : "none"
                    }}
                  >
                    <span style={{
                      fontSize: "11px",
                      fontFamily: "'JetBrains Mono', monospace",
                      color: "#5c9e2e",
                      fontWeight: 600,
                      marginTop: "2px",
                      width: "28px"
                    }}>
                      [{ref.id}]
                    </span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: "13.5px", fontWeight: 500, color: "#0a0a0a" }}>
                        {ref.title}
                      </div>
                      <div style={{ fontSize: "11.5px", color: "#9ca3af", fontFamily: "'JetBrains Mono', monospace", marginTop: "2px" }}>
                        {ref.country} ({ref.year})
                      </div>
                      <div style={{ fontSize: "13px", color: "#6b7280", marginTop: "4px" }}>
                        {ref.relevance}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}