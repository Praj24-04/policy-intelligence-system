import { useNavigate } from "react-router-dom";
import { MapPin, Calendar, ExternalLink, Tag } from "lucide-react";
import SectorBadge from "./SectorBadge";

export default function PolicyCard({ policy, delay = 1, selectable, selected, onSelect }) {
  const nav = useNavigate();

  return (
    <div className={`card fade-up fade-up-${delay}`}
      onClick={() => selectable ? onSelect?.(policy) : nav(`/policies/${policy.id}`)}
      style={{
        padding: "18px 20px", cursor: "pointer",
        borderColor: selected ? "var(--cyan)" : undefined,
        background: selected ? "rgba(34,211,238,0.05)" : undefined,
      }}>
      {/* Top row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 10 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", lineHeight: 1.35, marginBottom: 6 }}>
            {policy.title}
          </div>
          <SectorBadge sector={policy.sector} />
        </div>
        {!selectable && (
          <ExternalLink size={14} color="var(--text-dim)" style={{ flexShrink: 0, marginTop: 2 }} />
        )}
      </div>

      {/* Meta row */}
      <div style={{ display: "flex", gap: 16, marginBottom: 10 }}>
        <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--text-muted)" }}>
          <MapPin size={11} /> {policy.country}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--text-muted)" }}>
          <Calendar size={11} /> {policy.year ?? "—"}
        </span>
        <span style={{
          fontSize: 11, padding: "1px 7px", borderRadius: 4,
          background: policy.status === "Active" ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
          color: policy.status === "Active" ? "#10b981" : "#f59e0b",
          border: `1px solid ${policy.status === "Active" ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)"}`,
        }}>
          {policy.status}
        </span>
      </div>

      {/* Tags */}
      {policy.tags?.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
          {policy.tags.slice(0, 4).map(t => (
            <span key={t} style={{
              fontSize: 10, padding: "2px 7px", borderRadius: 4,
              background: "var(--bg-hover)", color: "var(--text-muted)",
              border: "1px solid var(--border)", fontFamily: "JetBrains Mono",
            }}>
              {t}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}