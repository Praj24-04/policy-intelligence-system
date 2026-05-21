export default function StatCard({ label, value, sub, accent = "green", delay = 0 }) {
  return (
    <div className={`fade-up fade-up-${delay} stat-card-themed`} style={{
      borderTop: "2px solid var(--cyan)",
      borderLeft: "1px solid var(--stat-border)",
      borderRight: "1px solid var(--stat-border)",
      borderBottom: "1px solid var(--stat-border)",
      background: "var(--stat-bg)",
      borderRadius: "12px",
      padding: "16px 20px 14px",
      boxShadow: "0 1px 3px rgba(0,0,0,0.01)",
      display: "flex",
      flexDirection: "column",
      position: "relative",
      overflow: "hidden"
    }}>
      <div style={{ 
        display: "flex", 
        justifyContent: "space-between", 
        alignItems: "center",
        marginBottom: 2
      }}>
        <span style={{ 
          fontSize: "10px", 
          color: "var(--stat-label)", 
          fontFamily: "'JetBrains Mono', monospace", 
          letterSpacing: "0.08em", 
          fontWeight: 600 
        }}>
          {label.toUpperCase()}
        </span>
        {label.toLowerCase().includes("total") && (
          <span style={{
            width: 5,
            height: 5,
            borderRadius: "50%",
            background: "var(--cyan)",
            boxShadow: "0 0 8px var(--cyan)",
            animation: "pulse 2s ease-in-out infinite"
          }} />
        )}
      </div>
      
      <div style={{ 
        fontSize: "28px", 
        fontFamily: "'JetBrains Mono', monospace", 
        fontWeight: 600, 
        color: "var(--text-main)", 
        lineHeight: "1.1", 
        margin: "4px 0" 
      }}>
        {value ?? "—"}
      </div>
      
      {sub && (
        <div style={{ 
          fontSize: "11px", 
          color: "var(--stat-sub)", 
          marginTop: "2px", 
          fontWeight: 500 
        }}>
          {sub}
        </div>
      )}
    </div>
  );
}