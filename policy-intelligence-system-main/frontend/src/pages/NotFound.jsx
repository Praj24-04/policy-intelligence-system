import { useNavigate } from "react-router-dom";
import { Globe2 } from "lucide-react";

export default function NotFound() {
  const nav = useNavigate();
  return (
    <div style={{
      minHeight: "100vh", display: "flex",
      flexDirection: "column", alignItems: "center",
      justifyContent: "center", background: "var(--bg-deep)"
    }}>
      <Globe2 size={48} color="var(--text-dim)" style={{ marginBottom: 24 }} />
      <div style={{
        fontFamily: "Syne", fontSize: 64, fontWeight: 800,
        color: "var(--text-dim)", marginBottom: 8
      }}>
        404
      </div>
      <div style={{
        fontFamily: "Syne", fontSize: 18,
        color: "var(--text-muted)", marginBottom: 24
      }}>
        Page not found
      </div>
      <button onClick={() => nav("/")} style={{
        padding: "10px 24px", borderRadius: 8,
        background: "rgba(34,211,238,0.1)",
        border: "1px solid rgba(34,211,238,0.3)",
        color: "var(--cyan)", fontSize: 13,
        cursor: "pointer", fontFamily: "JetBrains Mono"
      }}>
        ← Back to Dashboard
      </button>
    </div>
  );
}