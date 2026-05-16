import { useNavigate } from "react-router-dom";
import TopNavbar from "../components/TopNavbar";

export default function Home() {
  const nav = useNavigate();

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "var(--bg-deep)" }}>
      <TopNavbar />
      
      <main style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "60px 20px" }}>
        
        {/* Hero Section */}
        <div className="fade-up" style={{ textAlign: "center", maxWidth: 800, marginBottom: 48 }}>
          <h1 style={{
            fontSize: "clamp(3rem, 6vw, 5.5rem)", 
            fontWeight: 800, 
            lineHeight: 1.1,
            color: "var(--text-main)",
            letterSpacing: "-0.04em",
            marginBottom: 24
          }}>
            Master global <br />
            <span style={{ 
              position: "relative", 
              display: "inline-block"
            }}>
              compliance.
              <div style={{
                position: "absolute",
                bottom: 4,
                left: 0,
                right: 0,
                height: "12px",
                background: "var(--cyan)",
                zIndex: -1,
                opacity: 0.9
              }} />
            </span>
          </h1>
          
          <p style={{
            fontSize: "1.1rem",
            color: "var(--text-muted)",
            maxWidth: 600,
            margin: "0 auto 32px",
            lineHeight: 1.6
          }}>
            PolicyIQ scores your compliance, tracks global regulations, runs gap analyses, 
            and alerts your legal team to upcoming regulatory changes.
          </p>

          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16 }}>
            <button 
              onClick={() => nav("/login")}
              style={{
                background: "var(--cyan)",
                color: "#000",
                border: "none",
                padding: "14px 28px",
                borderRadius: 8,
                fontSize: 16,
                fontWeight: 700,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 8,
                transition: "transform 0.2s"
              }}
              onMouseOver={e => e.currentTarget.style.transform = "translateY(-2px)"}
              onMouseOut={e => e.currentTarget.style.transform = "translateY(0)"}
            >
              Open dashboard &rarr;
            </button>
            
            <button 
              style={{
                background: "transparent",
                color: "var(--text-main)",
                border: "1px solid var(--border)",
                padding: "14px 28px",
                borderRadius: 8,
                fontSize: 16,
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 8,
                transition: "background 0.2s"
              }}
              onMouseOver={e => e.currentTarget.style.background = "var(--bg-hover)"}
              onMouseOut={e => e.currentTarget.style.background = "transparent"}
            >
              <span style={{ fontSize: 12 }}>▶</span> Watch 90s demo
            </button>
          </div>

          <div style={{ 
            marginTop: 24, 
            display: "flex", 
            justifyContent: "center", 
            alignItems: "center", 
            gap: 16,
            fontSize: 12,
            color: "var(--text-dim)",
            fontFamily: "JetBrains Mono"
          }}>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <span style={{ color: "var(--cyan)" }}>★</span> 4.8 from 12k+ users
            </span>
            <span>·</span>
            <span>Free forever · $249/mo pro</span>
          </div>
        </div>

        {/* Stats Section */}
        <div className="fade-up fade-up-1" style={{ 
          display: "flex", 
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: 16,
          padding: "32px 0",
          width: "100%",
          maxWidth: 900,
          boxShadow: "0 10px 40px rgba(0,0,0,0.05)"
        }}>
          <div style={{ flex: 1, textAlign: "center", borderRight: "1px solid var(--border)" }}>
            <div style={{ fontSize: 36, fontWeight: 800, color: "var(--text-main)" }}>
              730<span style={{ color: "var(--cyan)" }}>+</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", letterSpacing: "1px", marginTop: 4 }}>
              POLICIES TRACKED
            </div>
          </div>
          <div style={{ flex: 1, textAlign: "center", borderRight: "1px solid var(--border)" }}>
            <div style={{ fontSize: 36, fontWeight: 800, color: "var(--text-main)" }}>
              20<span style={{ color: "var(--cyan)" }}>+</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", letterSpacing: "1px", marginTop: 4 }}>
              REGIONS COVERED
            </div>
          </div>
          <div style={{ flex: 1, textAlign: "center" }}>
            <div style={{ fontSize: 36, fontWeight: 800, color: "var(--text-main)" }}>
              $8B<span style={{ color: "var(--cyan)" }}>+</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", letterSpacing: "1px", marginTop: 4 }}>
              EXTRACTED FINES
            </div>
          </div>
        </div>

      </main>

      {/* Ticker / Marquee */}
      <div style={{ 
        padding: "16px 0", 
        borderTop: "1px solid var(--border)", 
        background: "var(--bg-base)",
        overflow: "hidden",
        whiteSpace: "nowrap"
      }}>
        <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", padding: "0 24px", letterSpacing: "0.1em", marginBottom: 12 }}>
          LIVE · RECENT UPDATES
        </div>
        <div style={{ display: "flex", gap: 16, padding: "0 24px" }}>
          {[
            { tag: "EU", title: "AI Act finalized", status: "Active" },
            { tag: "US", title: "CISA KEV updated", status: "Active" },
            { tag: "UK", title: "FCA Crypto regulations", status: "Review" },
            { tag: "IN", title: "DPDP Rules drafted", status: "Review" },
            { tag: "SG", title: "MAS AI Guidelines", status: "Active" }
          ].map((item, i) => (
            <div key={i} style={{ 
              display: "inline-flex", alignItems: "center", gap: 8, 
              background: "var(--bg-card)", border: "1px solid var(--border)", 
              padding: "8px 16px", borderRadius: 8, fontSize: 13 
            }}>
              <span style={{ 
                background: "rgba(183,255,0,0.15)", color: "#7ca800", 
                padding: "2px 6px", borderRadius: 4, fontSize: 11, fontWeight: 600
              }}>
                {item.tag}
              </span>
              <span style={{ color: "var(--text-main)" }}>{item.title}</span>
              <span style={{ color: "var(--text-muted)" }}>&rarr;</span>
              <span style={{ color: "var(--text-main)", fontWeight: 500 }}>{item.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
