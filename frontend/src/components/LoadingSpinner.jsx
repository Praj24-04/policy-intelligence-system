export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14, padding: 60 }}>
      <div style={{
        width: 36, height: 36, borderRadius: "50%",
        border: "2px solid var(--border)",
        borderTop: "2px solid var(--cyan)",
        animation: "spin 0.8s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <span style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>{label}</span>
    </div>
  );
}