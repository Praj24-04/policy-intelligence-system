import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { fetchMLStatus } from "../services/api";
import { 
  LayoutDashboard, ScrollText, GitCompare, 
  BarChart3, Sparkles, Upload, FileText, 
  ChevronsLeft, UserCircle, LogOut 
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";

const categories = [
  {
    name: "WORK",
    links: [
      { to: "/", icon: LayoutDashboard, label: "Dashboard" },
      { to: "/policies", icon: ScrollText, label: "Database" },
    ]
  },
  {
    name: "PREP",
    links: [
      { to: "/compare", icon: GitCompare, label: "Compare" },
      { to: "/analytics", icon: BarChart3, label: "Analytics" },
    ]
  },
  {
    name: "DISCOVER",
    links: [
      { to: "/recommend", icon: Sparkles, label: "Recommender" },
      { to: "/generate", icon: FileText, label: "Generate Policy" },
      { to: "/upload", icon: Upload, label: "Upload PDF" },
    ]
  }
];

export default function Sidebar({ user, onLogout }) {
  const { theme } = useTheme();
  const [mlStatus, setMlStatus] = useState(null);

  useEffect(() => {
    fetchMLStatus().then(d => {
      if (d) setMlStatus(d);
    });
  }, []);

  const userInitial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U";

  // Premium translucent green highlight and border accent
  const activeBg = "rgba(163, 230, 53, 0.06)";
  const activeColor = theme === "light" ? "#4d7c0f" : "var(--cyan)";
  const activeBorder = "var(--cyan)";

  return (
    <aside style={{
      width: 240,
      minHeight: "100vh",
      background: "var(--bg-base)",
      borderRight: "1px solid var(--border)",
      display: "flex",
      flexDirection: "column",
      padding: "0",
      flexShrink: 0,
    }}>
      {/* Top Profile Header */}
      <div style={{ 
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "16px 20px", borderBottom: "1px solid var(--border)", height: "64px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 6,
            background: "#5c6bc0", 
            color: "#fff",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 700, fontSize: 13,
            fontFamily: "Inter"
          }}>
            {userInitial}
          </div>
          <div style={{ 
            fontFamily: "Inter", fontWeight: 700, fontSize: 13, 
            color: "var(--text-main)", textTransform: "uppercase",
            maxWidth: 110, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis"
          }}>
            {user?.full_name || "USER"}
          </div>
        </div>
        <button style={{ 
          background: "none", border: "none", color: "var(--text-muted)", 
          cursor: "pointer", display: "flex", alignItems: "center" 
        }}>
          <ChevronsLeft size={18} />
        </button>
      </div>

      {/* Nav Categories */}
      <nav style={{ padding: "20px 12px", flex: 1, overflowY: "auto" }}>
        {categories.map((cat, idx) => (
          <div key={idx} style={{ marginBottom: 24 }}>
            {/* Category Title */}
            <div style={{ 
              display: "flex", alignItems: "center", gap: 8, 
              paddingLeft: 12, marginBottom: 8 
            }}>
              <div style={{ width: 6, height: 6, background: "var(--cyan)" }} />
              <div style={{ 
                fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", 
                letterSpacing: "1px", fontWeight: 500
              }}>
                {cat.name}
              </div>
            </div>

            {/* Links */}
            {cat.links.map(({ to, icon: Icon, label }) => (
              <NavLink key={to} to={to} end={to === "/"} style={({ isActive }) => ({
                display: "flex", alignItems: "center", gap: 12,
                padding: isActive ? "10px 14px 10px 12px" : "10px 14px", 
                borderRadius: 8, marginBottom: 2,
                textDecoration: "none",
                background: isActive ? activeBg : "transparent",
                color: isActive ? activeColor : "var(--text-muted)",
                borderLeft: isActive ? `3px solid ${activeBorder}` : "3px solid transparent",
                fontSize: 14, fontWeight: isActive ? 600 : 500,
                transition: "all 0.15s",
              })}>
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </div>
        ))}

        {/* ACCOUNT Category */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ 
            display: "flex", alignItems: "center", gap: 8, 
            paddingLeft: 12, marginBottom: 8 
          }}>
            <div style={{ width: 6, height: 6, background: "var(--cyan)" }} />
            <div style={{ 
              fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", 
              letterSpacing: "1px", fontWeight: 500
            }}>
              ACCOUNT
            </div>
          </div>
          
          <div style={{
            display: "flex", alignItems: "center", gap: 12,
            padding: "10px 14px", borderRadius: 8, marginBottom: 2,
            color: "var(--text-muted)", fontSize: 14, fontWeight: 500,
            cursor: "pointer"
          }}>
            <UserCircle size={18} />
            My Profile
          </div>

          <div 
            onClick={onLogout}
            style={{
              display: "flex", alignItems: "center", gap: 12,
              padding: "10px 14px", borderRadius: 8, marginBottom: 2,
              color: "var(--text-muted)", fontSize: 14, fontWeight: 500,
              cursor: "pointer"
            }}
          >
            <LogOut size={18} />
            Logout
          </div>
        </div>
      </nav>
      {/* ML Status Indicator */}
      {mlStatus && (
        <div style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          gap: 10,
          background: "rgba(255,255,255,0.01)"
        }}>
          <div style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            backgroundColor: (() => {
              if (!mlStatus.last_retrain_timestamp || mlStatus.last_retrain_timestamp === "Never") return "#94a3b8";
              const lastTime = new Date(mlStatus.last_retrain_timestamp);
              const diffHours = Math.abs(new Date() - lastTime) / (1000 * 60 * 60);
              if (diffHours < 2) return "#10b981"; // Green
              if (diffHours < 24) return "#f59e0b"; // Yellow
              return "#94a3b8";
            })(),
            boxShadow: "0 0 8px currentColor"
          }} />
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600 }}>
              {mlStatus.total_indexed_in_chroma ?? mlStatus.total_policies ?? 0} POLICIES INDEXED
            </span>
            <span style={{ fontSize: 9, fontFamily: "JetBrains Mono", color: "var(--text-dim)", textTransform: "uppercase" }}>
              Active search index
            </span>
          </div>
        </div>
      )}
    </aside>
  );
}