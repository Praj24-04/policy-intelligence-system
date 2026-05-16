import { Link, useNavigate } from "react-router-dom";
import { Globe2, Moon, Sun } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export default function TopNavbar() {
  const { theme, toggleTheme } = useTheme();
  const nav = useNavigate();

  const navStyle = {
    textDecoration: "none",
    color: "var(--text-main)",
    fontSize: 14,
    fontWeight: 500,
  };

  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "16px 48px",
      background: "var(--bg-base)",
      borderBottom: "1px solid var(--border)",
      position: "sticky",
      top: 0,
      zIndex: 50
    }}>
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: "var(--cyan)",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <Globe2 size={16} color="#000" />
        </div>
        <div style={{ fontFamily: "Syne", fontWeight: 800, fontSize: 18, color: "var(--text-main)", letterSpacing: "-0.5px" }}>
          PolicyIQ
        </div>
      </div>

      {/* Nav Links */}
      <nav style={{ display: "flex", gap: 32 }}>
        <Link to="/" style={navStyle}>Home</Link>
        <Link to="/policies" onClick={(e) => { e.preventDefault(); nav("/login"); }} style={navStyle}>Policies</Link>
        <Link to="/compare" onClick={(e) => { e.preventDefault(); nav("/login"); }} style={navStyle}>Compare</Link>
        <Link to="/analytics" onClick={(e) => { e.preventDefault(); nav("/login"); }} style={navStyle}>Analytics</Link>
        <Link to="/recommend" onClick={(e) => { e.preventDefault(); nav("/login"); }} style={navStyle}>Recommender</Link>
        <Link to="/generate" onClick={(e) => { e.preventDefault(); nav("/login"); }} style={navStyle}>Generate</Link>
      </nav>

      {/* Actions */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <button onClick={toggleTheme} style={{
          background: "transparent", border: "none", cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "var(--text-muted)"
        }}>
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button 
          onClick={() => nav("/login")}
          style={{
            background: "var(--bg-hover)",
            border: "1px solid var(--border)",
            color: "var(--text-main)",
            padding: "8px 16px",
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.2s"
          }}
        >
          Sign In
        </button>
      </div>
    </header>
  );
}
