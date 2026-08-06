import { NavLink } from "react-router-dom";
import { Moon, Sun, Globe2, Menu } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import PartnerLogos from "./PartnerBar";

export default function DashboardNavbar({ user, onMenuToggle }) {
  const { theme, toggleTheme } = useTheme();
  const userInitial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U";

  const links = [
    { to: "/",          label: "Home"      },
    { to: "/policies",  label: "Database"  },
    { to: "/compare",   label: "Compare"   },
    { to: "/analytics", label: "Analytics" },
  ];

  return (
    <header className="dashboard-navbar">

      {/* ── GRID COL 1 – LEFT: Hamburger (mobile) + PolicyIQ + partner logos ── */}
      <div style={{ display: "flex", alignItems: "center" }}>
        <button className="hamburger-btn" onClick={onMenuToggle} aria-label="Toggle menu">
          <Menu size={22} />
        </button>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 6,
            background: "var(--text-main)",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "var(--bg-base)",
          }}>
            <Globe2 size={16} />
          </div>
          <div style={{ fontWeight: 700, fontSize: 16, color: "var(--text-main)", letterSpacing: "-0.5px" }}>
            PolicyIQ
          </div>
        </div>
        <PartnerLogos />
      </div>

      {/* ── GRID COL 2 – CENTRE: Nav links (hidden on mobile via CSS) ── */}
      <nav className="nav-center">
        {links.map((l) => (
          <NavLink
            key={l.to} to={l.to} end={l.to === "/"}
            style={({ isActive }) => ({
              textDecoration: "none",
              color: isActive ? "var(--text-main)" : "var(--text-muted)",
              fontSize: 14, fontWeight: 500, transition: "color 0.2s",
            })}
          >
            {l.label}
          </NavLink>
        ))}
      </nav>

      {/* ── GRID COL 3 – RIGHT: Actions ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, justifyContent: "flex-end" }}>
        <button onClick={toggleTheme} style={{
          background: "transparent", border: "none", cursor: "pointer",
          display: "flex", alignItems: "center", color: "var(--text-muted)",
        }}>
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div style={{
          width: 32, height: 32, borderRadius: 6,
          background: "#5c6bc0", color: "#fff",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontWeight: 700, fontSize: 14, fontFamily: "Inter",
        }}>
          {userInitial}
        </div>
      </div>
    </header>
  );
}
