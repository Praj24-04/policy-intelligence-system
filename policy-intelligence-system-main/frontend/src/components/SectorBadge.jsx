export default function SectorBadge({ sector, size = "sm" }) {
  const map = {
    "AI Governance": "pill-ai",
    "Cybersecurity":  "pill-cyber",
    "Data Privacy":   "pill-priv",
  };
  const pad = size === "sm" ? "2px 9px" : "4px 12px";
  const fs  = size === "sm" ? 11 : 12;

  return (
    <span className={map[sector] || "pill-ai"} style={{
      padding: pad, borderRadius: 20,
      fontSize: fs, fontWeight: 500,
      fontFamily: "DM Sans", whiteSpace: "nowrap",
      display: "inline-block",
    }}>
      {sector}
    </span>
  );
}