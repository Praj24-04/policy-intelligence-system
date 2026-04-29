import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchPolicy } from "../services/api";
import SectorBadge from "../components/SectorBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import { ArrowLeft, ExternalLink, MapPin, Calendar } from "lucide-react";

export default function PolicyDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const [policy, setPolicy] = useState(null);

  useEffect(() => { fetchPolicy(id).then(setPolicy); }, [id]);

  if (!policy) return <LoadingSpinner label="Loading policy..." />;

  return (
    <div style={{ padding: "28px 32px", maxWidth: 800 }}>
      <button onClick={() => nav(-1)} style={{
        display: "flex", alignItems: "center", gap: 6, marginBottom: 24,
        background: "none", border: "none", color: "var(--text-muted)",
        cursor: "pointer", fontSize: 13,
      }}>
        <ArrowLeft size={14} /> Back to Library
      </button>

      <div className="card fade-up" style={{ padding: "28px 32px" }}>
        <div style={{ marginBottom: 16 }}>
          <SectorBadge sector={policy.sector} size="md" />
        </div>

        <h1 style={{ fontFamily: "Syne", fontSize: 22, fontWeight: 800, color: "var(--text-main)", lineHeight: 1.3, marginBottom: 16 }}>
          {policy.title}
        </h1>

        <div style={{ display: "flex", gap: 20, marginBottom: 24, flexWrap: "wrap" }}>
          {[
            { icon: MapPin,   val: policy.country },
            { icon: Calendar, val: policy.year ?? "N/A" },
          ].map(({ icon: Icon, val }, i) => (
            <span key={i} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--text-muted)" }}>
              <Icon size={13} /> {val}
            </span>
          ))}
          <span style={{
            fontSize: 12, padding: "2px 10px", borderRadius: 4,
            background: policy.status === "Active" ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
            color: policy.status === "Active" ? "#10b981" : "#f59e0b",
            border: `1px solid ${policy.status === "Active" ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)"}`,
          }}>
            {policy.status}
          </span>
          <span style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
            v{policy.version}
          </span>
        </div>

        {/* Policy Content */}
        <div style={{ background: "var(--bg-hover)", border: "1px solid var(--border)", borderRadius: 10, padding: "20px 22px", marginBottom: 20 }}>
          <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", letterSpacing: "0.1em", marginBottom: 10 }}>
            POLICY CONTENT
          </div>
          <p style={{ color: "var(--text-main)", lineHeight: 1.75, fontSize: 14 }}>
            {policy.content}
          </p>
        </div>

        {/* Tags */}
        {policy.tags?.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", letterSpacing: "0.1em", marginBottom: 8 }}>
              KEY THEMES
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {policy.tags.map(t => (
                <span key={t} style={{
                  fontSize: 12, padding: "4px 10px", borderRadius: 6,
                  background: "var(--bg-card)", color: "var(--text-muted)",
                  border: "1px solid var(--border)", fontFamily: "JetBrains Mono",
                }}>
                  #{t}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ── Penalty Fines — Auto Extracted ── */}
        {policy.penalty_fines?.has_fines && (
          <div style={{
            background: "rgba(244,63,94,0.05)",
            border: "1px solid rgba(244,63,94,0.2)",
            borderRadius: 10, padding: "18px 22px", marginBottom: 20
          }}>
            <div style={{
              fontSize: 11, color: "#f43f5e",
              fontFamily: "JetBrains Mono",
              letterSpacing: "0.1em", marginBottom: 14
            }}>
              ⚖ PENALTY & ENFORCEMENT — AUTO EXTRACTED
            </div>

            {/* Summary */}
            <div style={{
              fontSize: 14, fontFamily: "Syne", fontWeight: 700,
              color: "#f43f5e", marginBottom: 14
            }}>
              {policy.penalty_fines.summary}
            </div>

            {/* Monetary Fines */}
            {policy.penalty_fines.monetary_fines?.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 8 }}>
                  MONETARY PENALTIES
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {policy.penalty_fines.monetary_fines.map((f, i) => (
                    <div key={i} style={{
                      padding: "8px 14px", borderRadius: 8,
                      background: "rgba(244,63,94,0.08)",
                      border: "1px solid rgba(244,63,94,0.2)",
                    }}>
                      <div style={{ fontSize: 16, fontFamily: "Syne", fontWeight: 800, color: "#f43f5e" }}>
                        {f.amount}
                      </div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
                        {f.currency}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Percentage Fines */}
            {policy.penalty_fines.percentage_fines?.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginBottom: 8 }}>
                  REVENUE-BASED PENALTIES
                </div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {policy.penalty_fines.percentage_fines.map((f, i) => (
                    <span key={i} style={{
                      padding: "6px 14px", borderRadius: 8,
                      background: "rgba(245,158,11,0.1)",
                      border: "1px solid rgba(245,158,11,0.2)",
                      color: "#f59e0b", fontFamily: "Syne",
                      fontWeight: 700, fontSize: 15
                    }}>
                      {f.percentage} of revenue
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Imprisonment */}
            {policy.penalty_fines.imprisonment && (
              <div style={{
                padding: "8px 14px", borderRadius: 8,
                background: "rgba(99,102,241,0.08)",
                border: "1px solid rgba(99,102,241,0.2)",
                fontSize: 13, color: "#a5b4fc"
              }}>
                ⚠ {policy.penalty_fines.imprisonment}
              </div>
            )}
          </div>
        )}

        {/* NER Countries */}
        {policy.extracted_countries?.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", letterSpacing: "0.1em", marginBottom: 8 }}>
              NLP · DETECTED ENTITIES
            </div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {policy.extracted_countries.map(c => (
                <span key={c} style={{
                  fontSize: 11, padding: "3px 9px", borderRadius: 4,
                  background: "rgba(34,211,238,0.07)", color: "var(--cyan)",
                  border: "1px solid rgba(34,211,238,0.15)", fontFamily: "JetBrains Mono",
                }}>
                  {c}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Source */}
        {policy.source_url && (
          <a href={policy.source_url} target="_blank" rel="noreferrer"
            style={{
              display: "inline-flex", alignItems: "center", gap: 6,
              fontSize: 12, color: "var(--cyan)", textDecoration: "none",
              border: "1px solid rgba(34,211,238,0.2)", borderRadius: 8,
              padding: "8px 14px", background: "rgba(34,211,238,0.06)",
            }}>
            <ExternalLink size={12} /> View Official Source
          </a>
        )}
      </div>
    </div>
  );
}