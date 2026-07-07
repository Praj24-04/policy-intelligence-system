import { useState } from "react";
import { Upload, FileText, Sparkles, CheckCircle2 } from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner";
import { getToken, BASE, clearApiCache } from "../services/api";

const MaturityColor = {
  nascent:    { bg: "rgba(244,63,94,0.08)",  border: "rgba(244,63,94,0.2)",   text: "#f43f5e" },
  emerging:   { bg: "rgba(245,158,11,0.08)", border: "rgba(245,158,11,0.2)",  text: "#f59e0b" },
  developing: { bg: "rgba(92,158,46,0.08)",  border: "rgba(92,158,46,0.2)",   text: "#5c9e2e" },
  advanced:   { bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.2)",  text: "#10b981" },
};

export default function UploadPolicy() {
  const [file,     setFile]     = useState(null);
  const [result,   setResult]   = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (f) => {
    if (!f || !f.name.endsWith(".pdf")) {
      setError("Only PDF files are accepted.");
      return;
    }
    setError(null);
    setFile(f);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = getToken();
      const res = await fetch(`${BASE}/upload/pdf`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();
      if (res.status === 401) throw new Error("Session expired. Please log in again.");
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      clearApiCache();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Inline section label matching Dashboard/Recommend style
  const SectionLabel = ({ text }) => (
    <div style={{
      display: "inline-block",
      background: "rgba(92, 158, 46, 0.08)",
      border: "1px solid rgba(92, 158, 46, 0.15)",
      borderRadius: "4px",
      padding: "4px 10px",
      marginBottom: "8px"
    }}>
      <span style={{
        fontFamily: "DM Sans",
        fontWeight: 600,
        fontSize: "13px",
        color: "#5c9e2e",
        letterSpacing: "0.02em"
      }}>
        {text}
      </span>
    </div>
  );

  // Mono section divider matching Compare page
  const SectionDivider = ({ label }) => (
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px", marginTop: "28px" }}>
      <div style={{ width: "20px", height: "1px", background: "var(--border)" }} />
      <span style={{
        fontSize: "11px",
        fontFamily: "JetBrains Mono",
        color: "var(--text-muted)",
        letterSpacing: "0.12em",
        fontWeight: 500,
        textTransform: "uppercase",
        whiteSpace: "nowrap"
      }}>
        {label}
      </span>
      <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
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
        .upload-dropzone {
          background: var(--bg-card);
          border: 1.5px dashed var(--border);
          border-radius: 8px;
          padding: 56px 48px;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s ease;
          margin-bottom: 16px;
        }
        .upload-dropzone:hover {
          border-color: #5c9e2e;
          background: rgba(92, 158, 46, 0.02);
        }
        .upload-dropzone.dragging {
          border-color: #5c9e2e;
          background: rgba(92, 158, 46, 0.03);
        }
        .upload-dropzone.has-file {
          border-color: #5c9e2e;
          border-style: solid;
          background: rgba(92, 158, 46, 0.02);
        }
        .upload-btn-primary {
          width: 100%;
          height: 48px;
          background: #0a0a0a;
          color: #ffffff;
          border: none;
          border-radius: 6px;
          font-size: 15px;
          font-family: 'DM Sans', sans-serif;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: background 0.15s ease;
          margin-bottom: 24px;
        }
        .upload-btn-primary:hover {
          background: #222222;
        }
        [data-theme="dark"] .upload-btn-primary {
          background: #fafafa;
          color: #09090b;
        }
        [data-theme="dark"] .upload-btn-primary:hover {
          background: #e4e4e7;
        }
        .sim-policy-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border-radius: 6px;
          background: var(--bg-hover);
          border: 1px solid var(--border);
          transition: border-color 0.15s ease;
        }
        .sim-policy-row:hover {
          border-color: var(--border-lit);
        }
        .rec-card {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 22px 24px;
          transition: border-color 0.15s ease;
        }
        .rec-card:hover {
          border-color: var(--border-lit);
        }
      `}</style>

      <div style={{
        maxWidth: "1100px",
        margin: "0 auto",
        padding: "32px 40px",
        width: "100%"
      }}>

        {/* ── Page Header ── */}
        <div style={{ marginBottom: "32px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--cyan)" }} />
                <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.1em" }}>
                  DISCOVER / INGESTION
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
                Analyze custom{" "}
                <span style={{ position: "relative", display: "inline-block", zIndex: 1 }}>
                  documents.
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
                Upload any policy PDF to get ML-powered recommendations and similarity analysis
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

        {/* ── Upload Dropzone ── */}
        <div
          className={`upload-dropzone${dragging ? " dragging" : ""}${file ? " has-file" : ""}`}
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
          onClick={() => document.getElementById("pdf-input").click()}
        >
          <input
            id="pdf-input"
            type="file"
            accept=".pdf"
            style={{ display: "none" }}
            onChange={e => handleFile(e.target.files[0])}
          />

          {file ? (
            <>
              <FileText size={40} color="#5c9e2e" style={{ margin: "0 auto 16px", display: "block" }} />
              <div style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "16px",
                fontWeight: 600,
                color: "#5c9e2e",
                marginBottom: "4px"
              }}>
                {file.name}
              </div>
              <div style={{ fontSize: "13px", color: "var(--text-muted)", fontFamily: "DM Sans" }}>
                {(file.size / 1024).toFixed(1)} KB · Click or drop another to replace
              </div>
            </>
          ) : (
            <>
              <Upload size={40} color="var(--text-dim)" style={{ margin: "0 auto 16px", display: "block" }} />
              <div style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "16px",
                fontWeight: 600,
                color: "var(--text-muted)",
                marginBottom: "4px"
              }}>
                Drop PDF here or click to browse
              </div>
              <div style={{ fontSize: "13px", color: "var(--text-dim)", fontFamily: "DM Sans" }}>
                Max 10 MB · PDF format only
              </div>
            </>
          )}
        </div>

        {/* ── Error Banner ── */}
        {error && (
          <div style={{
            padding: "12px 16px",
            borderRadius: "6px",
            marginBottom: "16px",
            background: "rgba(244,63,94,0.06)",
            border: "1px solid rgba(244,63,94,0.18)",
            color: "#f43f5e",
            fontSize: "13px",
            fontFamily: "DM Sans"
          }}>
            {error}
          </div>
        )}

        {/* ── Analyze Button ── */}
        {file && !loading && (
          <button className="upload-btn-primary" onClick={handleUpload}>
            <Sparkles size={15} />
            Analyze Policy Document
          </button>
        )}

        {/* ── Loading State ── */}
        {loading && <LoadingSpinner label="Extracting text, computing embeddings, and running ML analysis..." />}

        {/* ── Results ── */}
        {result && !loading && (
          <div className="fade-up">

            {/* ── Document Metadata Card ── */}
            <SectionDivider label="Document Analysis" />
            <div style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "22px 28px",
              marginBottom: "20px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                <div>
                  <SectionLabel text="Ingested Document" />
                  <div style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontWeight: 700,
                    fontSize: "20px",
                    color: "var(--text-main)",
                    marginBottom: "12px"
                  }}>
                    {result.title}
                  </div>
                  <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", alignItems: "center" }}>
                    <span style={{ fontSize: "13px", color: "var(--text-muted)", fontFamily: "DM Sans" }}>
                      📄 <b>{result.word_count?.toLocaleString()}</b> words
                    </span>
                    {result.year && (
                      <span style={{ fontSize: "13px", color: "var(--text-muted)", fontFamily: "DM Sans" }}>
                        📅 <b>{result.year}</b>
                      </span>
                    )}
                    <span style={{ fontSize: "13px", color: "var(--text-muted)", fontFamily: "DM Sans" }}>
                      🌍 <b>{result.extracted_countries?.length || 0}</b> countries detected
                    </span>
                  </div>
                </div>
                <div style={{ flexShrink: 0 }}>
                  <span style={{
                    display: "block",
                    fontSize: "10px",
                    fontFamily: "JetBrains Mono",
                    color: "var(--text-muted)",
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    marginBottom: "4px"
                  }}>
                    Detected Sector
                  </span>
                  <span style={{
                    background: "var(--stat-bg)",
                    border: "1px solid var(--stat-border)",
                    borderRadius: "4px",
                    padding: "4px 10px",
                    fontSize: "12px",
                    fontFamily: "JetBrains Mono",
                    fontWeight: 600,
                    color: "var(--stat-label)"
                  }}>
                    {result.detected_sector || "Auto-detected"}
                  </span>
                </div>
              </div>

              {/* Tags */}
              {result.tags?.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "16px" }}>
                  {result.tags.map(t => (
                    <span key={t} style={{
                      fontSize: "11px",
                      padding: "3px 8px",
                      borderRadius: "4px",
                      background: "var(--bg-hover)",
                      color: "var(--text-muted)",
                      border: "1px solid var(--border)",
                      fontFamily: "JetBrains Mono"
                    }}>
                      #{t}
                    </span>
                  ))}
                </div>
              )}

              {/* Content Preview */}
              <div style={{
                background: "var(--bg-hover)",
                border: "1px solid var(--border)",
                borderRadius: "6px",
                padding: "12px 16px"
              }}>
                <div style={{
                  fontSize: "10px",
                  color: "var(--text-dim)",
                  fontFamily: "JetBrains Mono",
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  marginBottom: "8px"
                }}>
                  Content Preview
                </div>
                <p style={{ fontSize: "13px", color: "var(--text-muted)", lineHeight: 1.65, margin: 0, fontFamily: "DM Sans" }}>
                  {result.content_preview}
                </p>
              </div>
            </div>

            {/* ── Similar Policies ── */}
            {result.similar_policies?.length > 0 && (
              <>
                <SectionDivider label="Most Similar Policies in Database" />
                <div style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "22px 28px",
                  marginBottom: "20px"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                    <div>
                      <SectionLabel text="Cosine Similarity Match" />
                      <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                        Top matching frameworks from the policy database
                      </div>
                    </div>
                    <span style={{
                      background: "var(--bg-hover)",
                      border: "1px solid var(--border)",
                      borderRadius: "4px",
                      padding: "3px 8px",
                      fontSize: "10px",
                      color: "var(--text-muted)",
                      fontFamily: "JetBrains Mono"
                    }}>
                      {result.similar_policies.length} results
                    </span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {result.similar_policies.map((p, i) => (
                      <div key={i} className="sim-policy-row">
                        <div>
                          <div style={{ fontSize: "14px", color: "var(--text-main)", fontWeight: 600, fontFamily: "DM Sans", marginBottom: "3px" }}>
                            {p.title}
                          </div>
                          <div style={{ fontSize: "12px", color: "var(--text-muted)", fontFamily: "DM Sans" }}>
                            {p.country}{p.sector ? ` · ${p.sector}` : ""}{p.year ? ` · ${p.year}` : ""}
                          </div>
                        </div>
                        <div style={{
                          fontFamily: "JetBrains Mono",
                          fontSize: "17px",
                          fontWeight: 700,
                          color: p.similarity > 0.5 ? "#5c9e2e" : p.similarity > 0.3 ? "#f59e0b" : "var(--text-muted)",
                          flexShrink: 0,
                          marginLeft: "16px"
                        }}>
                          {Math.round(p.similarity * 100)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* ── ML Recommendations ── */}
            <SectionDivider label="Adoption Priority Recommendations" />

            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              marginBottom: "20px"
            }}>
              <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#5c9e2e" }} />
              <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.08em" }}>
                {result.ml_method}
              </span>
            </div>

            {/* Scoring Legend Card */}
            <div style={{
              background: "var(--bg-hover)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "16px 20px",
              marginBottom: "20px",
              display: "flex",
              flexDirection: "column",
              gap: "8px"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ width: "4px", height: "4px", borderRadius: "50%", background: "#5c9e2e" }} />
                <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600, letterSpacing: "0.08em" }}>
                  NEED INDEX METHODOLOGY & LEGEND
                </span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", margin: 0, lineHeight: "1.5", fontFamily: "DM Sans" }}>
                The Need Index (from <code style={{ fontFamily: "JetBrains Mono", color: "var(--cyan)" }}>0.000</code> to <code style={{ fontFamily: "JetBrains Mono", color: "var(--cyan)" }}>1.000</code>) is computed dynamically using our multi-factor scoring system:
              </p>
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                gap: "10px",
                marginTop: "6px"
              }}>
                {[
                  { name: "Sector Gap Severity (35%)", desc: "Absence of active legislation in primary sector." },
                  { name: "Statutory Infrastructure (25%)", desc: "Country's baseline regulatory maturity tier." },
                  { name: "Legislative Intent (20%)", desc: "Semantic alignment using Legal-BERT embeddings." },
                  { name: "Geopolitical Peer (12%)", desc: "Adoption velocity in adjacent regional markets." },
                  { name: "Developmental Tier (8%)", desc: "Socioeconomic and GDP tier alignment." }
                ].map((f, idx) => (
                  <div key={idx} style={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border)",
                    borderRadius: "6px",
                    padding: "8px 12px",
                    fontSize: "12px",
                    fontFamily: "DM Sans"
                  }}>
                    <div style={{ fontWeight: 600, color: "var(--text-main)", marginBottom: "4px" }}>
                      {f.name}
                    </div>
                    <span style={{ color: "var(--text-muted)", fontSize: "11px", display: "block", lineHeight: "1.3" }}>{f.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {result.recommendations.map((rec, i) => {
                const mc = MaturityColor[rec.regulatory_maturity] || MaturityColor.developing;
                const needPctVal = rec.need_score * 100;
                const needPct = needPctVal.toFixed(1);
                const needColor = rec.need_score > 0.6 ? "#f43f5e" : rec.need_score > 0.4 ? "#f59e0b" : "#5c9e2e";

                return (
                  <div key={rec.country} className={`rec-card fade-up fade-up-${Math.min(i + 1, 5)}`}>
                    {/* Card Header */}
                    <div style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: "16px"
                    }}>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                          <span style={{
                            fontFamily: "'DM Sans', sans-serif",
                            fontWeight: 700,
                            fontSize: "18px",
                            color: "var(--text-main)"
                          }}>
                            #{i + 1} {rec.country}
                          </span>
                          <span style={{ fontSize: "12px", color: "var(--text-muted)", fontFamily: "DM Sans" }}>
                            · {rec.region}
                          </span>
                          {!rec.already_has_sector && (
                            <span style={{
                              fontSize: "10px",
                              padding: "2px 8px",
                              borderRadius: "4px",
                              background: "rgba(244,63,94,0.06)",
                              color: "#f43f5e",
                              border: "1px solid rgba(244,63,94,0.18)",
                              fontFamily: "JetBrains Mono",
                              fontWeight: 600
                            }}>
                              Missing sector
                            </span>
                          )}
                        </div>
                        <span style={{
                          fontSize: "11px",
                          padding: "3px 8px",
                          borderRadius: "4px",
                          background: mc.bg,
                          color: mc.text,
                          border: `1px solid ${mc.border}`,
                          fontFamily: "JetBrains Mono",
                          fontWeight: 600
                        }}>
                          {rec.regulatory_maturity?.toUpperCase()} MATURITY
                        </span>
                      </div>
                      <div style={{ textAlign: "right", flexShrink: 0 }}>
                        <div style={{
                          fontSize: "10px",
                          color: "var(--text-muted)",
                          fontFamily: "JetBrains Mono",
                          letterSpacing: "0.08em",
                          textTransform: "uppercase",
                          marginBottom: "4px"
                        }}>
                          Need Index
                        </div>
                        <div style={{
                          fontFamily: "'DM Sans', sans-serif",
                          fontWeight: 700,
                          fontSize: "28px",
                          color: needColor,
                          lineHeight: 1
                        }}>
                          {rec.need_score.toFixed(3)}
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div style={{
                      height: "4px",
                      background: "var(--bg-hover)",
                      borderRadius: "2px",
                      marginBottom: "16px",
                      overflow: "hidden"
                    }}>
                      <div style={{
                        height: "100%",
                        width: `${needPct}%`,
                        background: needColor,
                        borderRadius: "2px",
                        transition: "width 0.8s ease"
                      }} />
                    </div>

                    {/* Why This Country */}
                    <div style={{
                      background: "var(--bg-hover)",
                      border: "1px solid var(--border)",
                      borderRadius: "6px",
                      padding: "12px 16px",
                      marginBottom: "16px"
                    }}>
                      <div style={{
                        fontSize: "10px",
                        color: "var(--text-dim)",
                        fontFamily: "JetBrains Mono",
                        letterSpacing: "0.08em",
                        textTransform: "uppercase",
                        marginBottom: "6px"
                      }}>
                        Why This Country
                      </div>
                      <p style={{ fontSize: "13px", color: "var(--text-main)", lineHeight: 1.65, margin: 0, fontFamily: "DM Sans" }}>
                        {rec.reasoning}
                      </p>
                    </div>

                    {/* Expected Benefits */}
                    <div>
                      <div style={{
                        fontSize: "10px",
                        color: "var(--text-dim)",
                        fontFamily: "JetBrains Mono",
                        letterSpacing: "0.08em",
                        textTransform: "uppercase",
                        marginBottom: "10px"
                      }}>
                        Expected Regulatory Benefits
                      </div>
                      <div style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gap: "8px"
                      }}>
                        {rec.expected_benefits.map((b, j) => (
                          <div key={j} style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
                            <CheckCircle2
                              size={14}
                              color="#5c9e2e"
                              style={{ flexShrink: 0, marginTop: "2px" }}
                            />
                            <span style={{
                              fontSize: "12px",
                              color: "var(--text-muted)",
                              lineHeight: 1.5,
                              fontFamily: "DM Sans"
                            }}>
                              {b}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}