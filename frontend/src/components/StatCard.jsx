export default function StatCard({ label, value, sub, accent = "cyan", delay = 0 }) {
  const colors = {
    cyan:  { bg: "var(--bg-card)", border: "var(--border)", text: "var(--cyan)" },
    amber: { bg: "var(--bg-card)", border: "var(--border)", text: "var(--cyan)" },
    green: { bg: "var(--bg-card)", border: "var(--border)", text: "var(--cyan)" },
    indigo:{ bg: "var(--bg-card)", border: "var(--border)", text: "var(--cyan)" },
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