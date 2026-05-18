import { NavLink } from "react-router-dom";
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

  const userInitial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U";

  // Light mode exact matches from InternHack
  const activeBg = theme === "light" ? "#1a1a1a" : "var(--cyan)";
  const activeColor = theme === "light" ? "#fff" : "#000";
  const activeBorder = theme === "light" ? "var(--cyan)" : "#000";

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
                padding: "10px 14px", borderRadius: 8, marginBottom: 2,
                textDecoration: "none",
                background: isActive ? activeBg : "transparent",
                color: isActive ? activeColor : "var(--text-muted)",
                borderLeft: isActive ? `4px solid ${activeBorder}` : "4px solid transparent",
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
    </aside>
  );
}