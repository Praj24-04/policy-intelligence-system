import { NavLink } from "react-router-dom";
import { Moon, Sun, Globe2 } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export default function DashboardNavbar({ user }) {
  const { theme, toggleTheme } = useTheme();

  const userInitial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U";

  const links = [
    { to: "/", label: "Home" },
    { to: "/policies", label: "Database" },
    { to: "/compare", label: "Compare" },
    { to: "/analytics", label: "Analytics" },
  ];

  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "16px 32px",
      background: "var(--bg-base)",
      borderBottom: "1px solid var(--border)",
      flexShrink: 0
    }}>
      {/* Brand */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 30, height: 30, borderRadius: 6,
          background: "var(--text-main)",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "var(--bg-base)"
        }}>
          <Globe2 size={16} />
        </div>
        <div style={{ fontWeight: 700, fontSize: 16, color: "var(--text-main)", letterSpacing: "-0.5px" }}>
          PolicyIQ
        </div>
      </div>

      {/* Center Nav Links */}
      <nav style={{ display: "flex", gap: 32 }}>
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} style={({ isActive }) => ({
            textDecoration: "none",
            color: isActive ? "var(--text-main)" : "var(--text-muted)",
            fontSize: 14,
            fontWeight: 500,
            transition: "color 0.2s"
          })}>
            {l.label}
          </NavLink>
        ))}
      </nav>

      {/* Right Actions */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <button onClick={toggleTheme} style={{
          background: "transparent", border: "none", cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "var(--text-muted)"
        }}>
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div style={{
          width: 32, height: 32, borderRadius: 6,
          background: "#5c6bc0", // generic nice purple/blue
          color: "#fff",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontWeight: 700, fontSize: 14,
          fontFamily: "Inter"
        }}>
          {userInitial}
        </div>
      </div>
    </header>
  );
}
