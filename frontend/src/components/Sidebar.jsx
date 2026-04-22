import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, ScrollText, GitCompare,
  BarChart3, Globe2, Zap
} from "lucide-react";

const links = [
  { to: "/",          icon: LayoutDashboard, label: "Dashboard"  },
  { to: "/policies",  icon: ScrollText,      label: "Policies"   },
  { to: "/compare",   icon: GitCompare,      label: "Compare"    },
  { to: "/analytics", icon: BarChart3,       label: "Analytics"  },
];

export default function Sidebar() {
  return (
    <aside style={{
      width: 220,
      minHeight: "100vh",
      background: "var(--bg-base)",
      borderRight: "1px solid var(--border)",
      display: "flex",
      flexDirection: "column",
      padding: "0",
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{ padding: "24px 20px 20px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg, var(--cyan-dim), #0e7490)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Globe2 size={16} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 13, color: "var(--text-main)", lineHeight: 1.2 }}>
              PolicyIQ
            </div>
            <div style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
              v1.0 · 3 sectors
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ padding: "12px 10px", flex: 1 }}>
        <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", padding: "8px 10px 4px", letterSpacing: "0.1em" }}>
          NAVIGATION
        </div>
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === "/"} style={({ isActive }) => ({
            display: "flex", alignItems: "center", gap: 10,
            padding: "9px 12px", borderRadius: 8, marginBottom: 2,
            textDecoration: "none",
            background: isActive ? "rgba(34,211,238,0.08)" : "transparent",
            color: isActive ? "var(--cyan)" : "var(--text-muted)",
            borderLeft: isActive ? "2px solid var(--cyan)" : "2px solid transparent",
            fontSize: 13, fontWeight: 500,
            transition: "all 0.15s",
          })}>
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer badge */}
      <div style={{ padding: "16px 20px", borderTop: "1px solid var(--border)" }}>
        <div style={{
          background: "rgba(34,211,238,0.06)", border: "1px solid rgba(34,211,238,0.15)",
          borderRadius: 8, padding: "10px 12px",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
            <Zap size={11} color="var(--cyan)" />
            <span style={{ fontSize: 11, color: "var(--cyan)", fontFamily: "JetBrains Mono" }}>NLP ACTIVE</span>
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", lineHeight: 1.4 }}>
            spaCy NER · 30 policies indexed
          </div>
        </div>
      </div>
    </aside>
  );
}