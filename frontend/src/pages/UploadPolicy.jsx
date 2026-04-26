import { useState } from "react";
import { Upload, FileText, Sparkles, CheckCircle2, Globe2 } from "lucide-react";
import SectorBadge from "../components/SectorBadge";
import LoadingSpinner from "../components/LoadingSpinner";

const MaturityColor = {
  nascent:    { bg: "rgba(244,63,94,0.1)",  border: "rgba(244,63,94,0.2)",  text: "#f43f5e" },
  emerging:   { bg: "rgba(245,158,11,0.1)", border: "rgba(245,158,11,0.2)", text: "#f59e0b" },
  developing: { bg: "rgba(99,102,241,0.1)", border: "rgba(99,102,241,0.2)", text: "#a5b4fc" },
  advanced:   { bg: "rgba(16,185,129,0.1)", border: "rgba(16,185,129,0.2)", text: "#10b981" },
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
    setFile(f);
    setError(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/upload/pdf", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "28px 32px" }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div style={{ width: 3, height: 22, background: "#f59e0b", borderRadius: 2 }} />
          <h1 style={{ fontFamily: "Syne", fontSize: 22, fontWeight: 800, color: "var(--text-main)" }}>
            Upload Policy Document
          </h1>
          <div style={{
            display: "flex", alignItems: "center", gap: 6, marginLeft: 8,
            padding: "3px 10px", borderRadius: 20,
            background: "rgba(245,158,11,0.1)",
            border: "1px solid rgba(245,158,11,0.2)"
          }}>
            <Sparkles size={11} color="#f59e0b" />
            <span style={{ fontSize: 11, color: "#f59e0b", fontFamily: "JetBrains Mono" }}>
              PDF ANALYSIS
            </span>
          </div>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, paddingLeft: 13 }}>
          Upload any policy PDF to get ML-powered recommendations and similarity analysis
        </p>
      </div>

      {/* Upload Zone */}
      <div className="card fade-up fade-up-1"
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
        style={{
          padding: 48, textAlign: "center", marginBottom: 24,
          borderColor: dragging ? "var(--cyan)" : file ? "#10b981" : "var(--border)",
          background: dragging ? "rgba(34,211,238,0.03)" : "var(--bg-card)",
          cursor: "pointer", transition: "all 0.2s",
        }}
        onClick={() => document.getElementById("pdf-input").click()}>

        <input id="pdf-input" type="file" accept=".pdf"
          style={{ display: "none" }}
          onChange={e => handleFile(e.target.files[0])} />

        {file ? (
          <>
            <FileText size={40} color="#10b981" style={{ margin: "0 auto 16px", display: "block" }} />
            <div style={{ fontFamily: "Syne", fontSize: 16, color: "#10b981", marginBottom: 4 }}>
              {file.name}
            </div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {(file.size / 1024).toFixed(1)} KB · Click to change
            </div>
          </>
        ) : (
          <>
            <Upload size={40} color="var(--text-dim)" style={{ margin: "0 auto 16px", display: "block" }} />
            <div style={{ fontFamily: "Syne", fontSize: 16, color: "var(--text-muted)", marginBottom: 4 }}>
              Drop PDF here or click to browse
            </div>
            <div style={{ fontSize: 12, color: "var(--text-dim)" }}>
              Max 10MB · PDF only
            </div>
          </>
        )}
      </div>

      {error && (
        <div style={{
          padding: "12px 16px", borderRadius: 8, marginBottom: 16,
          background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.2)",
          color: "#f43f5e", fontSize: 13
        }}>
          {error}
        </div>
      )}

      {file && !loading && (
        <button onClick={handleUpload} style={{
          width: "100%", padding: "14px", borderRadius: 10,
          background: "linear-gradient(135deg, #f59e0b, #d97706)",
          border: "none", color: "#000", fontFamily: "Syne",
          fontWeight: 700, fontSize: 15, cursor: "pointer",
          marginBottom: 24,
        }}>
          Analyze Policy Document
        </button>
      )}

      {loading && <LoadingSpinner label="Extracting and analyzing PDF..." />}

      {/* Results */}
      {result && !loading && (
        <div className="fade-up">
          {/* Document Info */}
          <div className="card" style={{
            padding: "20px 24px", marginBottom: 16,
            borderColor: "rgba(245,158,11,0.3)",
            background: "rgba(245,158,11,0.03)"
          }}>
            <div style={{ fontSize: 11, color: "#f59e0b", fontFamily: "JetBrains Mono", marginBottom: 8 }}>
              DOCUMENT ANALYZED
            </div>
            <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 16, color: "var(--text-main)", marginBottom: 12 }}>
              {result.title}
            </div>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 12 }}>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                📄 {result.word_count} words
              </span>
              {result.year && (
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  📅 {result.year}
                </span>
              )}
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                🌍 {result.extracted_countries?.length || 0} countries detected
              </span>
              <span style={{
                fontSize: 11, padding: "2px 8px", borderRadius: 4,
                background: "rgba(34,211,238,0.07)", color: "var(--cyan)",
                border: "1px solid rgba(34,211,238,0.15)", fontFamily: "JetBrains Mono"
              }}>
                Sector: {result.detected_sector || "Auto-detected"}
              </span>
            </div>

            {/* Tags */}
            {result.tags?.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
                {result.tags.map(t => (
                  <span key={t} style={{
                    fontSize: 11, padding: "2px 8px", borderRadius: 4,
                    background: "var(--bg-hover)", color: "var(--text-muted)",
                    border: "1px solid var(--border)", fontFamily: "JetBrains Mono"
                  }}>
                    #{t}
                  </span>
                ))}
              </div>
            )}

            {/* Content Preview */}
            <div style={{
              background: "var(--bg-hover)", border: "1px solid var(--border)",
              borderRadius: 8, padding: "12px 14px"
            }}>
              <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 6 }}>
                CONTENT PREVIEW
              </div>
              <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.6 }}>
                {result.content_preview}
              </p>
            </div>
          </div>

          {/* Similar Policies */}
          {result.similar_policies?.length > 0 && (
            <div className="card" style={{ padding: "20px 24px", marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 12 }}>
                MOST SIMILAR POLICIES IN DATABASE (COSINE SIMILARITY)
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {result.similar_policies.map((p, i) => (
                  <div key={i} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "10px 14px", borderRadius: 8,
                    background: "var(--bg-hover)", border: "1px solid var(--border)"
                  }}>
                    <div>
                      <div style={{ fontSize: 13, color: "var(--text-main)", fontWeight: 600, marginBottom: 2 }}>
                        {p.title}
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                        {p.country} · {p.sector} · {p.year}
                      </div>
                    </div>
                    <div style={{
                      fontFamily: "JetBrains Mono", fontSize: 16,
                      fontWeight: 700,
                      color: p.similarity > 0.5 ? "#10b981" : p.similarity > 0.3 ? "#f59e0b" : "var(--cyan)"
                    }}>
                      {Math.round(p.similarity * 100)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 12 }}>
            ⚙ {result.ml_method}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {result.recommendations.map((rec, i) => {
              const mc = MaturityColor[rec.regulatory_maturity] || MaturityColor.developing;
              return (
                <div key={rec.country} className={`card fade-up fade-up-${i + 1}`}
                  style={{ padding: "18px 22px" }}>
                  <div style={{
                    display: "flex", justifyContent: "space-between",
                    alignItems: "flex-start", marginBottom: 12
                  }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                        <span style={{ fontFamily: "Syne", fontWeight: 800, fontSize: 16, color: "var(--text-main)" }}>
                          #{i + 1} {rec.country}
                        </span>
                        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>· {rec.region}</span>
                        {!rec.already_has_sector && (
                          <span style={{
                            fontSize: 10, padding: "1px 7px", borderRadius: 4,
                            background: "rgba(244,63,94,0.08)", color: "#f43f5e",
                            border: "1px solid rgba(244,63,94,0.2)"
                          }}>Missing sector</span>
                        )}
                      </div>
                      <span style={{
                        fontSize: 11, padding: "2px 8px", borderRadius: 4,
                        background: mc.bg, color: mc.text,
                        border: `1px solid ${mc.border}`, fontFamily: "JetBrains Mono"
                      }}>
                        {rec.regulatory_maturity} maturity
                      </span>
                    </div>
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

                  <div style={{ height: 3, background: "var(--border)", borderRadius: 2, marginBottom: 12 }}>
                    <div style={{
                      height: "100%", borderRadius: 2,
                      width: `${rec.need_score * 100}%`,
                      background: rec.need_score > 0.6 ? "#f43f5e" : rec.need_score > 0.4 ? "#f59e0b" : "#10b981",
                      transition: "width 0.8s ease"
                    }} />
                  </div>

                  <div style={{
                    background: "var(--bg-hover)", border: "1px solid var(--border)",
                    borderRadius: 8, padding: "10px 14px", marginBottom: 12
                  }}>
                    <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 6 }}>
                      WHY THIS COUNTRY
                    </div>
                    <p style={{ fontSize: 12, color: "var(--text-main)", lineHeight: 1.65 }}>
                      {rec.reasoning}
                    </p>
                  </div>

                  <div>
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
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}