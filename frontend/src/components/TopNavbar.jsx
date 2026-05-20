import { Link, useNavigate } from "react-router-dom";
import { Globe2, Moon, Sun } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";

export default function TopNavbar() {
  const { theme, toggleTheme } = useTheme();
  const nav = useNavigate();
  const [activePath, setActivePath] = useState("#hero");

  useEffect(() => {
    const handleScroll = () => {
      const sections = ["hero", "features", "shipped", "faq"];
      let current = "#hero";
      for (let s of sections) {
        const el = document.getElementById(s);
        if (el && window.scrollY >= (el.offsetTop - 300)) {
          current = "#" + s;
        }
      }
      setActivePath(current);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const NavItem = ({ href, label }) => {
    const isActive = activePath === href;
    const [isHovered, setIsHovered] = useState(false);
    return (
      <a 
        href={href}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        style={{
          textDecoration: "none",
          color: isHovered || isActive ? "var(--text-main)" : "var(--text-muted)",
          fontSize: 14,
          fontWeight: 600,
          transition: "color 0.2s",
          position: "relative",
          paddingBottom: 4
        }}
      >
        {label}
        {isActive && (
          <motion.div 
            layoutId="nav-underline"
            style={{
              position: "absolute",
              bottom: -4,
              left: 0,
              right: 0,
              height: 2,
              background: "var(--cyan)",
              borderRadius: 2
            }}
          />
        )}
      </a>
    );
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
        <motion.div 
          whileHover={{ rotate: 180 }}
          transition={{ duration: 0.3 }}
          style={{
            width: 32, height: 32, borderRadius: 8,
            background: "var(--cyan)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
        >
          <Globe2 size={16} color="#000" />
        </motion.div>
        <div style={{ fontWeight: 800, fontSize: 18, color: "var(--text-main)", letterSpacing: "-0.5px" }}>
          PolicyIQ
        </div>
      </div>

      {/* Nav Links */}
      <nav style={{ display: "flex", gap: 32 }}>
        <NavItem href="#hero" label="Home" />
        <NavItem href="#features" label="Features" />
        <NavItem href="#shipped" label="Live Policies" />
        <NavItem href="#faq" label="FAQ" />
      </nav>

      {/* Actions */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <motion.button 
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleTheme} 
          style={{
            background: "transparent", border: "none", cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "var(--text-muted)"
          }}
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </motion.button>
        <motion.button 
          whileHover={{ backgroundColor: "var(--text-main)", color: "var(--bg-base)" }}
          whileTap={{ scale: 0.95 }}
          onClick={() => nav("/login")}
          style={{
            background: "var(--bg-hover)",
            border: "1px solid var(--border)",
            color: "var(--text-main)",
            padding: "8px 16px",
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
            transition: "background 0.2s, color 0.2s"
          }}
        >
          Sign In
        </motion.button>
      </div>
    </header>
  );
}
