export default function StatCard({ label, value, sub, accent = "cyan", delay = 0 }) {
  const colors = {
    cyan:  { bg: "rgba(34,211,238,0.07)",  border: "rgba(34,211,238,0.2)",  text: "var(--cyan)"  },
    amber: { bg: "rgba(245,158,11,0.07)",  border: "rgba(245,158,11,0.2)",  text: "#f59e0b" },
    green: { bg: "rgba(16,185,129,0.07)",  border: "rgba(16,185,129,0.2)",  text: "#10b981" },
    indigo:{ bg: "rgba(99,102,241,0.07)",  border: "rgba(99,102,241,0.2)",  text: "#a5b4fc" },
  };
  const c = colors[accent] || colors.cyan;

  return (
    <div className={`fade-up fade-up-${delay}`} style={{
      background: c.bg, border: `1px solid ${c.border}`,
      borderRadius: 12, padding: "20px 22px",
    }}>
      <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono", letterSpacing: "0.08em", marginBottom: 8 }}>
        {label.toUpperCase()}
      </div>
      <div style={{ fontSize: 36, fontFamily: "Syne", fontWeight: 800, color: c.text, lineHeight: 1 }}>
        {value ?? "—"}
      </div>
      {sub && <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}>{sub}</div>}
    </div>
  );
}