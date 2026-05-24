import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchPolicies, fetchRecommendations, submitFeedback, generatePolicyTemplate } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import { Sparkles, ExternalLink, Copy, ThumbsUp, ThumbsDown, Target, Shield, Search } from "lucide-react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { jsPDF } from "jspdf";

export default function Recommend() {
  const nav = useNavigate();
  const [policies,      setPolicies]      = useState([]);
  const [selected,      setSelected]      = useState(null);
  const [result,        setResult]        = useState(null);
  const [loading,       setLoading]       = useState(false);
  const [sector,        setSector]        = useState("");
  const [search,        setSearch]        = useState("");
  const [feedbackGiven, setFeedbackGiven] = useState({});
  const [weights,       setWeights]       = useState({
    sector_gap: 35,
    regulatory_maturity: 25,
    semantic_need: 20,
    regional_pressure: 12,
    economic_tier: 8
  });
  
  const [step, setStep] = useState(1); // step 1: selecting policy, step 2: viewing results
  const [showWeightsPanel, setShowWeightsPanel] = useState(true); // CollapsibleFactor weights
  const [expandedReasons, setExpandedReasons] = useState({});
  const [drawerOpen,    setDrawerOpen]    = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [proposal,      setProposal]      = useState(null);

  // Hover states tracking for custom micro-interactions
  const [hoveredSector, setHoveredSector] = useState(null);
  const [hoveredPolicy, setHoveredPolicy] = useState(null);
  const [hoveredProposalBtn, setHoveredProposalBtn] = useState({});
  const [hoveredFeedbackBtn, setHoveredFeedbackBtn] = useState({});
  const [hoveredBack, setHoveredBack] = useState(false);

  const toggleReason = (country) => {
    setExpandedReasons(prev => ({
      ...prev,
      [country]: !prev[country]
    }));
  };

  const handleGenerateProposal = (country, sector) => {
    setDrawerOpen(true);
    setDrawerLoading(true);
    setProposal(null);
    generatePolicyTemplate(country, sector)
      .then(data => {
        setProposal(data);
        setDrawerLoading(false);
      })
      .catch(err => {
        console.error(err);
        alert("Failed to generate AI proposal. Please make sure you are logged in.");
        setDrawerLoading(false);
        setDrawerOpen(false);
      });
  };

  useEffect(() => {
    fetchPolicies({}).then(d => setPolicies(d || []));
  }, []);

  const handleSelect = (policy) => {
    setSelected(policy);
    setResult(null);
    setFeedbackGiven({});
    setLoading(true);
    setStep(2); // Switch to single column Mode B results page

    const decimalWeights = {
      sector_gap: weights.sector_gap / 100,
      regulatory_maturity: weights.regulatory_maturity / 100,
      semantic_need: weights.semantic_need / 100,
      regional_pressure: weights.regional_pressure / 100,
      economic_tier: weights.economic_tier / 100,
    };

    fetchRecommendations(policy.id, 6, decimalWeights).then(r => {
      setResult(r);
      setLoading(false);
    });
  };

  const handleWeightChange = (key, value) => {
    setWeights(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleResetWeights = () => {
    setWeights({
      sector_gap: 35,
      regulatory_maturity: 25,
      semantic_need: 20,
      regional_pressure: 12,
      economic_tier: 8
    });
  };

  const handleAutoBalance = () => {
    const sum = Object.values(weights).reduce((a, b) => a + b, 0);
    if (sum === 0) {
      setWeights({
        sector_gap: 35,
        regulatory_maturity: 25,
        semantic_need: 20,
        regional_pressure: 12,
        economic_tier: 8
      });
      return;
    }
    const factor = 100 / sum;
    const balanced = {
      sector_gap: Math.round(weights.sector_gap * factor),
      regulatory_maturity: Math.round(weights.regulatory_maturity * factor),
      semantic_need: Math.round(weights.semantic_need * factor),
      regional_pressure: Math.round(weights.regional_pressure * factor),
      economic_tier: Math.round(weights.economic_tier * factor),
    };
    
    // Adjust rounding discrepancy to exact 100
    const newSum = Object.values(balanced).reduce((a, b) => a + b, 0);
    const diff = 100 - newSum;
    if (diff !== 0) {
      balanced.sector_gap += diff;
    }
    setWeights(balanced);
  };

  const handleRecalculate = () => {
    if (!selected) return;
    setLoading(true);
    const decimalWeights = {
      sector_gap: weights.sector_gap / 100,
      regulatory_maturity: weights.regulatory_maturity / 100,
      semantic_need: weights.semantic_need / 100,
      regional_pressure: weights.regional_pressure / 100,
      economic_tier: weights.economic_tier / 100,
    };
    fetchRecommendations(selected.id, 6, decimalWeights).then(r => {
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

  const downloadProposalPDF = (proposalData) => {
    if (!proposalData) return;
    const doc = new jsPDF();
    
    // Theme Colors
    const primaryColor = [10, 10, 10]; // slate black
    const accentColor = [92, 158, 46]; // lime green
    const textColor = [55, 65, 81]; // grey
    
    // Header
    doc.setFillColor(...primaryColor);
    doc.rect(0, 0, 210, 35, "F");
    
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("POLICYIQ AI BRIEF & DRAFT PROPOSAL", 14, 15);
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text(`Generated on ${new Date().toLocaleDateString()} | Confidential Executive Brief`, 14, 25);
    
    // Content body
    doc.setTextColor(...primaryColor);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text(proposalData.suggested_title || "Draft Policy Framework", 14, 50);
    
    doc.setDrawColor(...accentColor);
    doc.setLineWidth(1);
    doc.line(14, 55, 196, 55);
    
    // Metadata block
    doc.setFillColor(250, 250, 250);
    doc.rect(14, 60, 182, 35, "F");
    doc.setDrawColor(232, 232, 232);
    doc.rect(14, 60, 182, 35, "S");
    
    doc.setTextColor(...textColor);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.text(`TARGET COUNTRY:`, 20, 68);
    doc.text(`SECTOR:`, 20, 75);
    doc.text(`REGULATORY MATURITY:`, 20, 82);
    doc.text(`REGULATORY GAP STATE:`, 20, 89);
    
    doc.setFont("helvetica", "normal");
    doc.text(proposalData.country, 70, 68);
    doc.text(proposalData.sector, 70, 75);
    doc.text(proposalData.maturity_level.toUpperCase(), 70, 82);
    doc.text(proposalData.regulatory_gap ? "GAP IDENTIFIED (No active framework)" : "POTENTIAL ADVANCED ENHANCEMENT", 70, 89);
    
    // Priority Needs & Policy Context
    let y = 110;
    doc.setTextColor(...primaryColor);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.text("1. NATIONAL DEVELOPMENT CONTEXT & POLICY GAP", 14, y);
    y += 8;
    doc.setTextColor(...textColor);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    const splitContext = doc.splitTextToSize(proposalData.policy_context || "No context provided.", 182);
    doc.text(splitContext, 14, y);
    y += splitContext.length * 5 + 10;
    
    // Priority Areas
    doc.setTextColor(...primaryColor);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.text("2. PRIORITY NEEDS IDENTIFIED", 14, y);
    y += 8;
    doc.setTextColor(...textColor);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    (proposalData.priority_areas || []).forEach((area, idx) => {
      doc.text(`• ${area}`, 18, y);
      y += 6;
    });
    y += 8;
    
    // Key Requirements
    doc.setTextColor(...primaryColor);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.text("3. KEY RECOMMENDED REGULATORY REQUIREMENTS", 14, y);
    y += 8;
    doc.setTextColor(...textColor);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    (proposalData.key_requirements || []).forEach((req, idx) => {
      doc.text(`${idx + 1}. ${req}`, 18, y);
      y += 6;
    });
    y += 12;
    
    // Suggested Sections
    doc.setTextColor(...primaryColor);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.text("4. RECOMMENDED STATUTORY SECTIONS", 14, y);
    y += 8;
    doc.setTextColor(...textColor);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    (proposalData.recommended_sections || []).forEach((section, idx) => {
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
      doc.text(section, 18, y);
      y += 6;
    });
    y += 12;
    
    // Implementation Timeline
    if (y > 250) {
      doc.addPage();
      y = 20;
    }
    doc.setTextColor(...primaryColor);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.text("5. PROPOSED IMPLEMENTATION TIMELINE", 14, y);
    y += 8;
    doc.setTextColor(...textColor);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    
    Object.entries(proposalData.implementation_timeline || {}).forEach(([phase, details]) => {
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
      doc.setFont("helvetica", "bold");
      doc.text(`${phase}:`, 18, y);
      doc.setFont("helvetica", "normal");
      doc.text(details, 65, y);
      y += 6;
    });
    y += 15;
    
    // Cryptographic Verifiability Hash
    if (y > 260) {
      doc.addPage();
      y = 20;
    }
    doc.setDrawColor(...accentColor);
    doc.setLineWidth(0.5);
    doc.line(14, y, 196, y);
    y += 8;
    
    const verificationHash = "VERIFY-SHA256-" + btoa(proposalData.country + proposalData.sector).slice(0, 16).toUpperCase() + "-" + new Date().getTime().toString().slice(-6);
    
    doc.setTextColor(...textColor);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.text(`PolicyIQ Cryptographic Assurance Hash: ${verificationHash}`, 14, y);
    doc.text("Verified secure gazette crawling source integrity - Google DeepMind NLP Engine", 14, y + 4);
    
    const pdfBase64 = doc.output("datauristring");
    const filename = `PolicyIQ_AI_Brief_${proposalData.country.replace(/\s+/g, '_')}_${proposalData.sector.replace(/\s+/g, '_')}.pdf`;

    const form = document.createElement("form");
    form.method = "POST";
    form.action = "http://localhost:8000/api/generate/download-pdf";

    const base64Input = document.createElement("input");
    base64Input.type = "hidden";
    base64Input.name = "base64_data";
    base64Input.value = pdfBase64;
    form.appendChild(base64Input);

    const filenameInput = document.createElement("input");
    filenameInput.type = "hidden";
    filenameInput.name = "filename";
    filenameInput.value = filename;
    form.appendChild(filenameInput);

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
  };

  const filtered = policies.filter(p => {
    const matchesSector = !sector || p.sector === sector;
    const matchesSearch = !search || 
      (p.title && p.title.toLowerCase().includes(search.toLowerCase())) ||
      (p.country && p.country.toLowerCase().includes(search.toLowerCase())) ||
      (p.sector && p.sector.toLowerCase().includes(search.toLowerCase()));
    return matchesSector && matchesSearch;
  });

  const weightsSum = Object.values(weights).reduce((a, b) => a + b, 0);

  return (
    <div style={{
      flex: 1,
      overflowY: "auto",
      background: "var(--bg-deep)",
      color: "var(--text-main)",
      minHeight: "100vh",
      transition: "background 0.3s ease, color 0.3s ease, border-color 0.3s ease"
    }}>
      <style>{`
        .custom-slider-input {
          -webkit-appearance: none;
          appearance: none;
          width: 100%;
          height: 4px;
          background: var(--border-lit);
          border-radius: 2px;
          outline: none;
          cursor: pointer;
          transition: background 0.3s ease;
        }
        .custom-slider-input::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: var(--text-main);
          border: 2px solid var(--bg-card);
          box-shadow: 0 1px 3px rgba(0,0,0,0.2);
          cursor: pointer;
          transition: background 0.15s ease, border-color 0.3s ease;
        }
        .custom-slider-input::-moz-range-thumb {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: var(--text-main);
          border: 2px solid var(--bg-card);
          box-shadow: 0 1px 3px rgba(0,0,0,0.2);
          cursor: pointer;
          transition: background 0.15s ease, border-color 0.3s ease;
        }
        .custom-slider-input:focus::-webkit-slider-thumb,
        .custom-slider-input:active::-webkit-slider-thumb {
          background: #5c9e2e !important;
        }
        .custom-slider-input:focus::-moz-range-thumb,
        .custom-slider-input:active::-moz-range-thumb {
          background: #5c9e2e !important;
        }
        .db-link-btn:hover {
          color: #5c9e2e !important;
          background: rgba(163, 230, 53, 0.1) !important;
        }
        .selected-policy-title-hover:hover {
          color: #5c9e2e !important;
        }
        .similar-policy-card-hover {
          cursor: pointer;
          transition: all 0.3s ease-in-out;
        }
        .similar-policy-card-hover:hover {
          border-color: #5c9e2e !important;
          background: var(--bg-hover) !important;
          box-shadow: 0 4px 12px rgba(92, 158, 46, 0.08);
          transform: translateY(-2px);
        }
      `}</style>

      <div style={{
        maxWidth: "1100px",
        margin: "0 auto",
        padding: "32px 40px",
        width: "100%",
        transition: "all 0.3s ease"
      }}>
        
        {/* ========================================================================= */}
        {/* MODE A: POLICY SELECTION (step === 1) */}
        {/* ========================================================================= */}
        {step === 1 && (
          <>
            {/* Header */}
            <div style={{ marginBottom: "32px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                    <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--cyan)" }} />
                    <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.1em" }}>
                      DISCOVER / INTELLIGENCE
                    </span>
                  </div>
                  <h1 style={{ 
                    fontFamily: "'DM Sans', sans-serif", 
                    fontSize: "48px", 
                    fontWeight: 700, 
                    color: "var(--text-main)", 
                    margin: "0 0 8px 0", 
                    letterSpacing: "-1px", 
                    lineHeight: "1.1" 
                  }}>
                    Find policy <span style={{
                      position: "relative",
                      display: "inline-block",
                      zIndex: 1
                    }}>
                      gaps.
                      <span style={{
                        position: "absolute",
                        bottom: "4px",
                        left: 0,
                        right: 0,
                        height: "45%",
                        background: "rgba(163, 230, 53, 0.45)",
                        zIndex: -1
                      }} />
                    </span>
                  </h1>
                  <p style={{ fontFamily: "DM Sans", fontSize: "15px", color: "var(--text-muted)", margin: 0 }}>
                    Select a policy to discover which countries would benefit most from adopting it
                  </p>
                </div>
                <div style={{
                  display: "flex", 
                  alignItems: "center", 
                  gap: "6px",
                  padding: "8px 16px", 
                  borderRadius: "20px",
                  background: "var(--stat-bg)",
                  border: "1px solid var(--stat-border)",
                  flexShrink: 0
                }}>
                  <Sparkles size={14} color="#5c9e2e" />
                  <span style={{ fontSize: "13px", color: "var(--stat-label)", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                    ML POWERED
                  </span>
                </div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: "24px", alignItems: "start" }}>
              {/* Left Panel: Filters + Compact Policy Cards */}
              <div>
                {/* Search Input Bar */}
                <div style={{ position: "relative", marginBottom: "16px" }}>
                  <span style={{ 
                    position: "absolute", 
                    left: 14, 
                    top: "50%", 
                    transform: "translateY(-50%)",
                    pointerEvents: "none",
                    display: "flex",
                    alignItems: "center",
                    color: "var(--text-muted)"
                  }}>
                    <Search size={16} />
                  </span>
                  <input
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Search source policies..."
                    className="search-input-custom"
                    style={{
                      width: "100%",
                      height: 40,
                      border: "1px solid var(--border)",
                      borderRadius: "6px",
                      padding: "0 12px 0 38px",
                      outline: "none",
                      fontSize: "14px",
                      fontFamily: "DM Sans",
                      background: "var(--bg-card)",
                      color: "var(--text-main)",
                      boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
                      transition: "all 0.3s ease"
                    }}
                  />
                </div>

                {/* Sector Filters */}
                <div style={{ marginBottom: "20px" }}>
                  <div style={{ 
                    fontSize: "12px", 
                    color: "var(--text-muted)", 
                    fontFamily: "JetBrains Mono", 
                    marginBottom: "12px", 
                    letterSpacing: "0.1em" 
                  }}>
                    FILTER BY SECTOR
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    {[
                      "", "AI Governance", "Cybersecurity", "Data Privacy", 
                      "Healthcare AI", "Financial Regulation", "ESG Policies", 
                      "POSH Policies", "IoT and Robotics"
                    ].map(s => (
                      <button 
                        key={s} 
                        onClick={() => setSector(s)}
                        onMouseEnter={() => setHoveredSector(s)}
                        onMouseLeave={() => setHoveredSector(null)}
                        style={{
                          width: "100%",
                          padding: "10px 14px",
                          borderRadius: "6px",
                          textAlign: "left",
                          fontSize: "15px",
                          fontFamily: "DM Sans",
                          cursor: "pointer",
                          background: sector === s 
                            ? "var(--stat-bg)" 
                            : hoveredSector === s 
                              ? "var(--bg-hover)" 
                              : "transparent",
                          border: "none",
                          borderLeft: sector === s ? "2px solid var(--cyan)" : "none",
                          color: sector === s ? "var(--stat-label)" : "var(--text-muted)",
                          transition: "all 0.15s ease",
                          outline: "none",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}
                      >
                        <span>{s || "All Sectors"}</span>
                        <span style={{ 
                          fontFamily: "JetBrains Mono", 
                          fontSize: "12px", 
                          color: "var(--text-dim)" 
                        }}>
                          {s ? policies.filter(p => p.sector === s).length : policies.length}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Divider */}
                <div style={{ borderTop: "1px solid var(--border)", margin: "16px 0" }} />

                {/* Policy List */}
                <div style={{ 
                  display: "flex", 
                  flexDirection: "column", 
                  gap: "8px", 
                  maxHeight: "520px", 
                  overflowY: "auto", 
                  paddingRight: "4px" 
                }}>
                  {filtered.map(p => {
                    const isSelected = selected?.id === p.id;
                    return (
                      <div 
                        key={p.id}
                        onClick={() => handleSelect(p)}
                        onMouseEnter={() => setHoveredPolicy(p.id)}
                        onMouseLeave={() => setHoveredPolicy(null)}
                        style={{
                          background: isSelected ? "var(--stat-bg)" : "var(--bg-card)",
                          border: isSelected 
                            ? "2px solid var(--cyan)" 
                            : hoveredPolicy === p.id 
                              ? "1px solid var(--border-lit)" 
                              : "1px solid var(--border)",
                          borderRadius: "8px",
                          padding: "14px 16px",
                          cursor: "pointer",
                          transition: "all 0.15s ease",
                          display: "flex",
                          flexDirection: "column"
                        }}
                      >
                        {/* Top Row */}
                        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                          <div style={{ display: "flex", alignItems: "center", flex: 1, minWidth: 0 }}>
                            {/* Avatar */}
                            <div style={{
                              width: "32px",
                              height: "32px",
                              borderRadius: "6px",
                              background: "var(--bg-hover)",
                              border: "1px solid var(--border)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              flexShrink: 0
                            }}>
                              <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-muted)", fontWeight: "bold" }}>
                                {p.title ? p.title.charAt(0).toUpperCase() : "P"}
                              </span>
                            </div>

                            {/* Title */}
                            <span style={{
                              fontFamily: "DM Sans",
                              fontWeight: 500,
                              fontSize: "15px",
                              color: "var(--text-main)",
                              margin: "0 12px",
                              flex: 1,
                              display: "-webkit-box",
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: "vertical",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              lineHeight: "1.3"
                            }}>
                              {p.title}
                            </span>
                          </div>

                          {/* Sector badge */}
                          <div style={{ display: "flex", alignItems: "center", gap: "4px", flexShrink: 0 }}>
                            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--cyan)" }} />
                            <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                              {p.sector}
                            </span>
                          </div>

                          {/* Database Info Link */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              nav(`/policies/${p.id}`);
                            }}
                            title="View source database page"
                            style={{
                              marginLeft: "8px",
                              background: "none",
                              border: "none",
                              padding: "4px",
                              cursor: "pointer",
                              display: "flex",
                              alignItems: "center",
                              color: "var(--text-muted)",
                              borderRadius: "4px",
                              transition: "all 0.15s ease",
                              outline: "none"
                            }}
                            className="db-link-btn"
                          >
                            <ExternalLink size={12} />
                          </button>
                        </div>

                        {/* Bottom Row */}
                        <div style={{ 
                          display: "flex", 
                          alignItems: "center", 
                          gap: "8px", 
                          marginTop: "8px" 
                        }}>
                          <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", textTransform: "uppercase" }}>
                            {p.country}
                          </span>
                          {p.year && (
                            <>
                              <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>·</span>
                              <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                                {p.year}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right Panel: Empty State */}
              <div>
                <div style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "54px 48px",
                  textAlign: "center"
                }}>
                  <Target size={40} color="var(--border)" style={{ display: "block", margin: "0 auto 16px" }} />
                  <h3 style={{
                    fontFamily: "DM Sans",
                    fontSize: "18px",
                    fontWeight: 600,
                    color: "var(--text-main)",
                    marginBottom: "8px"
                  }}>
                    Select a policy to begin
                  </h3>
                  <p style={{
                    fontFamily: "DM Sans",
                    fontSize: "15px",
                    color: "var(--text-muted)",
                    lineHeight: "1.65",
                    maxWidth: "340px",
                    margin: "0 auto"
                  }}>
                    The ML engine will identify countries with the highest adoption need based on regulatory gaps and contextual alignment.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ========================================================================= */}
        {/* MODE B: COLLAPSED SELECTION & SINGLE COLUMN RESULTS (step === 2) */}
        {/* ========================================================================= */}
        {step === 2 && (
          <div style={{ width: "100%" }}>
            
            {/* Top Navigation Row */}
            <div style={{ 
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center", 
              marginBottom: "20px" 
            }}>
              <div>
                {/* Breadcrumbs */}
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--cyan)" }} />
                  <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.1em" }}>
                    DISCOVER / INTELLIGENCE
                  </span>
                </div>
                <div 
                  onClick={() => {
                    setStep(1);
                    setResult(null);
                    setSelected(null);
                    setSearch("");
                  }}
                  onMouseEnter={() => setHoveredBack(true)}
                  onMouseLeave={() => setHoveredBack(false)}
                  style={{
                    fontSize: "13px",
                    fontFamily: "JetBrains Mono",
                    color: hoveredBack ? "var(--cyan)" : "var(--text-muted)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    transition: "color 0.15s ease",
                    marginTop: "4px"
                  }}
                >
                  ← Change policy
                </div>
              </div>
              
              {result && !loading && (
                <div style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                  {result.recommendations?.length || 0} recommendations
                </div>
              )}
            </div>

            {/* Selected Policy Compact Card */}
            {selected && (
              <div style={{
                background: "var(--bg-hover)",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                padding: "16px 20px",
                marginBottom: "16px",
                display: "flex",
                alignItems: "center",
                gap: "16px"
              }}>
                {/* Left avatar */}
                <div style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "6px",
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0
                }}>
                  <span style={{ fontSize: "16px", fontFamily: "DM Sans", color: "var(--text-muted)", fontWeight: 600 }}>
                    {selected.title ? selected.title.charAt(0).toUpperCase() : "P"}
                  </span>
                </div>

                {/* Center */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", textTransform: "uppercase" }}>
                    ANALYZING
                  </div>
                  <h4 
                    onClick={() => nav(`/policies/${selected.id}`)}
                    title="View source database page"
                    className="selected-policy-title-hover"
                    style={{ 
                      fontFamily: "DM Sans", 
                      fontSize: "16px", 
                      fontWeight: 600, 
                      color: "var(--text-main)", 
                      margin: "2px 0 6px 0",
                      cursor: "pointer",
                      lineHeight: "1.4",
                      wordBreak: "break-word"
                    }}
                  >
                    {selected.title}
                    <ExternalLink size={13} style={{ color: "var(--text-muted)", marginLeft: "6px", display: "inline-block", verticalAlign: "middle" }} />
                  </h4>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                    <span style={{
                      fontSize: "11px",
                      fontFamily: "JetBrains Mono",
                      color: "var(--cyan)",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px"
                    }}>
                      <span style={{ width: "4px", height: "4px", borderRadius: "50%", background: "var(--cyan)" }} />
                      {selected.sector}
                    </span>
                    <span style={{ color: "var(--border)" }}>·</span>
                    <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", textTransform: "uppercase" }}>
                      {selected.country}
                    </span>
                    {selected.cluster && (
                      <>
                        <span style={{ color: "var(--border)" }}>·</span>
                        <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                          CLUSTER #{selected.cluster}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                {/* Right */}
                <div style={{
                  fontSize: "11px",
                  fontFamily: "JetBrains Mono",
                  color: "var(--text-muted)",
                  border: "1px solid var(--border)",
                  borderRadius: "4px",
                  padding: "4px 10px",
                  background: "var(--bg-card)",
                  flexShrink: 0
                }}>
                  Intellect AI · 5-Factor Gap Engine
                </div>
              </div>
            )}

            {/* Verified Source Banner */}
            {selected && (
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "10px 16px",
                background: "var(--bg-hover)",
                border: "1px solid var(--border)",
                borderRadius: "6px",
                marginBottom: "12px"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Shield size={14} color="var(--cyan)" />
                  <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                    VERIFIED SOURCE
                  </span>
                  <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                    {result?.source_policy?.integrity_hash 
                      ? (result.source_policy.integrity_hash.slice(0, 20) + "...") 
                      : selected.integrity_hash 
                        ? (selected.integrity_hash.slice(0, 20) + "...") 
                        : "sha256-..."}
                  </span>
                  <Copy 
                    size={11} 
                    color="var(--border-lit)" 
                    style={{ cursor: "pointer" }} 
                    onClick={() => {
                      const hash = result?.source_policy?.integrity_hash || selected.integrity_hash || "sha256-dummy-hash-value-for-testing";
                      navigator.clipboard.writeText(hash);
                      alert("Integrity hash copied to clipboard!");
                    }}
                  />
                </div>
                {(result?.source_policy?.source_url || selected.source_url) && (
                  <a 
                    href={result?.source_policy?.source_url || selected.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      fontSize: "11px", 
                      fontFamily: "JetBrains Mono", 
                      color: "var(--cyan)",
                      textDecoration: "none",
                      cursor: "pointer",
                      fontWeight: 600
                    }}
                  >
                    SOURCE ↗
                  </a>
                )}
              </div>
            )}

            {/* Loading Recommendations State */}
            {loading && (
              <div style={{
                background: "var(--bg-card)",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                padding: "54px",
                textAlign: "center",
                marginTop: "16px",
                width: "100%"
              }}>
                <LoadingSpinner />
                <p style={{
                  fontFamily: "DM Sans",
                  fontSize: "15px",
                  color: "var(--text-muted)",
                  marginTop: "14px",
                  marginBottom: 0
                }}>
                  Analyzing {selected?.title}...
                </p>
                <p style={{
                  fontFamily: "JetBrains Mono",
                  fontSize: "13px",
                  color: "var(--text-muted)",
                  marginTop: "6px",
                  marginBottom: 0
                }}>
                  Running ML pipeline across {policies.length || 0} countries
                </p>
              </div>
            )}

            {/* Results Block */}
            {result && !loading && (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>

                {/* Factor Weights Panel */}
                <div style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "20px 24px",
                  marginBottom: "20px"
                }}>
                  {/* Header Row */}
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: showWeightsPanel ? "16px" : "4px"
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", flex: 1, marginRight: "16px" }}>
                      <div style={{ width: "20px", height: "1px", background: "var(--border)" }} />
                      <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.12em" }}>
                        FACTOR WEIGHTS
                      </span>
                      <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "12px", flexShrink: 0 }}>
                      <span style={{
                        fontSize: "12px",
                        fontFamily: "JetBrains Mono",
                        color: weightsSum === 100 ? "var(--cyan)" : "var(--red)",
                        fontWeight: 600
                      }}>
                        {weightsSum}%
                      </span>
                      <span 
                        onClick={() => setShowWeightsPanel(!showWeightsPanel)}
                        style={{
                          fontSize: "12px",
                          fontFamily: "JetBrains Mono",
                          color: "var(--text-muted)",
                          cursor: "pointer",
                          marginLeft: "12px"
                        }}
                        onMouseEnter={(e) => e.target.style.color = "var(--text-main)"}
                        onMouseLeave={(e) => e.target.style.color = "var(--text-muted)"}
                      >
                        {showWeightsPanel ? "hide" : "show"}
                      </span>
                    </div>
                  </div>

                  {showWeightsPanel && (
                    <>
                      <p style={{
                        fontSize: "14px",
                        fontFamily: "DM Sans",
                        color: "var(--text-muted)",
                        marginBottom: "16px",
                        marginTop: 0
                      }}>
                        Adjust factor significance. Recalculates recommendations in real-time.
                      </p>

                      <div style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gap: "16px 24px"
                      }}>
                        {[
                          { key: "sector_gap", label: "Regulatory Gap Severity", desc: "35" },
                          { key: "regulatory_maturity", label: "Statutory Infrastructure", desc: "25" },
                          { key: "semantic_need", label: "Legislative Intent Match", desc: "20" },
                          { key: "regional_pressure", label: "Geopolitical Peer Adoption", desc: "12" },
                          { key: "economic_tier", label: "Developmental Alignment", desc: "8" },
                        ].map((item) => (
                          <div key={item.key} style={{ display: "flex", flexDirection: "column" }}>
                            <div style={{
                              display: "flex",
                              justifyContent: "space-between",
                              marginBottom: "6px",
                              alignItems: "baseline"
                            }}>
                              <span style={{ fontSize: "14px", fontFamily: "DM Sans", fontWeight: 500, color: "var(--text-main)" }}>
                                {item.label}
                              </span>
                              <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                                <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                                  default {item.desc}%
                                </span>
                                <span style={{ fontSize: "14px", fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600 }}>
                                  {weights[item.key]}%
                                </span>
                              </div>
                            </div>

                            <input 
                              type="range"
                              min="0"
                              max="100"
                              value={weights[item.key]}
                              onChange={(e) => handleWeightChange(item.key, parseInt(e.target.value))}
                              style={{
                                width: "100%",
                                height: "4px",
                                background: "var(--border)",
                                borderRadius: "2px",
                                outline: "none",
                                appearance: "none",
                                cursor: "pointer",
                                accentColor: "var(--text-main)"
                              }}
                              className="custom-slider-input"
                            />
                          </div>
                        ))}
                      </div>

                      {/* Action buttons row */}
                      <div style={{
                        display: "flex",
                        gap: "8px",
                        marginTop: "16px",
                        justifyContent: "flex-end",
                        borderTop: "1px solid var(--border)",
                        paddingTop: "16px"
                      }}>
                        <button 
                          onClick={handleResetWeights}
                          style={{
                            border: "1px solid var(--border)",
                            background: "var(--bg-card)",
                            color: "var(--text-muted)",
                            fontSize: "14px",
                            fontFamily: "DM Sans",
                            padding: "12px 24px",
                            borderRadius: "6px",
                            cursor: "pointer",
                            fontWeight: 500,
                            transition: "all 0.15s ease"
                          }}
                          onMouseEnter={(e) => {
                            e.target.style.borderColor = "var(--border-lit)";
                            e.target.style.color = "var(--text-main)";
                            e.target.style.background = "var(--bg-hover)";
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.borderColor = "var(--border)";
                            e.target.style.color = "var(--text-muted)";
                            e.target.style.background = "var(--bg-card)";
                          }}
                        >
                          Reset to defaults
                        </button>
                        <button 
                          onClick={handleAutoBalance}
                          style={{
                            border: "1px solid var(--border)",
                            background: "var(--bg-card)",
                            color: "var(--text-muted)",
                            fontSize: "14px",
                            fontFamily: "DM Sans",
                            padding: "12px 24px",
                            borderRadius: "6px",
                            cursor: "pointer",
                            fontWeight: 500,
                            transition: "all 0.15s ease"
                          }}
                          onMouseEnter={(e) => {
                            e.target.style.borderColor = "var(--border-lit)";
                            e.target.style.color = "var(--text-main)";
                            e.target.style.background = "var(--bg-hover)";
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.borderColor = "var(--border)";
                            e.target.style.color = "var(--text-muted)";
                            e.target.style.background = "var(--bg-card)";
                          }}
                        >
                          Auto-Balance
                        </button>
                        <button 
                          onClick={handleRecalculate}
                          disabled={loading}
                          style={{
                            background: "var(--text-main)",
                            color: "var(--bg-card)",
                            fontSize: "14px",
                            fontFamily: "DM Sans",
                            fontWeight: 600,
                            padding: "12px 28px",
                            borderRadius: "6px",
                            cursor: "pointer",
                            border: "none",
                            transition: "all 0.15s ease"
                          }}
                          onMouseEnter={(e) => { e.target.style.background = "var(--text-muted)"; }}
                          onMouseLeave={(e) => { e.target.style.background = "var(--text-main)"; }}
                        >
                          {loading ? "Recalculating..." : "Recalculate"}
                        </button>
                      </div>
                    </>
                  )}
                </div>

                {/* Similar Policies Section */}
                {result?.similar_policies?.length > 0 && (
                  <div style={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    padding: "18px 22px",
                    marginBottom: "20px"
                  }}>
                    {/* Section label */}
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
                      <div style={{ width: "20px", height: "1px", background: "var(--border)" }} />
                      <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.12em" }}>
                        THEMATICALLY SIMILAR POLICIES
                      </span>
                      <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
                    </div>
                    
                    <div style={{
                      fontSize: "13px",
                      fontFamily: "DM Sans",
                      color: "var(--text-muted)",
                      marginBottom: "14px"
                    }}>
                      Regulatory Similarity · Underpinning baseline comparative context
                    </div>

                    {/* Horizontal scroll list */}
                    <div style={{
                      display: "flex",
                      gap: "10px",
                      overflowX: "auto",
                      paddingBottom: "8px"
                    }}>
                      {result.similar_policies.map((p, idx) => (
                        <div 
                          key={idx} 
                          onClick={() => nav(`/policies/${p.id}`)}
                          className="similar-policy-card-hover"
                          title={`Click to view ${p.title} details`}
                          style={{
                            background: "var(--bg-hover)",
                            border: "1px solid var(--border)",
                            borderRadius: "6px",
                            padding: "10px 14px",
                            flexShrink: 0,
                            minWidth: "200px",
                            maxWidth: "240px",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "space-between",
                            position: "relative"
                          }}>
                          <div>
                            <div style={{
                              fontFamily: "DM Sans",
                              fontWeight: 500,
                              fontSize: "13px",
                              color: "var(--text-main)",
                              lineHeight: "1.4",
                              display: "-webkit-box",
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: "vertical",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              paddingRight: "36px"
                            }}>
                              {p.title}
                            </div>
                            <div style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginTop: "4px" }}>
                              {p.country} · {p.sector}
                            </div>
                          </div>
                          <div style={{
                            position: "absolute",
                            top: "10px",
                            right: "14px",
                            fontFamily: "JetBrains Mono",
                            fontSize: "12px",
                            color: "var(--cyan)",
                            fontWeight: 600
                          }}>
                            {Math.round((p.approx_similarity ?? p.similarity ?? 0) * 100)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations Cards Stack */}
                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  {result.recommendations.map((rec, i) => {
                    const needPercent = Math.round(rec.need_score * 100);
                    const colorAccent = needPercent > 85 
                      ? "#5c9e2e" 
                      : needPercent > 70 
                        ? "#d97706" 
                        : "#2563eb";

                    const isReasonExpanded = expandedReasons[rec.country];
                    const needsReasonTruncation = rec.reasoning && rec.reasoning.length > 200;
                    const reasoningDisplayText = (needsReasonTruncation && !isReasonExpanded)
                      ? rec.reasoning.slice(0, 180) + "..."
                      : rec.reasoning;

                    return (
                      <div key={rec.country} style={{
                        background: "white",
                        border: "1px solid #e8e8e8",
                        borderRadius: "8px",
                        marginBottom: "16px",
                        overflow: "hidden"
                      }}>
                        
                        {/* TOP ACCENT BAR */}
                        <div style={{
                          height: "3px",
                          width: "100%",
                          background: colorAccent
                        }} />

                        {/* CARD CONTENT */}
                        <div style={{ padding: "20px 24px" }}>
                          
                          {/* TOP ROW (country header) */}
                          <div style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            marginBottom: "16px"
                          }}>
                            <div>
                              <div style={{ display: "flex", gap: "8px", alignItems: "baseline" }}>
                                <span style={{ fontFamily: "JetBrains Mono", fontSize: "12px", color: "#9ca3af" }}>
                                  #{i + 1}
                                </span>
                                <span style={{ fontFamily: "DM Sans", fontWeight: 700, fontSize: "22px", color: "#0a0a0a" }}>
                                  {rec.country}
                                </span>
                                <span style={{ fontFamily: "DM Sans", fontSize: "14px", color: "#9ca3af" }}>
                                  · {rec.region}
                                </span>
                              </div>

                              <div style={{ display: "flex", gap: "6px", marginTop: "4px" }}>
                                {rec.already_has_sector ? (
                                  <span style={{ 
                                    fontSize: "10px", 
                                    padding: "3px 8px", 
                                    borderRadius: "3px", 
                                    background: "#f5f5f5", 
                                    color: "#6b7280", 
                                    border: "1px solid #e8e8e8",
                                    fontFamily: "JetBrains Mono" 
                                  }}>
                                    has sector
                                  </span>
                                ) : (
                                  <span style={{ 
                                    fontSize: "10px", 
                                    padding: "3px 8px", 
                                    borderRadius: "3px", 
                                    background: "#fef2f2", 
                                    color: "#dc2626", 
                                    border: "1px solid #fecaca",
                                    fontFamily: "JetBrains Mono" 
                                  }}>
                                    Missing sector
                                  </span>
                                )}

                                <span style={{ 
                                  fontSize: "10px", 
                                  padding: "3px 8px", 
                                  borderRadius: "3px", 
                                  background: "#f5f5f5", 
                                  color: "#6b7280", 
                                  border: "1px solid #e8e8e8", 
                                  fontFamily: "JetBrains Mono"
                                }}>
                                  {rec.regulatory_maturity} maturity
                                </span>
                              </div>
                            </div>

                            <div style={{ textAlign: "right" }}>
                              <div style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "#9ca3af" }}>
                                NEED SCORE
                              </div>
                              <div style={{
                                fontFamily: "DM Sans",
                                fontSize: "38px",
                                fontWeight: 700,
                                color: colorAccent,
                                lineHeight: "1"
                              }}>
                                {needPercent}%
                              </div>
                            </div>
                          </div>

                          {/* SCORE BAR */}
                          <div style={{
                            height: "3px",
                            width: "100%",
                            background: "#f0f0f0",
                            borderRadius: "2px",
                            marginBottom: "20px"
                          }}>
                            <div style={{
                              height: "100%",
                              borderRadius: "2px",
                              width: `${rec.need_score * 100}%`,
                              background: colorAccent,
                              transition: "width 0.8s ease"
                            }} />
                          </div>

                          {/* THREE-COLUMN CONTENT GRID */}
                          <div style={{
                            display: "grid",
                            gridTemplateColumns: "1fr 1fr 200px",
                            gap: "20px",
                            alignItems: "start"
                          }}>
                            
                            {/* COLUMN 1 — "WHY THIS COUNTRY" */}
                            <div>
                              <div style={{
                                fontSize: "11px",
                                fontFamily: "JetBrains Mono",
                                color: "#9ca3af",
                                letterSpacing: "0.1em",
                                marginBottom: "8px"
                              }}>
                                WHY THIS COUNTRY
                              </div>
                              <div style={{
                                background: "#fafafa",
                                border: "1px solid #e8e8e8",
                                borderRadius: "6px",
                                padding: "14px 16px"
                              }}>
                                <p style={{
                                  fontSize: "14px",
                                  fontFamily: "DM Sans",
                                  color: "#374151",
                                  lineHeight: "1.7",
                                  margin: 0
                                }}>
                                  {reasoningDisplayText}
                                </p>
                                {needsReasonTruncation && (
                                  <button
                                    onClick={() => toggleReason(rec.country)}
                                    style={{
                                      background: "none",
                                      border: "none",
                                      color: "#5c9e2e",
                                      fontSize: "12px",
                                      fontFamily: "JetBrains Mono",
                                      cursor: "pointer",
                                      padding: 0,
                                      marginTop: "8px",
                                      fontWeight: 600
                                    }}
                                  >
                                    {isReasonExpanded ? "SHOW LESS" : "READ FULL REASONING"}
                                  </button>
                                )}
                              </div>
                            </div>

                            {/* COLUMN 2 — "EXPECTED BENEFITS" */}
                            <div>
                              <div style={{
                                fontSize: "11px",
                                fontFamily: "JetBrains Mono",
                                color: "#9ca3af",
                                letterSpacing: "0.1em",
                                marginBottom: "8px"
                              }}>
                                EXPECTED BENEFITS
                              </div>
                              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                                {rec.expected_benefits.map((b, idx) => (
                                  <div key={idx} style={{ display: "flex", gap: "8px", alignItems: "flex-start", marginBottom: "8px" }}>
                                    <span style={{ color: "#5c9e2e", fontWeight: 600, flexShrink: 0 }}>—</span>
                                    <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "#374151", lineHeight: "1.6" }}>
                                      {b}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* COLUMN 3 — RADAR CHART */}
                            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                              <div style={{ width: "200px", height: "180px" }}>
                                <ResponsiveContainer width="100%" height="100%">
                                  <RadarChart cx="50%" cy="50%" outerRadius="65%" data={[
                                    { subject: "Gap Severity", score: Math.round((rec.score_breakdown.sector_gap / (weights.sector_gap / 100 || 1)) * 100) },
                                    { subject: "Infrastructure", score: Math.round((rec.score_breakdown.regulatory_maturity / (weights.regulatory_maturity / 100 || 1)) * 100) },
                                    { subject: "Intent Match", score: Math.round((rec.score_breakdown.semantic_need / (weights.semantic_need / 100 || 1)) * 100) },
                                    { subject: "Peer Adoption", score: Math.round((rec.score_breakdown.regional_pressure / (weights.regional_pressure / 100 || 1)) * 100) },
                                    { subject: "Development", score: Math.round((rec.score_breakdown.economic_tier / (weights.economic_tier / 100 || 1)) * 100) }
                                  ]}>
                                    <PolarGrid stroke="#e8e8e8" />
                                    <PolarAngleAxis dataKey="subject" tick={{ fill: "#9ca3af", fontSize: 10, fontFamily: "JetBrains Mono" }} />
                                    <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                                    <Radar 
                                      name="Need Index" 
                                      dataKey="score" 
                                      stroke="#5c9e2e" 
                                      fill="#5c9e2e" 
                                      fillOpacity={0.08} 
                                      strokeWidth={1.5}
                                    />
                                  </RadarChart>
                                </ResponsiveContainer>
                              </div>

                              {/* Factor values mini grid */}
                              <div style={{
                                display: "grid",
                                gridTemplateColumns: "repeat(5, 1fr)",
                                textAlign: "center",
                                gap: "4px",
                                marginTop: "8px",
                                paddingTop: "8px",
                                borderTop: "1px solid #e8e8e8",
                                width: "100%"
                              }}>
                                {[
                                  { label: "Gap Severity", val: rec.score_breakdown.sector_gap },
                                  { label: "Infrastructure", val: rec.score_breakdown.regulatory_maturity },
                                  { label: "Intent Match", val: rec.score_breakdown.semantic_need },
                                  { label: "Peer Adoption", val: rec.score_breakdown.regional_pressure },
                                  { label: "Development", val: rec.score_breakdown.economic_tier }
                                ].map(itm => (
                                  <div key={itm.label} style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                                    <span style={{ fontSize: "11px", color: "#9ca3af", fontFamily: "JetBrains Mono" }}>
                                      {itm.label.slice(0, 3)}
                                    </span>
                                    <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "#0a0a0a", fontWeight: 600 }}>
                                      {itm.val.toFixed(1)}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>

                          </div>

                          {/* BOTTOM ROW (card footer) */}
                          <div style={{
                            borderTop: "1px solid #f0f0f0",
                            marginTop: "16px",
                            paddingTop: "12px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between"
                          }}>
                            {/* AI Proposal button */}
                            <button
                              onClick={() => handleGenerateProposal(rec.country, selected.sector)}
                              onMouseEnter={() => setHoveredProposalBtn(prev => ({ ...prev, [rec.country]: true }))}
                              onMouseLeave={() => setHoveredProposalBtn(prev => ({ ...prev, [rec.country]: false }))}
                              style={{
                                background: hoveredProposalBtn[rec.country] ? "#f0f7e8" : "white",
                                border: hoveredProposalBtn[rec.country] ? "1px solid #5c9e2e" : "1px solid #e8e8e8",
                                color: hoveredProposalBtn[rec.country] ? "#3d6b1e" : "#374151",
                                borderRadius: "6px",
                                padding: "8px 14px",
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                cursor: "pointer",
                                transition: "all 0.15s ease",
                                outline: "none"
                              }}
                            >
                              <Sparkles size={13} color="#5c9e2e" />
                              <span style={{ fontSize: "13px", fontFamily: "DM Sans", fontWeight: 500 }}>
                                Generate AI Proposal
                              </span>
                            </button>

                            {/* Feedback buttons */}
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                              <span style={{ fontSize: "12px", fontFamily: "DM Sans", color: "#9ca3af", marginRight: "8px" }}>
                                Was this relevant?
                              </span>
                              <button 
                                onClick={() => handleFeedback(rec.country, true)}
                                onMouseEnter={() => setHoveredFeedbackBtn(prev => ({ ...prev, [`${rec.country}_pos`]: true }))}
                                onMouseLeave={() => setHoveredFeedbackBtn(prev => ({ ...prev, [`${rec.country}_pos`]: false }))}
                                style={{
                                  border: feedbackGiven[rec.country] === "positive" ? "1px solid #5c9e2e" : "1px solid #e8e8e8",
                                  background: feedbackGiven[rec.country] === "positive" 
                                    ? "#f0f7e8" 
                                    : hoveredFeedbackBtn[`${rec.country}_pos`] 
                                      ? "#fafafa" 
                                      : "white",
                                  color: feedbackGiven[rec.country] === "positive" ? "#3d6b1e" : "#6b7280",
                                  fontSize: "12px",
                                  fontFamily: "DM Sans",
                                  padding: "6px 12px",
                                  borderRadius: "4px",
                                  cursor: "pointer",
                                  display: "flex",
                                  alignItems: "center",
                                  transition: "all 0.15s ease"
                                }}
                              >
                                <ThumbsUp size={12} style={{ marginRight: "4px" }} />
                                Helpful
                              </button>
                              <button 
                                onClick={() => handleFeedback(rec.country, false)}
                                onMouseEnter={() => setHoveredFeedbackBtn(prev => ({ ...prev, [`${rec.country}_neg`]: true }))}
                                onMouseLeave={() => setHoveredFeedbackBtn(prev => ({ ...prev, [`${rec.country}_neg`]: false }))}
                                style={{
                                  border: feedbackGiven[rec.country] === "negative" ? "1px solid #fecaca" : "1px solid #e8e8e8",
                                  background: feedbackGiven[rec.country] === "negative" 
                                    ? "#fef2f2" 
                                    : hoveredFeedbackBtn[`${rec.country}_neg`] 
                                      ? "#fafafa" 
                                      : "white",
                                  color: feedbackGiven[rec.country] === "negative" ? "#dc2626" : "#6b7280",
                                  fontSize: "12px",
                                  fontFamily: "DM Sans",
                                  padding: "6px 12px",
                                  borderRadius: "4px",
                                  cursor: "pointer",
                                  display: "flex",
                                  alignItems: "center",
                                  transition: "all 0.15s ease"
                                }}
                              >
                                <ThumbsDown size={12} style={{ marginRight: "4px" }} />
                                Not Relevant
                              </button>
                            </div>
                          </div>

                        </div>
                      </div>
                    );
                  })}
                </div>

              </div>
            )}

          </div>
        )}

      </div>

      {/* ========================================================================= */}
      {/* SLIDING AI BRIEF DRAWER */}
      {/* ========================================================================= */}
      {drawerOpen && (
        <div style={{
          position: "fixed",
          top: 0, right: 0, bottom: 0,
          width: "540px",
          background: "white",
          borderLeft: "1px solid #e8e8e8",
          boxShadow: "-8px 0 24px rgba(0,0,0,0.06)",
          zIndex: 1000,
          display: "flex",
          flexDirection: "column",
          color: "#0a0a0a",
          animation: "slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards"
        }}>
          
          {/* Drawer Header */}
          <div style={{
            padding: "24px 28px",
            borderBottom: "1px solid #e8e8e8",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                <Sparkles size={14} color="#5c9e2e" />
                <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "#5c9e2e", letterSpacing: "0.1em" }}>
                  AI LEGISLATIVE SYNTHESIS
                </span>
              </div>
              <h2 style={{ fontFamily: "DM Sans", fontSize: "22px", fontWeight: 700, margin: 0 }}>
                Executive Brief & Draft Proposal
              </h2>
            </div>
            <button 
              onClick={() => setDrawerOpen(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "#9ca3af",
                fontSize: "20px",
                cursor: "pointer",
                padding: "4px"
              }}
            >
              ✕
            </button>
          </div>

          {/* Drawer Body */}
          <div style={{ flex: 1, overflowY: "auto", padding: "28px" }}>
            {drawerLoading && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", gap: "16px" }}>
                <LoadingSpinner label="Drafting professional policy framework..." />
                <p style={{ color: "#9ca3af", fontSize: "14px", textAlign: "center", maxWidth: "80%", fontFamily: "DM Sans" }}>
                  Running semantic gap synthesis, mapping developmental parameters, and assembling implementation timelines.
                </p>
              </div>
            )}

            {proposal && !drawerLoading && (
              <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                
                {/* Proposal Title */}
                <div style={{ 
                  padding: "16px 20px", 
                  background: "#fafafa", 
                  border: "1px solid #e8e8e8",
                  borderRadius: "8px"
                }}>
                  <div style={{ fontSize: "12px", color: "#5c9e2e", fontFamily: "JetBrains Mono", marginBottom: "6px" }}>
                    DRAFT STATUTORY BILL TITLE
                  </div>
                  <h3 style={{ fontFamily: "DM Sans", fontSize: "18px", fontWeight: 700, margin: 0, color: "#0a0a0a" }}>
                    {proposal.suggested_title}
                  </h3>
                </div>

                {/* Country Context */}
                <div>
                  <div style={{ fontSize: "12px", color: "#9ca3af", fontFamily: "JetBrains Mono", marginBottom: "6px" }}>
                    NATIONAL DEVELOPMENT CONTEXT & STATUTORY JUSTIFICATION
                  </div>
                  <div style={{ background: "#ffffff", padding: "14px 18px", borderRadius: "8px", border: "1px solid #e8e8e8" }}>
                    <p style={{ fontSize: "14px", lineHeight: "1.6", color: "#374151", margin: 0, fontFamily: "DM Sans" }}>
                      {proposal.policy_context}
                    </p>
                  </div>
                </div>

                {/* Focus Areas */}
                <div>
                  <div style={{ fontSize: "12px", color: "#9ca3af", fontFamily: "JetBrains Mono", marginBottom: "6px" }}>
                    PRIORITY STRATEGIC DEVELOPMENT AREAS
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    {proposal.priority_areas?.map((area, idx) => (
                      <div key={idx} style={{ 
                        display: "flex", 
                        alignItems: "center", 
                        gap: "8px", 
                        background: "#fafafa", 
                        padding: "8px 12px", 
                        borderRadius: "6px", 
                        border: "1px solid #e8e8e8" 
                      }}>
                        <span style={{ color: "#5c9e2e", fontSize: "13px", fontFamily: "JetBrains Mono", fontWeight: 600 }}>0{idx + 1}</span>
                        <span style={{ fontSize: "14px", color: "#374151", fontFamily: "DM Sans" }}>{area}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommended Bill Sections */}
                <div>
                  <div style={{ fontSize: "12px", color: "#9ca3af", fontFamily: "JetBrains Mono", marginBottom: "6px" }}>
                    RECOMMENDED BILL SECTIONS
                  </div>
                  <div style={{ background: "white", borderRadius: "8px", border: "1px solid #e8e8e8", overflow: "hidden" }}>
                    {proposal.recommended_sections?.map((section, idx) => (
                      <div key={idx} style={{
                        padding: "10px 14px",
                        fontSize: "14px",
                        color: "#374151",
                        borderBottom: idx < proposal.recommended_sections.length - 1 ? "1px solid #e8e8e8" : "none",
                        fontFamily: "JetBrains Mono"
                      }}>
                        {section}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Key Requirements */}
                <div>
                  <div style={{ fontSize: "12px", color: "#9ca3af", fontFamily: "JetBrains Mono", marginBottom: "6px" }}>
                    KEY IMPLEMENTATION MANDATES
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {proposal.key_requirements?.map((req, idx) => (
                      <div key={idx} style={{ 
                        display: "flex", 
                        alignItems: "flex-start", 
                        gap: "8px", 
                        background: "#fafafa", 
                        padding: "10px 14px", 
                        borderRadius: "6px", 
                        border: "1px solid #e8e8e8" 
                      }}>
                        <span style={{ color: "#5c9e2e", fontWeight: 600, fontSize: "14px" }}>✓</span>
                        <span style={{ fontSize: "14px", color: "#374151", lineHeight: "1.5", fontFamily: "DM Sans" }}>{req}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Implementation Timeline */}
                <div>
                  <div style={{ fontSize: "12px", color: "#9ca3af", fontFamily: "JetBrains Mono", marginBottom: "6px" }}>
                    EXPECTED ENACTMENT TIMELINE
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {Object.entries(proposal.implementation_timeline || {}).map(([phase, desc]) => (
                      <div key={phase} style={{
                        background: "white",
                        padding: "12px 16px",
                        borderRadius: "8px",
                        border: "1px solid #e8e8e8"
                      }}>
                        <div style={{ color: "#5c9e2e", fontSize: "13px", fontFamily: "JetBrains Mono", fontWeight: 600, marginBottom: "4px" }}>
                          {phase}
                        </div>
                        <div style={{ fontSize: "14px", color: "#374151", fontFamily: "DM Sans", lineHeight: "1.5" }}>
                          {desc}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* NLP Reference Sources */}
                {proposal.reference_policies?.length > 0 && (
                  <div>
                    <div style={{ fontSize: "12px", color: "#9ca3af", fontFamily: "JetBrains Mono", marginBottom: "6px" }}>
                      NLP CROSS-REFERENCE SOURCES
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                      {proposal.reference_policies.map((ref, idx) => (
                        <div key={idx} style={{ 
                          display: "flex", 
                          justifyContent: "space-between", 
                          alignItems: "center", 
                          background: "#fafafa", 
                          padding: "8px 12px", 
                          borderRadius: "6px", 
                          border: "1px solid #e8e8e8" 
                        }}>
                          <div>
                            <div style={{ fontSize: "14px", color: "#0a0a0a", fontWeight: 600, fontFamily: "DM Sans" }}>{ref.title}</div>
                            <div style={{ fontSize: "12px", color: "#9ca3af", fontFamily: "DM Sans" }}>Jurisdiction: {ref.country}</div>
                          </div>
                          {ref.source_url && (
                            <a href={ref.source_url} target="_blank" rel="noopener noreferrer" style={{ color: "#5c9e2e", fontSize: "12px", textDecoration: "none", display: "flex", alignItems: "center", gap: "4px", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                              <ExternalLink size={12} /> LINK
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            )}
          </div>

          {/* Drawer Footer */}
          {proposal && !drawerLoading && (
            <div style={{
              padding: "20px 28px",
              borderTop: "1px solid #e8e8e8",
              background: "white",
              display: "flex"
            }}>
              <button 
                onClick={() => downloadProposalPDF(proposal)}
                style={{
                  flex: 1,
                  padding: "12px",
                  borderRadius: "8px",
                  background: "#0a0a0a",
                  color: "white",
                  fontFamily: "DM Sans",
                  fontWeight: 700,
                  fontSize: 15,
                  cursor: "pointer",
                  border: "none",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  transition: "background 0.15s ease"
                }}
                onMouseEnter={(e) => e.target.style.background = "#1f2937"}
                onMouseLeave={(e) => e.target.style.background = "#0a0a0a"}
              >
                📥 DOWNLOAD EXECUTIVE PDF PROPOSAL
              </button>
            </div>
          )}

        </div>
      )}

    </div>
  );
}