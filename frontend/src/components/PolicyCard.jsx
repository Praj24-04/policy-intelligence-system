import { useNavigate } from "react-router-dom";
import { MapPin, Calendar, ArrowUpRight } from "lucide-react";

export default function PolicyCard({ policy, delay = 1, selectable, selected, onSelect }) {
  const nav = useNavigate();

  const letter = policy.country && policy.country !== "Unknown" 
    ? policy.country.charAt(0).toUpperCase() 
    : "P";

  return (
    <div className={`card fade-up fade-up-${delay}`}
      onClick={() => selectable ? onSelect?.(policy) : nav(`/policies/${policy.id}`)}
      style={{
        padding: "20px 24px", cursor: "pointer",
        borderColor: selected ? "var(--cyan)" : "var(--border)",
        background: selected ? "rgba(34,211,238,0.05)" : "var(--bg-card)",
        display: "flex",
        flexDirection: "column",
        minHeight: "220px",
      }}>
      
      {/* Top section */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
        <div style={{ 
          width: 36, height: 36, background: "var(--bg-hover)", borderRadius: 6, 
          display: "flex", alignItems: "center", justifyContent: "center", 
          fontWeight: 700, fontSize: 16, color: "var(--text-main)", flexShrink: 0,
          border: "1px solid var(--border)"
        }}>
          {letter}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ 
            fontFamily: "Inter", fontWeight: 700, fontSize: 16, color: "var(--text-main)", 
            lineHeight: 1.3, marginBottom: 4 
          }}>
            {policy.title}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
          <div style={{ width: 6, height: 6, background: "var(--cyan)", borderRadius: 1 }} />
          <span style={{ 
            fontSize: 10, color: "var(--text-muted)", fontFamily: "JetBrains Mono", 
            textTransform: "uppercase", fontWeight: 600, letterSpacing: "0.5px"
          }}>
            {policy.sector}
          </span>
        </div>
      </div>

      {/* Middle section - truncated description */}
      <div style={{ 
        fontSize: 13, color: "var(--text-muted)", marginTop: 16, marginBottom: 20, 
        display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", 
        overflow: "hidden", lineHeight: 1.6
      }}>
        {policy.content || "No detailed description provided for this policy framework."}
      </div>

      {/* Bottom section */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: "auto" }}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <div style={{ 
            display: "flex", alignItems: "center", gap: 4, padding: "4px 8px", 
            background: "var(--bg-hover)", borderRadius: 4, fontSize: 10, 
            color: "var(--text-muted)", fontFamily: "JetBrains Mono",
            border: "1px solid var(--border)"
          }}>
            <MapPin size={10} /> {policy.country}
          </div>
          {policy.year && (
             <div style={{ 
               display: "flex", alignItems: "center", gap: 4, padding: "4px 8px", 
               background: "var(--bg-hover)", borderRadius: 4, fontSize: 10, 
               color: "var(--text-muted)", fontFamily: "JetBrains Mono",
               border: "1px solid var(--border)"
             }}>
               <Calendar size={10} /> {policy.year}
             </div>
          )}
        </div>
        
        {!selectable && (
          <div style={{ 
            display: "flex", alignItems: "center", gap: 4, fontSize: 11, 
            color: "var(--text-muted)", fontFamily: "JetBrains Mono", fontWeight: 600,
            transition: "color 0.2s"
          }}>
            VIEW POLICY <ArrowUpRight size={14} />
          </div>
        )}
      </div>
    </div>
  );
}