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

      {step === 3 && result && !loading && (
        <div className="fade-up" style={{ marginBottom: 24 }}>
          {/* Comparison View */}
          <div>

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

                  {/* Tags */}
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

                  {/* Multi-Dimensional Rubric */}
                  {p.rubric && (
                    <div style={{ marginTop: 14 }}>
                      <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 8, borderBottom: "1px solid var(--border)", paddingBottom: 4 }}>
                        REGULATORY RUBRIC SCORES
                      </div>
                      
                      {[
                        { label: "Prescriptiveness", score: p.rubric.prescriptiveness, color: "#f43f5e" },
                        { label: "Rights Orientation", score: p.rubric.rights_orientation, color: "#34d399" },
                        { label: "Tech Specificity", score: p.rubric.technical_specificity, color: "#818cf8" },
                        { label: "Enforcement Power", score: p.rubric.enforcement_power, color: "#f59e0b" }
                      ].map(dim => (
                        <div key={dim.label} style={{ marginBottom: 6 }}>
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-muted)", marginBottom: 2 }}>
                            <span>{dim.label}</span>
                            <span style={{ color: dim.color }}>{dim.score}/100</span>
                          </div>
                          <div style={{ width: "100%", height: 4, background: "var(--bg-hover)", borderRadius: 2 }}>
                            <div style={{ width: `${dim.score}%`, height: "100%", background: dim.color, borderRadius: 2 }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Unique Focus Areas (ML TF-IDF) */}
                  {i === 0 && result.ml_metrics?.themes?.unique_1?.length > 0 && (
                    <div style={{ marginTop: 12 }}>
                      <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 4 }}>
                        ML-EXTRACTED UNIQUE FOCUS
                      </div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {result.ml_metrics.themes.unique_1.map(t => (
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
                  {i === 1 && result.ml_metrics?.themes?.unique_2?.length > 0 && (
                    <div style={{ marginTop: 12 }}>
                      <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 4 }}>
                        ML-EXTRACTED UNIQUE FOCUS
                      </div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {result.ml_metrics.themes.unique_2.map(t => (
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

                  {/* Clause Gaps (Sentence Matrices) */}
                  {i === 0 && result.ml_metrics?.clause_gaps?.orphaned_in_1?.length > 0 && (
                    <div style={{ marginTop: 14 }}>
                      <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 6 }}>
                        VERBATIM ORPHANED CLAUSES (GAP)
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {result.ml_metrics.clause_gaps.orphaned_in_1.map((gap, idx) => (
                          <div key={idx} style={{ 
                            fontSize: 11, color: "var(--text-muted)", 
                            background: "rgba(129,140,248,0.05)", borderLeft: "2px solid #818cf8",
                            padding: "6px 10px", lineHeight: 1.4, borderRadius: "0 4px 4px 0"
                          }}>
                            "{gap.text}"
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {i === 1 && result.ml_metrics?.clause_gaps?.orphaned_in_2?.length > 0 && (
                    <div style={{ marginTop: 14 }}>
                      <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 6 }}>
                        VERBATIM ORPHANED CLAUSES (GAP)
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {result.ml_metrics.clause_gaps.orphaned_in_2.map((gap, idx) => (
                          <div key={idx} style={{ 
                            fontSize: 11, color: "var(--text-muted)", 
                            background: "rgba(34,211,238,0.05)", borderLeft: "2px solid var(--cyan)",
                            padding: "6px 10px", lineHeight: 1.4, borderRadius: "0 4px 4px 0"
                          }}>
                            "{gap.text}"
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Penalty Fines Summary */}
                  {p.penalty_fines?.has_fines && (
                    <div style={{
                      marginTop: 10, padding: "8px 10px", borderRadius: 6,
                      background: "rgba(244,63,94,0.06)",
                      border: "1px solid rgba(244,63,94,0.15)",
                    }}>
                      <div style={{ fontSize: 10, color: "#f43f5e", fontFamily: "JetBrains Mono", marginBottom: 4 }}>
                        ⚖ PENALTIES
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-main)", lineHeight: 1.5 }}>
                        {p.penalty_fines.summary}
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

              {/* Semantic Alignment Bar */}
              {result.ml_metrics && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                    <span>SEMANTIC ALIGNMENT (BERT)</span>
                    <span style={{ color: "var(--cyan)" }}>{Math.round(result.ml_metrics.semantic_similarity_score * 100)}%</span>
                  </div>
                  <div style={{ width: "100%", height: 6, background: "rgba(255,255,255,0.05)", borderRadius: 3, overflow: "hidden" }}>
                    <div style={{ 
                      width: `${Math.round(result.ml_metrics.semantic_similarity_score * 100)}%`, 
                      height: "100%", 
                      background: "linear-gradient(90deg, #818cf8, var(--cyan))",
                      transition: "width 1s ease-out"
                    }} />
                  </div>
                </div>
              )}

              {/* Summary Row */}
              <div style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}>
                  {result.same_sector
                    ? <><CheckCircle2 size={13} color="#10b981" /><span style={{ color: "#10b981" }}>Same sector</span></>
                    : <><XCircle size={13} color="#f43f5e" /><span style={{ color: "#f43f5e" }}>Different sectors</span></>
                  }
                </div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  ML Shared Focus:{" "}
                  <span style={{ color: result.ml_metrics?.themes?.shared?.length ? "var(--cyan)" : "var(--text-dim)" }}>
                    {result.ml_metrics?.themes?.shared?.length > 0 ? result.ml_metrics.themes.shared.join(", ") : "None"}
                  </span>
                </div>
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

          </div>{/* ← end of comparison view div */}

          {/* Download button */}
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
            <button onClick={downloadReport} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "10px 20px", borderRadius: 8,
              background: "linear-gradient(135deg, var(--cyan-dim), #0e7490)",
              border: "none", color: "#fff",
              fontFamily: "Syne", fontWeight: 700,
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