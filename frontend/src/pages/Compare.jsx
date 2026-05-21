import { useEffect, useState, useRef } from "react";
import { fetchPolicies, comparePolicies } from "../services/api";
import PolicyCard from "../components/PolicyCard";
import SectorBadge from "../components/SectorBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import { GitCompare, CheckCircle2, XCircle, Lightbulb, RotateCcw } from "lucide-react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export default function Compare() {
  const [policies,     setPolicies]     = useState([]);
  const [sel1,         setSel1]         = useState(null);
  const [sel2,         setSel2]         = useState(null);
  const [result,       setResult]       = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [step,         setStep]         = useState(1);
  const [sectorFilter, setSectorFilter] = useState("");

  // Removed reportRef since we use jsPDF autoTable natively

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

  const downloadReport = () => {
    if (!result) return;
    
    const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
    const p1 = result.policy_1;
    const p2 = result.policy_2;

    // Header bar
    pdf.setFillColor(17, 24, 39);
    pdf.rect(0, 0, 210, 20, "F");
    pdf.setTextColor(34, 211, 238);
    pdf.setFontSize(16);
    pdf.setFont("helvetica", "bold");
    pdf.text("PolicyIQ — Policy Comparison Report", 14, 13);

    // Timestamp
    pdf.setTextColor(100, 116, 139);
    pdf.setFontSize(9);
    pdf.setFont("helvetica", "normal");
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 14, 26);

    let startY = 32;

    // 1. Overview Table
    autoTable(pdf, {
      startY: startY,
      head: [["Attribute", `Policy A: ${p1.title}`, `Policy B: ${p2.title}`]],
      body: [
        ["Sector", p1.sector || "N/A", p2.sector || "N/A"],
        ["Jurisdiction", p1.country || "N/A", p2.country || "N/A"],
        ["Region", p1.region || "N/A", p2.region || "N/A"],
        ["Year", p1.year ? String(p1.year) : "N/A", p2.year ? String(p2.year) : "N/A"]
      ],
      theme: "grid",
      headStyles: { fillColor: [17, 24, 39], textColor: [255, 255, 255], fontStyle: "bold" },
      styles: { fontSize: 10, cellPadding: 4, lineColor: [226, 232, 240] },
      columnStyles: { 0: { fontStyle: "bold", cellWidth: 30, fillColor: [248, 250, 252], textColor: [15, 23, 42] } }
    });
    
    startY = pdf.lastAutoTable.finalY + 10;

    // 2. Focus Areas & Tags Table
    autoTable(pdf, {
      startY: startY,
      head: [["Focus Areas", "Tags / Topics"]],
      body: [
        ["Shared Focus", result.ml_metrics?.themes?.shared?.length ? result.ml_metrics.themes.shared.join(", ") : "None"],
        ["Unique to Policy A", result.ml_metrics?.themes?.unique_1?.length ? result.ml_metrics.themes.unique_1.join(", ") : "None"],
        ["Unique to Policy B", result.ml_metrics?.themes?.unique_2?.length ? result.ml_metrics.themes.unique_2.join(", ") : "None"]
      ],
      theme: "grid",
      headStyles: { fillColor: [51, 65, 85], textColor: [255, 255, 255], fontStyle: "bold" },
      styles: { fontSize: 10, cellPadding: 4, lineColor: [226, 232, 240] },
      columnStyles: { 0: { fontStyle: "bold", cellWidth: 40, fillColor: [248, 250, 252], textColor: [15, 23, 42] } }
    });

    startY = pdf.lastAutoTable.finalY + 10;

    // 3. Regulatory Rubric Scores
    if (p1.rubric && p2.rubric) {
      autoTable(pdf, {
        startY: startY,
        head: [["Regulatory Dimension", `Policy A Score`, `Policy B Score`]],
        body: [
          ["Prescriptiveness (Binding)", `${p1.rubric.prescriptiveness}/100`, `${p2.rubric.prescriptiveness}/100`],
          ["Rights Orientation", `${p1.rubric.rights_orientation}/100`, `${p2.rubric.rights_orientation}/100`],
          ["Technical Specificity", `${p1.rubric.technical_specificity}/100`, `${p2.rubric.technical_specificity}/100`],
          ["Enforcement Power", `${p1.rubric.enforcement_power}/100`, `${p2.rubric.enforcement_power}/100`]
        ],
        theme: "grid",
        headStyles: { fillColor: [14, 116, 144], textColor: [255, 255, 255], fontStyle: "bold" },
        styles: { fontSize: 10, cellPadding: 4, lineColor: [226, 232, 240] },
        columnStyles: { 0: { fontStyle: "bold", cellWidth: 40, fillColor: [248, 250, 252], textColor: [15, 23, 42] } }
      });
      startY = pdf.lastAutoTable.finalY + 10;
    }
    
    // 4. Verbatim Clause Gaps
    if (result.ml_metrics?.clause_gaps) {
        const gaps1 = result.ml_metrics.clause_gaps.orphaned_in_1 || [];
        const gaps2 = result.ml_metrics.clause_gaps.orphaned_in_2 || [];
        
        if (gaps1.length > 0 || gaps2.length > 0) {
            autoTable(pdf, {
                startY: startY,
                head: [["Orphaned Clauses (Policy A)", "Orphaned Clauses (Policy B)"]],
                body: [
                  [
                    gaps1.map(g => `• ${g.text}`).join("\n\n") || "None",
                    gaps2.map(g => `• ${g.text}`).join("\n\n") || "None"
                  ]
                ],
                theme: "grid",
                headStyles: { fillColor: [99, 102, 241], textColor: [255, 255, 255], fontStyle: "bold" },
                styles: { fontSize: 9, cellPadding: 4, lineColor: [226, 232, 240] }
            });
            startY = pdf.lastAutoTable.finalY + 10;
        }
    }

    // 5. Penalties & Fines (if any)
    if (p1.penalty_fines?.has_fines || p2.penalty_fines?.has_fines) {
      autoTable(pdf, {
        startY: startY,
        head: [["Penalties & Fines", "Details"]],
        body: [
          ["Policy A", p1.penalty_fines?.summary || "No specific fines mentioned."],
          ["Policy B", p2.penalty_fines?.summary || "No specific fines mentioned."]
        ],
        theme: "grid",
        headStyles: { fillColor: [244, 63, 94], textColor: [255, 255, 255], fontStyle: "bold" },
        styles: { fontSize: 10, cellPadding: 4, lineColor: [254, 226, 226] },
        columnStyles: { 0: { fontStyle: "bold", cellWidth: 35, fillColor: [255, 241, 242], textColor: [225, 29, 72] } }
      });
      startY = pdf.lastAutoTable.finalY + 10;
    }

    // 4. AI-Generated Insights
    if (result.insights?.length > 0) {
      pdf.setFontSize(12);
      pdf.setFont("helvetica", "bold");
      pdf.setTextColor(17, 24, 39);
      pdf.text("AI-Generated Strategic Insights", 14, startY);
      
      const insightRows = result.insights.map(ins => ["•", ins]);
      
      autoTable(pdf, {
        startY: startY + 4,
        body: insightRows,
        theme: "plain",
        styles: { fontSize: 10, cellPadding: 2, textColor: [71, 85, 105] },
        columnStyles: { 0: { cellWidth: 10, fontStyle: "bold", textColor: [34, 211, 238] } }
      });
    }

    // Add Footer (Watermark & Page Numbers) to all pages
    const pageCount = pdf.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFont("helvetica", "italic");
      pdf.setFontSize(9);
      pdf.setTextColor(148, 163, 184); // slate-400
      
      // Left aligned watermark
      pdf.text("PolicyIQ Intelligence Platform", 14, 287);
      
      // Right aligned page number
      pdf.text(`Page ${i} of ${pageCount}`, 196, 287, { align: "right" });
      
      // Add a subtle top border for the footer
      pdf.setDrawColor(226, 232, 240); // slate-200
      pdf.line(14, 282, 196, 282);
    }

    // Save
    const filename = `PolicyIQ_Comparison_${p1.id}_vs_${p2.id}.pdf`;
    pdf.save(filename);
  };

  return (
    <div style={{
      flex: 1,
      overflowY: "auto",
      background: "#ffffff",
      minHeight: "100vh"
    }}>
      <div style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "32px 40px",
        width: "100%"
      }}>
      <div className="fade-up" style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 12 }}>
              <span style={{ color: "var(--cyan)", marginRight: 8 }}>■</span> PREP / ANALYSIS
            </div>
            <h1 style={{ fontFamily: "Inter", fontSize: 44, fontWeight: 800, color: "var(--text-main)", letterSpacing: "-1px", marginBottom: 16 }}>
              Compare frameworks <span className="half-highlight">side-by-side.</span>
            </h1>
            <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
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

      {step === 3 && result && !loading && (
        <div className="fade-up" style={{ marginBottom: 24 }}>
          {/* Comparison View */}
          <div>

            {/* Premium V2 Overall Similarity Banner */}
            {result.overall_metrics && (
              <div className="card" style={{
                padding: "20px 24px", marginBottom: 20,
                background: "linear-gradient(135deg, rgba(34,211,238,0.06) 0%, rgba(129,140,248,0.06) 100%)",
                borderColor: "rgba(34,211,238,0.25)",
                textAlign: "center"
              }}>
                <div style={{ fontSize: 10, color: "var(--cyan)", fontFamily: "JetBrains Mono", marginBottom: 6, letterSpacing: "1px" }}>
                  COMPOSITE REGULATORY ALIGNMENT
                </div>
                <div style={{ fontFamily: "Syne", fontWeight: 800, fontSize: 50, color: "var(--cyan)", lineHeight: 1.1 }}>
                  {Math.round(result.overall_metrics.composite_score * 100)}%
                </div>
                <div style={{ fontSize: 13, fontFamily: "Inter", fontWeight: 700, color: "var(--text-main)", marginTop: 6, letterSpacing: "0.5px" }}>
                  {result.overall_metrics.similarity_label}
                </div>
                
                <div style={{ display: "flex", justifyContent: "center", gap: 32, marginTop: 16, borderTop: "1px dashed var(--border)", paddingTop: 14 }}>
                  {[
                    { label: "Semantic Sim.", val: result.overall_metrics.semantic_similarity },
                    { label: "Cross-Encoder (Sigmoid)", val: result.overall_metrics.cross_encoder_normalized },
                    { label: "Jaccard Tag Sim.", val: result.overall_metrics.jaccard_coefficient }
                  ].map(metric => (
                    <div key={metric.label}>
                      <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 4 }}>
                        {metric.label}
                      </div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-main)", fontFamily: "JetBrains Mono" }}>
                        {Math.round(metric.val * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Policy Cards Side by Side */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 16 }}>
              {[(result.policy1 || result.policy_1), (result.policy2 || result.policy_2)].map((p, i) => {
                if (!p) return null;
                return (
                  <div key={i} className="card" style={{
                    padding: "18px 22px",
                    borderColor: i === 0 ? "#818cf8" : "var(--cyan)"
                  }}>
                    <div style={{ fontSize: 10, fontFamily: "JetBrains Mono", color: i === 0 ? "#818cf8" : "var(--cyan)", marginBottom: 8 }}>
                      POLICY {i === 0 ? "A" : "B"}
                    </div>
                    <div style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 8 }}>
                      {p.title}
                    </div>
                    <SectorBadge sector={p.sector} />
                    <div style={{ marginTop: 10, display: "flex", gap: 12, fontSize: 12, color: "var(--text-muted)" }}>
                      <span>{p.country}</span>
                      <span>{p.year}</span>
                      <span>{p.region}</span>
                    </div>

                    {/* Approach */}
                    {p.approach && (
                      <div style={{ marginTop: 8 }}>
                        <span style={{
                          fontSize: 10, padding: "2px 7px", borderRadius: 4,
                          background: "rgba(245,158,11,0.08)", color: "#f59e0b",
                          border: "1px solid rgba(245,158,11,0.2)", fontFamily: "JetBrains Mono"
                        }}>
                          {p.approach} Approach
                        </span>
                      </div>
                    )}

                    {/* Tags */}
                    {p.tags?.length > 0 && (
                      <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {p.tags.slice(0, 5).map(t => (
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
                  </div>
                );
              })}
            </div>

            {/* 6-Dimensional Analysis Grid */}
            {result.dimensional_breakdown && (
              <div className="card" style={{ padding: "20px 24px", marginBottom: 16 }}>
                <div style={{ fontSize: 11, color: "var(--cyan)", fontFamily: "JetBrains Mono", marginBottom: 14, letterSpacing: "0.5px" }}>
                  6-DIMENSIONAL REGULATORY ANALYSIS
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  {Object.entries(result.dimensional_breakdown).map(([dimName, info]) => (
                    <div key={dimName} style={{ background: "rgba(255,255,255,0.015)", border: "1px solid var(--border)", borderRadius: 8, padding: "12px 16px" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                        <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-main)", textTransform: "capitalize" }}>
                          {dimName}
                        </span>
                        <span style={{ fontSize: 10, fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                          Gap: {Math.round(info.gap * 100)}% (Dom: {info.dominant === "policy1" ? "Policy A" : "Policy B"})
                        </span>
                      </div>
                      
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {/* Policy A Strength Bar */}
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <span style={{ fontSize: 10, width: 50, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>Policy A</span>
                          <div style={{ flex: 1, height: 6, background: "rgba(255,255,255,0.05)", borderRadius: 3 }}>
                            <div style={{ width: `${Math.round(info.strength_policy1 * 100)}%`, height: "100%", background: "#818cf8", borderRadius: 3 }} />
                          </div>
                          <span style={{ fontSize: 10, color: "#818cf8", width: 35, fontFamily: "JetBrains Mono", textAlign: "right" }}>
                            {Math.round(info.strength_policy1 * 100)}%
                          </span>
                        </div>
                        {/* Policy B Strength Bar */}
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <span style={{ fontSize: 10, width: 50, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>Policy B</span>
                          <div style={{ flex: 1, height: 6, background: "rgba(255,255,255,0.05)", borderRadius: 3 }}>
                            <div style={{ width: `${Math.round(info.strength_policy2 * 100)}%`, height: "100%", background: "var(--cyan)", borderRadius: 3 }} />
                          </div>
                          <span style={{ fontSize: 10, color: "var(--cyan)", width: 35, fontFamily: "JetBrains Mono", textAlign: "right" }}>
                            {Math.round(info.strength_policy2 * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tag Gap Analysis */}
            {(result.shared_tags || result.only_policy1_tags || result.only_policy2_tags) && (
              <div className="card" style={{ padding: "20px 24px", marginBottom: 16 }}>
                <div style={{ fontSize: 11, color: "var(--cyan)", fontFamily: "JetBrains Mono", marginBottom: 14, letterSpacing: "0.5px" }}>
                  TAG GAP CLOUD ANALYSIS
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
                  {/* Shared Tags */}
                  <div style={{ background: "rgba(16,185,129,0.01)", border: "1px solid rgba(16,185,129,0.15)", borderRadius: 8, padding: "12px 14px" }}>
                    <div style={{ fontSize: 10, color: "#10b981", fontWeight: 700, fontFamily: "JetBrains Mono", marginBottom: 10 }}>
                      SHARED FOCUS TAGS ({result.shared_tags?.length || 0})
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                      {result.shared_tags?.length > 0 ? (
                        result.shared_tags.map(t => (
                          <span key={t} style={{ fontSize: 10, padding: "2px 7px", borderRadius: 4, background: "rgba(16,185,129,0.08)", color: "#10b981", border: "1px solid rgba(16,185,129,0.2)" }}>
                            {t}
                          </span>
                        ))
                      ) : (
                        <span style={{ fontSize: 11, color: "var(--text-dim)" }}>No shared focus tags</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Only Policy A Tags */}
                  <div style={{ background: "rgba(129,140,248,0.01)", border: "1px solid rgba(129,140,248,0.15)", borderRadius: 8, padding: "12px 14px" }}>
                    <div style={{ fontSize: 10, color: "#818cf8", fontWeight: 700, fontFamily: "JetBrains Mono", marginBottom: 10 }}>
                      UNIQUE TO POLICY A ({result.only_policy1_tags?.length || 0})
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                      {result.only_policy1_tags?.length > 0 ? (
                        result.only_policy1_tags.map(t => (
                          <span key={t} style={{ fontSize: 10, padding: "2px 7px", borderRadius: 4, background: "rgba(129,140,248,0.08)", color: "#818cf8", border: "1px solid rgba(129,140,248,0.2)" }}>
                            {t}
                          </span>
                        ))
                      ) : (
                        <span style={{ fontSize: 11, color: "var(--text-dim)" }}>No unique tags</span>
                      )}
                    </div>
                  </div>

                  {/* Only Policy B Tags */}
                  <div style={{ background: "rgba(6,182,212,0.01)", border: "1px solid rgba(6,182,212,0.15)", borderRadius: 8, padding: "12px 14px" }}>
                    <div style={{ fontSize: 10, color: "var(--cyan)", fontWeight: 700, fontFamily: "JetBrains Mono", marginBottom: 10 }}>
                      UNIQUE TO POLICY B ({result.only_policy2_tags?.length || 0})
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                      {result.only_policy2_tags?.length > 0 ? (
                        result.only_policy2_tags.map(t => (
                          <span key={t} style={{ fontSize: 10, padding: "2px 7px", borderRadius: 4, background: "rgba(6,182,212,0.08)", color: "var(--cyan)", border: "1px solid rgba(6,182,212,0.2)" }}>
                            {t}
                          </span>
                        ))
                      ) : (
                        <span style={{ fontSize: 11, color: "var(--text-dim)" }}>No unique tags</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Insights Panel */}
            <div className="card" style={{ padding: "22px 26px", borderColor: "rgba(245,158,11,0.25)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <Lightbulb size={15} color="#f59e0b" />
                <span style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 14, color: "var(--text-main)" }}>
                  AI-Generated Strategic Insights
                </span>
              </div>

              {/* Dynamic Insights list */}
              {result.insights?.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
                  {result.insights.map((insight, idx) => (
                    <div key={idx} style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: 12, color: "var(--text-muted)", lineHeight: 1.6 }}>
                      <span style={{ color: "#f59e0b", fontWeight: 900, marginRight: 2 }}>•</span>
                      <span>{insight}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 16 }}>
                  No structural comparative insights loaded.
                </div>
              )}

              {/* Source Links */}
              <div style={{ display: "flex", gap: 12, paddingTop: 14, borderTop: "1px solid var(--border)" }}>
                {[(result.policy1 || result.policy_1), (result.policy2 || result.policy_2)].map((p, i) => (
                  p?.source_url ? (
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

          </div>{/* ← end of comparison view div */}

          {/* Download button */}
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
            <button onClick={downloadReport} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "10px 20px", borderRadius: 8,
              background: "linear-gradient(135deg, var(--cyan-dim), #0e7490)",
              border: "none", color: "#fff",
              fontFamily: "Inter", fontWeight: 700,
              fontSize: 13, cursor: "pointer",
            }}>
              ⬇ Download Comparison Report (PDF)
            </button>
          </div>

        </div>
      )}

      {loading && <LoadingSpinner label="Running comparison analysis..." />}

      {/* Sector Filter + Policy Grid */}
      {step < 3 && (
        <>
          <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
            {["", "AI Governance", "Cybersecurity", "Data Privacy", "Healthcare AI", "Financial Regulation", "ESG Policies", "POSH Policies", "IoT and Robotics"].map(s => (
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
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
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
    </div>
  );
}