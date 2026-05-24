import { useNavigate } from "react-router-dom";
import { ExternalLink } from "lucide-react";

export default function PolicyCard({ policy, delay = 1, selectable, selected, onSelect }) {
  const nav = useNavigate();

  // First letter of policy title
  const letter = policy.title ? policy.title.charAt(0).toUpperCase() : "P";

  // Accent and Selected states styling
  const isSelected = selected;
  const cardBorder = isSelected ? "1px solid var(--cyan)" : "1px solid var(--border)";
  const cardBg = isSelected ? "var(--bg-hover)" : "var(--bg-card)";

  // Standard tags array: extract up to 3 tags
  const tagsToShow = policy.tags && Array.isArray(policy.tags) && policy.tags.length > 0
    ? policy.tags.slice(0, 3)
    : [policy.sector, policy.region].filter(Boolean);

  return (
    <div 
      className={`policy-card-custom fade-up fade-up-${delay}`}
      onClick={() => selectable ? onSelect?.(policy) : nav(`/policies/${policy.id}`)}
      style={{
        padding: "20px 20px 16px 20px",
        cursor: "pointer",
        borderRadius: "8px",
        border: cardBorder,
        background: cardBg,
        display: "flex",
        flexDirection: "column",
        minHeight: "250px",
        boxShadow: isSelected ? "0 2px 8px rgba(92,158,46,0.08)" : "none",
        transition: "border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease",
      }}
    >
      
      {/* ── ROW 1: Avatar + Title + Source badge ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        
        {/* Left: Avatar square */}
        <div style={{ display: "flex", gap: 10, flex: 1, alignItems: "flex-start" }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: "6px",
            background: "var(--bg-hover)",
            border: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "14px",
            fontWeight: 600,
            color: "var(--text-muted)",
            flexShrink: 0
          }}>
            {letter}
          </div>

          {/* Center-right: Title + Country */}
          <div style={{ display: "flex", flexDirection: "column", gap: 2, flex: 1 }}>
            <div style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "14px",
              fontWeight: 500,
              color: "var(--text-main)",
              lineHeight: 1.35,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden"
            }}>
              {policy.title}
            </div>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "10px",
              color: "var(--text-dim)",
              letterSpacing: "0.06em",
              textTransform: "uppercase"
            }}>
              {policy.country || "UNKNOWN"}
            </div>
          </div>
        </div>

        {/* Far right: source badge */}
        <div style={{ display: "flex", alignItems: "center", flexShrink: 0, marginTop: 3 }}>
          <div style={{
            width: 5,
            height: 5,
            borderRadius: "50%",
            background: "#5c9e2e",
            marginRight: 6
          }} />
          <span style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "9px",
            color: "#5c9e2e",
            letterSpacing: "0.08em",
            fontWeight: 500,
            textTransform: "uppercase"
          }}>
            {policy.sector || "GENERAL"}
          </span>
        </div>

      </div>

      {/* ── ROW 2: Description ── */}
      <div style={{
        fontFamily: "'DM Sans', sans-serif",
        fontSize: "13px",
        color: "var(--text-muted)",
        lineHeight: 1.55,
        marginTop: "12px",
        display: "-webkit-box",
        WebkitLineClamp: 3,
        WebkitBoxOrient: "vertical",
        overflow: "hidden",
        fontWeight: 400
      }}>
        {policy.content || "No detailed description provided for this policy framework."}
      </div>

      {/* ── ROW 3: Location + Year pills ── */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: "14px" }}>
        
        {/* Location pill */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 5,
          border: "1px solid var(--border)",
          borderRadius: "20px",
          padding: "3px 10px",
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: "10px",
          color: "var(--text-muted)",
          letterSpacing: "0.04em",
          textTransform: "uppercase"
        }}>
          <span style={{
            width: 4,
            height: 4,
            borderRadius: "50%",
            background: "var(--text-dim)",
            display: "inline-block"
          }} />
          {policy.country || "GLOBAL"}
        </div>

        {/* Year pill */}
        {policy.year && (
          <div style={{
            border: "1px solid var(--border)",
            borderRadius: "20px",
            padding: "3px 10px",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "10px",
            color: "var(--text-muted)",
            letterSpacing: "0.04em",
            textTransform: "uppercase"
          }}>
            {policy.year}
          </div>
        )}

      </div>

      {/* ── ROW 4: Tags ── */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
        {tagsToShow.map((tag, idx) => (
          <div key={idx} className="policy-card-tag" style={{
            borderRadius: "4px",
            padding: "3px 8px",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "10px",
            letterSpacing: "0.05em",
            textTransform: "uppercase"
          }}>
            {tag}
          </div>
        ))}
      </div>

      {/* ── ROW 5: VIEW POLICY link ── */}
      {!selectable && (
        <div style={{
          marginTop: "16px",
          borderTop: "1px solid var(--border)",
          paddingTop: "12px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}>
          <span className="view-policy-text" style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "11px",
            color: "var(--text-dim)",
            letterSpacing: "0.08em",
            transition: "color 0.15s ease"
          }}>
            VIEW POLICY
          </span>
          <ExternalLink className="view-policy-arrow" size={11} style={{
            color: "var(--text-dim)",
            transition: "color 0.15s ease"
          }} />
        </div>
      )}

    </div>
  );
}